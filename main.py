from fastapi import FastAPI, HTTPException

app = FastAPI(title="ACE-U Trust Demo")

# Fictional examples, not assessments of real people.
PROFILES = {
    "expert": {
        "name": "Morgan (synthetic)",
        "authenticity": [0.8, "Work artifacts align with stated experience."],
        "credibility": [0.9, "Example includes documented domain work."],
        "empathy": [0.4, "Limited collaboration evidence is provided; this does not imply low empathy."],
        "uniqueness": [0.3, "Deep specialization, with few cross-domain examples."],
    },
    "builder": {
        "name": "Avery (synthetic)",
        "authenticity": [0.9, "Projects align with stated interests."],
        "credibility": [0.6, "Example includes documented projects."],
        "empathy": [0.9, "Example includes mentoring and substantive peer feedback."],
        "uniqueness": [0.7, "Combines technical and community-building work."],
    },
    "explorer": {
        "name": "Riley (synthetic)",
        "authenticity": [0.7, "Projects support the stated interests."],
        "credibility": [0.5, "Promising work, but a short documented track record."],
        "empathy": [0.7, "Example includes collaborative work."],
        "uniqueness": [0.9, "Combines experience across relevant domains."],
    },
}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/profiles")
def list_profiles():
    return [{"id": key, "name": value["name"]} for key, value in PROFILES.items()]

@app.get("/profiles/{profile_id}/aceu")
def aceu(profile_id: str):
    profile = PROFILES.get(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile_id": profile_id,
        "name": profile["name"],
        "dimensions": {
            key: {"illustrative_value": profile[key][0], "explanation": profile[key][1]}
            for key in ("authenticity", "credibility", "empathy", "uniqueness")
        },
        "limitation": "Synthetic illustration only; these are not validated trust scores.",
    }
