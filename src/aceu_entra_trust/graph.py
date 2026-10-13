"""Read-only Microsoft Graph v1.0 export helpers."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

GRAPH = "https://graph.microsoft.com/v1.0"
COLLECTIONS = ("applications", "servicePrincipals", "federatedIdentityCredentials", "owners", "appRoleAssignments")


def get_token() -> str:
    token = os.getenv("GRAPH_TOKEN")
    if token:
        return token
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Set GRAPH_TOKEN or install aceu-entra-trust[graph] for azure-identity.") from exc
    return DefaultAzureCredential().get_token("https://graph.microsoft.com/.default").token


def _get(path: str, token: str) -> dict:
    request = Request(f"{GRAPH}/{path}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def _all(path: str, token: str) -> list[dict]:
    items = []
    while path:
        payload = _get(path, token) if path.startswith("https://") else _get(path, token)
        items.extend(payload.get("value", []))
        path = payload.get("@odata.nextLink", "")
        if path.startswith(GRAPH + "/"):
            path = path[len(GRAPH) + 1:]
    return items


def export_graph(token: str | None = None) -> dict:
    """Read required Graph resources. Requires application read permissions."""
    token = token or get_token()
    apps = _all("applications?$select=id,appId,displayName,signInAudience,passwordCredentials,keyCredentials", token)
    sps = _all("servicePrincipals?$select=id,appId,displayName", token)
    fics: dict[str, list[dict]] = {}
    owners: dict[str, list[dict]] = {}
    assignments: dict[str, list[dict]] = {}
    for app in apps:
        app_id = quote(app["id"], safe="")
        for key, path in (("federatedIdentityCredentials", f"applications/{app_id}/federatedIdentityCredentials"), ("owners", f"applications/{app_id}/owners")):
            try:
                found = _all(path, token)
            except HTTPError as exc:
                if exc.code not in (403, 404):
                    raise
                found = []
            (fics if key == "federatedIdentityCredentials" else owners)[app["id"]] = found
        sp = next((item for item in sps if item.get("appId") == app.get("appId")), None)
        if sp:
            try:
                assignments[sp["id"]] = _all(f"servicePrincipals/{quote(sp['id'], safe='')}/appRoleAssignments", token)
            except HTTPError as exc:
                if exc.code not in (403, 404):
                    raise
                assignments[sp["id"]] = []
    return {"applications": apps, "servicePrincipals": sps, "federatedIdentityCredentials": fics, "owners": owners, "appRoleAssignments": assignments}
