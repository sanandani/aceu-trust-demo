from fastapi.testclient import TestClient

from main import app
from scoring import calculate_aceu

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_profiles_are_synthetic():
    response = client.get("/profiles")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all("synthetic" in item["name"] for item in response.json())


def test_aceu_has_four_explained_dimensions():
    response = client.get("/profiles/builder/aceu")
    assert response.status_code == 200
    data = response.json()
    assert set(data["dimensions"]) == {
        "authenticity", "credibility", "empathy", "uniqueness"
    }
    assert all(
        dimension["explanation"]
        for dimension in data["dimensions"].values()
    )
    assert "unvalidated" in data["limitation"]


def test_unknown_profile_returns_404():
    assert client.get("/profiles/unknown/aceu").status_code == 404


def test_missing_evidence_is_not_scored_as_zero():
    dimensions = calculate_aceu({})
    assert all(
        dimension["illustrative_index"] is None
        for dimension in dimensions.values()
    )


def test_supported_claims_change_example_index():
    before = calculate_aceu({
        "claims": [{"text": "Builds tools", "artifact": ""}]
    })
    after = calculate_aceu({
        "claims": [{"text": "Builds tools", "artifact": "demo-repo"}]
    })
    assert before["authenticity"]["illustrative_index"] == 0.0
    assert after["authenticity"]["illustrative_index"] == 1.0


def test_root_redirects_to_docs():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"
