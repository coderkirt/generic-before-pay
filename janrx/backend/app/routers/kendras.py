from math import asin, cos, radians, sin, sqrt

from fastapi import APIRouter, Query, Request

from ..schemas import Kendra, KendraResponse

router = APIRouter(prefix="/v1/kendras", tags=["kendras"])


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * 6371.0088 * asin(sqrt(a))


@router.get("/nearest", response_model=KendraResponse)
async def nearest(request: Request, lat: float = Query(ge=-90, le=90), lng: float = Query(ge=-180, le=180),
                  limit: int = Query(3, ge=1, le=10)) -> KendraResponse:
    rows = request.app.state.data.load("kendras")
    ranked = sorted(rows, key=lambda k: haversine_km(lat, lng, k["lat"], k["lng"]))[:limit]
    out = [Kendra(**{**k, "distance_km": round(haversine_km(lat, lng, k["lat"], k["lng"]), 1),
                     "maps_url": f"https://www.google.com/maps/search/?api=1&query={k['lat']},{k['lng']}"})
           for k in ranked]
    return KendraResponse(kendras=out)
