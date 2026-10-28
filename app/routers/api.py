"""REST API endpoints (JSON). Documented automatically at /docs."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Battery
from app.qr import make_qr, passport_url
from app.schemas import BatteryCreate, BatteryRead, LifecycleStatus, StatusUpdate

router = APIRouter(prefix="/api/batteries", tags=["batteries"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_or_404(db: Session, product_id: str) -> Battery:
    battery = crud.get_battery(db, product_id)
    if battery is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Battery '{product_id}' not found")
    return battery


@router.post("", response_model=BatteryRead, status_code=status.HTTP_201_CREATED)
def register_battery(data: BatteryCreate, db: DbSession) -> Battery:
    try:
        return crud.create_battery(db, data)
    except crud.DuplicateBatteryError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("", response_model=list[BatteryRead])
def list_batteries(
    db: DbSession,
    status_filter: Annotated[LifecycleStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Battery]:
    return crud.list_batteries(db, status=status_filter, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=BatteryRead)
def get_battery(product_id: str, db: DbSession) -> Battery:
    return _get_or_404(db, product_id)


@router.patch("/{product_id}/status", response_model=BatteryRead)
def update_lifecycle_status(product_id: str, data: StatusUpdate, db: DbSession) -> Battery:
    battery = _get_or_404(db, product_id)
    return crud.update_status(db, battery, data.lifecycle_status)


@router.get(
    "/{product_id}/qr",
    responses={200: {"content": {"image/png": {}, "image/svg+xml": {}}}},
    response_class=Response,
)
def get_qr_code(
    product_id: str,
    db: DbSession,
    format: Literal["png", "svg"] = "png",
) -> Response:
    battery = _get_or_404(db, product_id)
    image = make_qr(passport_url(battery.product_id), kind=format)
    media_type = "image/png" if format == "png" else "image/svg+xml"
    return Response(content=image, media_type=media_type)
