from app.disclaimer import DISCLAIMER
from tests.conftest import make_client, FIX

PATIENT = {"age_years": 34, "gender": "female"}


def test_candidates_exact_ambiguous_fuzzy_none():
    c = make_client()
    res = c.post("/v1/prescription/candidates",
                 json={"items": ["testoprazole 40", "Testoprazole", "Testoprazol 40", "gibberishzzz"]}).json()
    exact, ambiguous, fuzzy, none = res["results"]
    assert exact["tier"] == "exact" and exact["matches"][0]["brand_id"] == "b_alpha_40" and exact["verify_notice"] is None
    assert ambiguous["tier"] == "uncertain" and ambiguous["reason"] == "strength_needed" and len(ambiguous["matches"]) == 2
    assert fuzzy["tier"] in ("likely", "uncertain") and fuzzy["verify_notice"]
    assert none["tier"] == "none" and none["matches"] == []
    assert res["disclaimer"] == DISCLAIMER


def test_candidates_never_contain_prices():
    r = make_client().post("/v1/prescription/candidates", json={"items": ["fakecillin"]}).json()
    assert set(r["results"][0]["matches"][0]) == {"brand_id", "brand_name", "composition_id", "score"}


def test_summary_requires_confirmation():
    r = make_client().post("/v1/prescription/summary", json={"patient": PATIENT, "confirmed_by_user": False,
                                                              "items": [{"brand_id": "b_alpha_40"}]})
    assert r.status_code == 400 and r.json()["error"]["code"] == "CONFIRMATION_REQUIRED"


def test_summary_totals_only_count_compared_lines():
    items = [{"brand_id": i} for i in ("b_alpha_40", "b_beta", "b_mm", "does_not_exist")]
    r = make_client().post("/v1/prescription/summary", json={"patient": PATIENT, "confirmed_by_user": True, "items": items})
    body = r.json()
    status = {l["brand_id"]: l["status"] for l in body["lines"]}
    assert status == {"b_alpha_40": "compared", "b_beta": "no_equivalent_in_data",
                      "b_mm": "unit_mismatch", "does_not_exist": "not_in_data"}
    t = body["totals"]
    # brand 150 for 15 tablets; cheapest listed equivalent 2.0/unit * 15 = 30
    assert (t["brand_total_inr"], t["listed_equivalent_total_inr"], t["difference_inr"]) == (150.0, 30.0, 120.0)
    assert t["compared_lines"] == 1 and t["not_compared_lines"] == 3
    assert body["disclaimer"] == DISCLAIMER


def test_summary_validation():
    c = make_client()
    r = c.post("/v1/prescription/summary", json={"patient": {"age_years": -1, "gender": "x"}, "confirmed_by_user": True,
                                                  "items": [{"brand_id": "b_alpha_40"}]})
    assert r.status_code == 422


def test_nearest_kendras_sorted_with_distance():
    r = make_client().get("/v1/kendras/nearest", params={"lat": 26.85, "lng": 80.95}).json()
    names = [k["kendra_code"] for k in r["kendras"]]
    assert names == ["K1", "K2", "K3"]
    d = [k["distance_km"] for k in r["kendras"]]
    assert d == sorted(d) and d[0] == 0.0 and "google.com/maps" in r["kendras"][0]["maps_url"]


def test_nearest_limit_and_bad_coords():
    c = make_client()
    assert len(c.get("/v1/kendras/nearest", params={"lat": 26.85, "lng": 80.95, "limit": 1}).json()["kendras"]) == 1
    assert c.get("/v1/kendras/nearest", params={"lat": 999, "lng": 0}).status_code == 422


def test_missing_data_is_honest(tmp_path):
    c = make_client(data_dir=str(tmp_path))
    r = c.get("/v1/kendras/nearest", params={"lat": 1, "lng": 1})
    assert r.status_code == 503 and r.json()["error"]["code"] == "DATA_NOT_LOADED"
    ready = c.get("/readyz").json()
    assert ready["status"] == "degraded" and ready["typing_path"] == "available"


def test_health_and_ready_with_data():
    c = make_client()
    assert c.get("/healthz").json() == {"status": "ok"}
    # fixtures include all three datasets -> ready (mock OCR)
    assert c.get("/readyz").json()["status"] == "ready"
