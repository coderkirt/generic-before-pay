from app.ocr.handwriting import HANDWRITING_NOTICE, group_rects

from tests.conftest import FakeProvider, make_client, post_image


def test_group_rects_same_line_sorted_left_to_right():
    # (x1, y1, x2, y2) — two letters on one line, one on the next
    groups = group_rects([(80, 10, 90, 30), (10, 12, 20, 32), (12, 80, 22, 100)], image_h=300)
    assert [r[0] for r in groups[0]] == [10, 80]
    assert groups[1][0][1] == 80


def test_ocr_handwriting_flag_sets_notice_and_keeps_fallback():
    r = post_image(make_client(FakeProvider()), handwriting="true", preprocess="false")
    assert r.status_code == 200
    body = r.json()
    assert body["notice"] == HANDWRITING_NOTICE
    assert "DOLO 650" in body["candidates"]
    assert body["disclaimer"]
    assert body["preprocessed"] is False
