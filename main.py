from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from scoring import calculate_aceu

app = FastAPI(
    title="ACE-U Trust Demo",
    description="Synthetic, educational demonstration; not a real-person assessment.",
)

PROFILES = {
    "expert": {
        "name": "Morgan (synthetic)",
        "claims": [
            {"text": "Builds identity systems", "artifact": "identity-api-demo"},
            {"text": "Writes about system design", "artifact": "architecture-note"},
        ],
        "projects": ["identity-api-demo", "architecture-note", "service-design-demo"],
        "credential_examples": ["fictional credential"],
        "peer_support_examples": [],
        "cross_domain_projects": [],
    },
    "builder": {
        "name": "Avery (synthetic)",
        "claims": [
            {"text": "Builds developer tools", "artifact": "developer-tool-demo"},
            {"text": "Mentors peers", "artifact": "fictional-mentoring-note"},
        ],
        "projects": ["developer-tool-demo", "community-guide"],
        "credential_examples": [],
        "peer_support_examples": [
            "Detailed review of a peer's project",
            "Mentoring note shared with permission in this fictional scenario",
            "Collaborative troubleshooting example",
        ],
        "cross_domain_projects": [
            {"name": "community-guide", "domains": ["software", "education"]},
            {"name": "developer-tool-demo", "domains": ["software", "community"]},
        ],
    },
    "explorer": {
        "name": "Riley (synthetic)",
        "claims": [
            {"text": "Explores identity and accessibility", "artifact": "prototype"}
        ],
        "projects": ["prototype"],
        "credential_examples": [],
        "peer_support_examples": ["Collaborative prototype review"],
        "cross_domain_projects": [
            {"name": "prototype", "domains": ["identity", "accessibility"]},
            {"name": "research-demo", "domains": ["design", "software"]},
            {"name": "workshop", "domains": ["education", "identity"]},
        ],
    },
}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/profiles")
def list_profiles():
    return [
        {"id": profile_id, "name": profile["name"]}
        for profile_id, profile in PROFILES.items()
    ]


@app.get("/profiles/{profile_id}/aceu")
def aceu(profile_id: str):
    profile = PROFILES.get(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile_id": profile_id,
        "name": profile["name"],
        "dimensions": calculate_aceu(profile),
        "limitation": (
            "Synthetic educational example only. Indices are unvalidated "
            "and must not be used to assess real people or make hiring decisions."
        ),
    }
