import re

from fastapi import APIRouter, Request
from rapidfuzz import fuzz

from ..errors import ApiError
from ..schemas import (CandidateResult, CandidatesRequest, CandidatesResponse, Equivalent, Match, SummaryLine,
                       SummaryRequest, SummaryResponse, SummaryTotals)

router = APIRouter(prefix="/v1/prescription", tags=["prescription"])
VERIFY = "The spelling was different from our records. Please check this against your prescription."


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _names(brand: dict) -> list[str]:
    return [n for n in {norm(brand["brand_name"]), *(norm(a) for a in brand.get("aliases", []))} if n]


def match_one(raw: str, brands: list[dict]) -> CandidateResult:
    q = norm(raw)
    if not q:
        return CandidateResult(input=raw, tier="none", matches=[], reason="empty_input")

    def m(b: dict, score: float) -> Match:
        return Match(brand_id=b["brand_id"], brand_name=b["brand_name"],
                     composition_id=b["composition_id"], score=round(score, 1))

    exact = [b for b in brands if q in _names(b)]
    if len(exact) == 1:
        return CandidateResult(input=raw, tier="exact", matches=[m(exact[0], 100)])
    if len(exact) > 1:  # same name, several strengths: do not guess
        return CandidateResult(input=raw, tier="uncertain", reason="strength_needed",
                               matches=[m(b, 100) for b in exact[:3]],
                               verify_notice="Several strengths exist. Please choose the one on your prescription.")

    scored = sorted(((max(fuzz.WRatio(q, n) for n in _names(b)), b) for b in brands), key=lambda t: -t[0])
    if not scored or scored[0][0] < 70:
        return CandidateResult(input=raw, tier="none", matches=[], reason="not_in_data")
    top, second = scored[0][0], (scored[1][0] if len(scored) > 1 else 0)
    if top >= 88 and top - second >= 6:
        return CandidateResult(input=raw, tier="likely", matches=[m(scored[0][1], top)], verify_notice=VERIFY)
    return CandidateResult(input=raw, tier="uncertain", reason="close_matches",
                           matches=[m(b, s) for s, b in scored[:3] if s >= 70], verify_notice=VERIFY)


@router.post("/candidates", response_model=CandidatesResponse)
async def candidates(body: CandidatesRequest, request: Request) -> CandidatesResponse:
    brands = request.app.state.data.load("brands")
    return CandidatesResponse(results=[match_one(x[:80], brands) for x in body.items])


@router.post("/summary", response_model=SummaryResponse)
async def summary(body: SummaryRequest, request: Request) -> SummaryResponse:
    if not body.confirmed_by_user:
        raise ApiError(400, "CONFIRMATION_REQUIRED",
                       "Please confirm each medicine and the patient details before we calculate a total.")
    store = request.app.state.data
    brands = {b["brand_id"]: b for b in store.load("brands")}
    ja_all = store.load("janaushadhi_products")
    lines: list[SummaryLine] = []
    t_brand = t_ja = 0.0
    compared = 0

    for it in body.items:
        b = brands.get(it.brand_id)
        if not b:
            lines.append(SummaryLine(brand_id=it.brand_id, status="not_in_data", quantity_packs=it.quantity_packs,
                                     note="Not in our data."))
            continue
        base = dict(brand_id=it.brand_id, brand_name=b["brand_name"], composition_id=b["composition_id"],
                    quantity_packs=it.quantity_packs)
        ja = [p for p in ja_all if p["composition_id"] == b["composition_id"]]
        if not ja:
            lines.append(SummaryLine(**base, status="no_equivalent_in_data",
                                     note="No Jan Aushadhi product with this composition in our data."))
            continue
        ja = [p for p in ja if p["pack_unit"] == b["pack_unit"]]
        if not ja:
            lines.append(SummaryLine(**base, status="unit_mismatch",
                                     note="Pack units differ, so a fair comparison is not possible."))
            continue
        eqs = sorted((Equivalent(ja_code=p.get("ja_code"), generic_name=p["generic_name"], pack_size=p["pack_size"],
                                 pack_unit=p["pack_unit"], pack_price_inr=p["price_inr"],
                                 per_unit_inr=round(p["price_inr"] / p["pack_size"], 4),
                                 source=p.get("source"), price_date=p.get("price_date")) for p in ja),
                     key=lambda e: e.per_unit_inr)
        units = b["pack_size"] * it.quantity_packs
        brand_total = round(b["mrp_inr"] * it.quantity_packs, 2)
        ja_total = round(eqs[0].per_unit_inr * units, 2)
        compared += 1
        t_brand += brand_total
        t_ja += ja_total
        lines.append(SummaryLine(**base, status="compared", units=units, brand_total_inr=brand_total,
                                 listed_equivalent_total_inr=ja_total, difference_inr=round(brand_total - ja_total, 2),
                                 equivalents=eqs))

    totals = SummaryTotals(compared_lines=compared, not_compared_lines=len(lines) - compared,
                           brand_total_inr=round(t_brand, 2), listed_equivalent_total_inr=round(t_ja, 2),
                           difference_inr=round(t_brand - t_ja, 2))
    return SummaryResponse(patient=body.patient, lines=lines, totals=totals)
