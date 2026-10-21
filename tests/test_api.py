"""
tests/test_api.py

Automated test suite for Generic Before Pay API.
Tests:
- Search accuracy, fuzzy matching, and misspelling tolerance
- Partial names and missing strengths
- Top-3 candidate ranking
- Drug detail retrieval and 404 not-found handling
- Prescription compare basket calculations
- Mandatory disclaimer presence across all endpoints
- Strict absence of forbidden advice/dosage fields
- Offline sync endpoints (version and bundle)
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.dal import STANDARD_DISCLAIMER

FORBIDDEN_KEYS = {
    "dosage",
    "dosage_instructions",
    "frequency",
    "duration",
    "course",
    "substitution_advice",
    "recommendation",
    "advice"
}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _assert_no_forbidden_fields(data):
    """Recursively verify no forbidden medical advice fields are present."""
    if isinstance(data, dict):
        for k, v in data.items():
            assert k.lower() not in FORBIDDEN_KEYS, f"Forbidden field '{k}' found in response!"
            _assert_no_forbidden_fields(v)
    elif isinstance(data, list):
        for item in data:
            _assert_no_forbidden_fields(item)


def test_search_exact_match(client):
    response = client.get("/api/v1/search?q=Calpol 500")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER
    matches = json_data["data"]["matches"]
    assert len(matches) >= 1
    assert matches[0]["brand_name"] == "Calpol 500"
    assert matches[0]["confidence_score"] >= 0.90
    _assert_no_forbidden_fields(json_data)


def test_search_fuzzy_misspelling(client):
    # Typo: 'clpol' instead of 'calpol'
    response = client.get("/api/v1/search?q=clpol")
    assert response.status_code == 200
    json_data = response.json()
    matches = json_data["data"]["matches"]
    assert len(matches) > 0
    assert matches[0]["brand_name"] == "Calpol 500"
    assert matches[0]["confidence_score"] >= 0.70
    _assert_no_forbidden_fields(json_data)


def test_search_missing_strength_returns_candidates(client):
    # Query without strength: 'glycomet'
    response = client.get("/api/v1/search?q=glycomet")
    assert response.status_code == 200
    json_data = response.json()
    matches = json_data["data"]["matches"]
    # Should return candidates with distinct strengths (e.g. 500 mg, 1000 mg)
    assert len(matches) >= 2
    strengths = {m["strength"] for m in matches}
    assert "500 mg" in strengths
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER
    _assert_no_forbidden_fields(json_data)


def test_search_top_3_limit(client):
    response = client.get("/api/v1/search?q=tab&limit=3")
    assert response.status_code == 200
    matches = response.json()["data"]["matches"]
    assert len(matches) <= 3


def test_search_not_found_returns_empty_matches(client):
    response = client.get("/api/v1/search?q=xyznonexistentdrug999")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_matches"] == 0
    assert json_data["data"]["matches"] == []
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER


def test_drug_detail_success(client):
    response = client.get("/api/v1/drugs/paracetamol-500mg-tab")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["id"] == "paracetamol-500mg-tab"
    assert data["brand_name"] == "Calpol 500"
    assert data["molecule"] == "Paracetamol"
    assert data["strength"] == "500 mg"
    assert data["branded_price"] == 32.50
    assert data["generic_price"] == 5.00
    assert data["savings_amount"] == 27.50
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER
    _assert_no_forbidden_fields(json_data)


def test_drug_detail_not_found(client):
    response = client.get("/api/v1/drugs/unknown-drug-id-999")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_compare_prescriptions(client):
    payload = {
        "items": [
            {"id": "paracetamol-500mg-tab", "quantity": 2},
            {"id": "metformin-500mg-tab", "quantity": 1}
        ]
    }
    response = client.post("/api/v1/compare", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    summary = json_data["data"]["summary"]
    breakdown = json_data["data"]["breakdown"]

    # 2 * 32.50 + 1 * 28.00 = 65.00 + 28.00 = 93.00
    assert summary["total_branded_cost"] == 93.00
    # 2 * 5.00 + 1 * 5.00 = 15.00
    assert summary["total_generic_cost"] == 15.00
    assert summary["total_savings"] == 78.00
    assert summary["overall_savings_percentage"] == 83.9
    assert len(breakdown) == 2
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER
    _assert_no_forbidden_fields(json_data)


def test_compare_validation_error(client):
    # Empty items list violates min_length=1
    response = client.post("/api/v1/compare", json={"items": []})
    assert response.status_code == 422
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "VALIDATION_ERROR"


def test_offline_data_version(client):
    response = client.get("/api/v1/data/version")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_records"] >= 20
    assert "dataset_hash" in json_data["data"]


def test_offline_data_bundle_and_etag(client):
    response = client.get("/api/v1/data/bundle")
    assert response.status_code == 200
    etag = response.headers.get("etag")
    assert etag is not None
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["drugs"]) >= 80
    assert json_data["disclaimer"] == STANDARD_DISCLAIMER
    _assert_no_forbidden_fields(json_data)

    # Test 304 Not Modified when ETag matches
    cached_response = client.get("/api/v1/data/bundle", headers={"If-None-Match": etag})
    assert cached_response.status_code == 304


def test_search_paracetmol_and_crocin_misspellings(client):
    # Case 1: 'Paracetmol' misspelling
    r1 = client.get("/api/v1/search?q=Paracetmol")
    assert r1.status_code == 200
    matches1 = r1.json()["data"]["matches"]
    assert len(matches1) >= 1
    names1 = [m["brand_name"] for m in matches1]
    assert "Calpol 500" in names1 or "Dolo 650" in names1
    assert matches1[0]["confidence_score"] >= 0.80

    # Case 2: 'Crocin 500' alias
    r2 = client.get("/api/v1/search?q=Crocin 500")
    assert r2.status_code == 200
    matches2 = r2.json()["data"]["matches"]
    assert len(matches2) >= 1
    assert matches2[0]["confidence_score"] >= 0.90


def test_dual_route_prefix(client):
    # Test unversioned /api/ path
    r_unversioned = client.get("/api/search?q=Dolo 650")
    assert r_unversioned.status_code == 200
    assert r_unversioned.json()["data"]["matches"][0]["brand_name"] == "Dolo 650"

    r_bundle = client.get("/api/data/version")
    assert r_bundle.status_code == 200
    assert r_bundle.json()["data"]["total_records"] >= 80


def test_disclaimer_present_in_error_responses(client):
    r_404 = client.get("/api/v1/drugs/non-existent-drug-1234")
    assert r_404.status_code == 404
    assert r_404.json()["disclaimer"] == STANDARD_DISCLAIMER

    r_422 = client.post("/api/v1/compare", json={"items": []})
    assert r_422.status_code == 422
    assert r_422.json()["disclaimer"] == STANDARD_DISCLAIMER


def test_dataset_size_at_least_80_records(client):
    response = client.get("/api/v1/data/version")
    assert response.status_code == 200
    total = response.json()["data"]["total_records"]
    assert total >= 80, f"Dataset has only {total} records, expected at least 80!"


def test_search_by_molecule_paracetamol(client):
    """Search by molecule 'Paracetamol' must return Crocin/Dolo/Calpol."""
    response = client.get("/api/v1/search?q=Paracetamol")
    assert response.status_code == 200
    data = response.json()["data"]
    matches = data["matches"]
    assert len(matches) >= 2
    matched_names = {m["brand_name"] for m in matches}
    # Must contain common Paracetamol brands
    assert any(name in matched_names for name in ["Calpol 500", "Dolo 650", "Crocin Advance"])
    # All returned items must have Paracetamol as active molecule
    for m in matches:
        assert "Paracetamol" in m["molecule"]
        assert m["confidence_score"] >= 0.85


def test_search_by_brand_crocin(client):
    """Search by brand 'Crocin' must return Crocin."""
    response = client.get("/api/v1/search?q=Crocin")
    assert response.status_code == 200
    matches = response.json()["data"]["matches"]
    assert len(matches) >= 1
    matched_names = [m["brand_name"] for m in matches]
    assert "Crocin Advance" in matched_names or "Calpol 500" in matched_names
    assert matches[0]["confidence_score"] == 1.0


def test_search_by_molecule_and_strength(client):
    """Search by molecule + strength combination."""
    r1 = client.get("/api/v1/search?q=Metformin 500")
    assert r1.status_code == 200
    m1 = r1.json()["data"]["matches"]
    assert len(m1) >= 1
    assert m1[0]["brand_name"] == "Glycomet 500"
    assert m1[0]["strength"] == "500 mg"
    assert m1[0]["confidence_score"] >= 0.95

    r2 = client.get("/api/v1/search?q=Atorvastatin 20")
    assert r2.status_code == 200
    m2 = r2.json()["data"]["matches"]
    assert len(m2) >= 1
    assert m2[0]["brand_name"] == "Atorva 20"
    assert m2[0]["strength"] == "20 mg"
    assert m2[0]["confidence_score"] >= 0.95


