"""Pure scoring rules for Microsoft Entra application identities."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _values(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, []) or []
    if isinstance(value, dict):
        return value.get("value", []) or []
    return value if isinstance(value, list) else []


def score_identities(export: dict[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
    """Score each application record in a Graph v1.0 export or a direct record.

    Expected collections: applications, servicePrincipals, owners,
    appRoleAssignments, and federatedIdentityCredentials. A single application
    dictionary is accepted for offline use.
    """
    now = now or datetime.now(timezone.utc)
    applications = _values(export, "applications")
    if not applications and ("id" in export or "appId" in export):
        applications = [export]
    sps = _values(export, "servicePrincipals")
    sp_by_app = {sp.get("appId"): sp for sp in sps}
    owners_by_id = export.get("owners", {}) or {}
    assignments_by_id = export.get("appRoleAssignments", {}) or {}
    federated_by_id = export.get("federatedIdentityCredentials", {}) or {}
    if not isinstance(owners_by_id, dict):
        owners_by_id = {}
    if not isinstance(assignments_by_id, dict):
        assignments_by_id = {}
    if not isinstance(federated_by_id, dict):
        federated_by_id = {}
    names: dict[str, int] = {}
    for app in applications:
        name = (app.get("displayName") or "").strip().casefold()
        if name:
            names[name] = names.get(name, 0) + 1

    results = []
    for app in applications:
        app_id = app.get("id") or app.get("appId") or "unknown"
        sp = sp_by_app.get(app.get("appId"), {})
        credentials = list(app.get("passwordCredentials", []) or []) + list(app.get("keyCredentials", []) or [])
        federated = federated_by_id.get(app_id, app.get("federatedIdentityCredentials", [])) or []
        if isinstance(federated, dict):
            federated = federated.get("value", [])
        secrets = app.get("passwordCredentials", []) or []
        certs = app.get("keyCredentials", []) or []
        credential_types = {str(c.get("type", "")).casefold() for c in credentials}
        credential_types.update(str(c.get("usage", "")).casefold() for c in certs)
        has_secret = bool(secrets) or "password" in credential_types or "secret" in credential_types
        has_cert = bool(certs) or "certificate" in credential_types
        auth_score = 100 if federated or app.get("managedIdentity", False) else (40 if has_secret else (75 if has_cert else 100))
        findings: list[dict[str, Any]] = []

        def add(rule_id: str, pillar: str, severity: str, message: str, penalty: int = 0) -> None:
            findings.append({"id": rule_id, "pillar": pillar, "severity": severity, "message": message, "penalty": penalty})

        if has_secret:
            add("ACEU001", "Authenticity", "high", "Client secret credential is present.")
        elif federated or app.get("managedIdentity", False):
            add("ACEU001", "Authenticity", "info", "Federated or managed identity authentication is configured.")
        elif has_cert:
            add("ACEU001", "Authenticity", "low", "Certificate-only authentication is configured.")
        for secret in secrets:
            created = _date(secret.get("startDateTime"))
            if created and (now - created).days > 180:
                auth_score -= 15
                add("ACEU002", "Authenticity", "medium", "Client secret is more than 180 days old.", 15)
        for cert in certs:
            created = _date(cert.get("startDateTime"))
            if created and (now - created).days > 365:
                auth_score -= 10
                add("ACEU003", "Authenticity", "medium", "Certificate is more than 365 days old.", 10)

        uniqueness = 100
        name = (app.get("displayName") or "").strip().casefold()
        if name and names.get(name, 0) > 1:
            uniqueness -= 40
            add("ACEU010", "Uniqueness", "high", "Duplicate application displayName.", 40)
        audience = app.get("signInAudience") or ""
        if audience in {"AzureADMultipleOrgs", "AzureADandPersonalMicrosoftAccount", "PersonalMicrosoftAccount"}:
            uniqueness -= 30
            add("ACEU011", "Uniqueness", "medium", "Application accepts a multi-tenant or personal account audience.", 30)
        owners = owners_by_id.get(app_id, app.get("owners", [])) or []
        if isinstance(owners, dict):
            owners = owners.get("value", [])
        if not owners:
            uniqueness -= 20
            add("ACEU012", "Uniqueness", "medium", "Application has no listed owner.", 20)

        credibility = 100
        expired = [c for c in credentials if (end := _date(c.get("endDateTime"))) is not None and end < now]
        if expired:
            credibility -= 25
            add("ACEU020", "Credibility", "high", f"{len(expired)} expired credential(s) are present.", 25)
        assignments = assignments_by_id.get(sp.get("id", app_id), app.get("appRoleAssignments", [])) or []
        if isinstance(assignments, dict):
            assignments = assignments.get("value", [])
        excess = max(0, len(assignments) - 5)
        if excess:
            penalty = min(excess * 10, 50)
            credibility -= penalty
            add("ACEU021", "Credibility", "medium", f"Application has {len(assignments)} app role assignments; more than five are present.", penalty)

        scores = {"Authenticity": max(0, min(100, auth_score)), "Uniqueness": max(0, min(100, uniqueness)), "Credibility": max(0, min(100, credibility))}
        total = round(0.4 * scores["Authenticity"] + 0.2 * scores["Uniqueness"] + 0.4 * scores["Credibility"], 2)
        band = "trusted" if total >= 80 else ("review" if total >= 55 else "risky")
        results.append({"id": app_id, "appId": app.get("appId"), "displayName": app.get("displayName", ""), "scores": scores, "total": total, "band": band, "findings": findings})
    return results
