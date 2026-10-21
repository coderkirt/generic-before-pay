from typing import Literal

from pydantic import BaseModel, Field

from .context import current_request_id
from .disclaimer import DISCLAIMER


class Envelope(BaseModel):
    request_id: str = Field(default_factory=current_request_id)
    disclaimer: str = DISCLAIMER


class OcrResponse(Envelope):
    text: str
    candidates: list[str]
    language: str
    provider: str
    mock: bool
    preprocessed: bool
    notice: str = "Candidates are text read from the image, not verified matches. Please check each one."


class CandidatesRequest(BaseModel):
    items: list[str] = Field(min_length=1, max_length=30)


class Match(BaseModel):
    brand_id: str
    brand_name: str
    composition_id: str
    score: float


class CandidateResult(BaseModel):
    input: str
    tier: Literal["exact", "likely", "uncertain", "none"]
    reason: str | None = None
    matches: list[Match]
    verify_notice: str | None = None


class CandidatesResponse(Envelope):
    results: list[CandidateResult]


class Patient(BaseModel):
    age_years: float = Field(ge=0, le=120)
    gender: Literal["male", "female", "other", "prefer_not_to_say"]


class SummaryItem(BaseModel):
    brand_id: str
    quantity_packs: int = Field(default=1, ge=1, le=12)


class SummaryRequest(BaseModel):
    patient: Patient
    items: list[SummaryItem] = Field(min_length=1, max_length=30)
    confirmed_by_user: bool


class Equivalent(BaseModel):
    ja_code: str | None = None
    generic_name: str
    pack_size: float
    pack_unit: str
    pack_price_inr: float
    per_unit_inr: float
    source: str | None = None
    price_date: str | None = None


class SummaryLine(BaseModel):
    brand_id: str
    status: Literal["compared", "no_equivalent_in_data", "unit_mismatch", "not_in_data"]
    brand_name: str | None = None
    composition_id: str | None = None
    quantity_packs: int
    units: float | None = None
    brand_total_inr: float | None = None
    listed_equivalent_total_inr: float | None = None
    difference_inr: float | None = None
    equivalents: list[Equivalent] = []
    note: str | None = None


class SummaryTotals(BaseModel):
    compared_lines: int
    not_compared_lines: int
    brand_total_inr: float
    listed_equivalent_total_inr: float
    difference_inr: float


class SummaryResponse(Envelope):
    patient: Patient
    lines: list[SummaryLine]
    totals: SummaryTotals
    note: str = ("Totals include only lines with status 'compared'. Equivalent totals are estimated for the same "
                 "number of units. Please confirm with your doctor or pharmacist.")


class Kendra(BaseModel):
    kendra_code: str | None = None
    name: str
    address: str | None = None
    pincode: str | None = None
    district: str | None = None
    state: str | None = None
    phone: str | None = None
    lat: float
    lng: float
    distance_km: float
    maps_url: str
    data_date: str | None = None


class KendraResponse(Envelope):
    kendras: list[Kendra]
    note: str = "Please call ahead; stock may vary."
