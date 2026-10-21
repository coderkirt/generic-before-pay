import logging

from app.ocr.service import sanitize_candidates

from tests.conftest import FakeProvider, make_client, post_image


def test_sanitize_drops_advice_dosage_and_names_not_in_text():
    text = "DOLO 650 Tablets\nPANTOCID 40"
    cands = [
        "DOLO 650",
        "Take twice daily",
        "Paracetamol 500mg twice a day after food",
        "safe to replace with generic",
        "PANTOCID 40",
        "InventedBrand",
    ]
    assert sanitize_candidates(text, cands) == ["DOLO 650", "PANTOCID 40"]


def test_ocr_logs_do_not_include_extracted_text(caplog):
    with caplog.at_level(logging.INFO, logger="janrx"):
        post_image(make_client(FakeProvider(text="SECRETBRAND 99", candidates=["SECRETBRAND 99"])))
    blob = caplog.text.lower()
    assert "secretbrand" not in blob
    assert "dolo" not in blob


def test_summary_logs_do_not_include_age_or_gender(caplog):
    c = make_client()
    with caplog.at_level(logging.INFO, logger="janrx"):
        c.post("/v1/prescription/summary", json={
            "patient": {"age_years": 34, "gender": "female"},
            "confirmed_by_user": True,
            "items": [{"brand_id": "testoprazole_40_tab", "quantity_packs": 1}],
        })
    blob = caplog.text.lower()
    assert "female" not in blob
    assert "age_years" not in blob
    assert "gender" not in blob
