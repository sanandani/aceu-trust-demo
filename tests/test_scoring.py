from datetime import datetime, timezone

from aceu_entra_trust.scoring import score_identities


NOW = datetime(2026, 10, 1, tzinfo=timezone.utc)


def test_federated_identity_is_trusted():
    result = score_identities({"id": "one", "displayName": "deploy", "federatedIdentityCredentials": [{}], "owners": [{}]}, NOW)[0]
    assert result["total"] == 100
    assert result["band"] == "trusted"


def test_old_secret_twelve_roles_no_owner_is_risky():
    export = {
        "applications": [{"id": "one", "appId": "app", "displayName": "worker", "passwordCredentials": [{"startDateTime": "2025-01-01T00:00:00Z", "endDateTime": "2025-01-02T00:00:00Z"}]}],
        "appRoleAssignments": {"one": [{} for _ in range(12)]},
    }
    result = score_identities(export, NOW)[0]
    assert result["scores"] == {"Authenticity": 25, "Uniqueness": 80, "Credibility": 25}
    assert result["total"] == 36
    assert result["band"] == "risky"
    assert {finding["id"] for finding in result["findings"]} >= {"ACEU001", "ACEU002", "ACEU012", "ACEU020", "ACEU021"}


def test_duplicate_display_names_reduce_uniqueness():
    export = {"applications": [
        {"id": "one", "displayName": "Worker", "federatedIdentityCredentials": [{}], "owners": [{}]},
        {"id": "two", "displayName": " worker ", "federatedIdentityCredentials": [{}], "owners": [{}]},
    ]}
    results = score_identities(export, NOW)
    assert [result["scores"]["Uniqueness"] for result in results] == [60, 60]
    assert all("ACEU010" in {f["id"] for f in result["findings"]} for result in results)
