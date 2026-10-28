"""Server-rendered HTML pages (read-only)."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.qr import passport_url

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

router = APIRouter(include_in_schema=False)

DbSession = Annotated[Session, Depends(get_db)]


def _not_found(request: Request, product_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "not_found.html", {"product_id": product_id}, status_code=404
    )


@router.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/batteries")


@router.get("/batteries", response_class=HTMLResponse)
def battery_list(request: Request, db: DbSession) -> HTMLResponse:
    batteries = crud.list_batteries(db, limit=200)
    return templates.TemplateResponse(request, "battery_list.html", {"batteries": batteries})


@router.get("/batteries/{product_id}", response_class=HTMLResponse)
def battery_detail(request: Request, product_id: str, db: DbSession) -> HTMLResponse:
    battery = crud.get_battery(db, product_id)
    if battery is None:
        return _not_found(request, product_id)
    return templates.TemplateResponse(
        request,
        "battery_detail.html",
        {"battery": battery, "passport_url": passport_url(battery.product_id)},
    )


@router.get("/passport/{product_id}", response_class=HTMLResponse)
def public_passport(request: Request, product_id: str, db: DbSession) -> HTMLResponse:
    battery = crud.get_battery(db, product_id)
    if battery is None:
        return _not_found(request, product_id)
    return templates.TemplateResponse(request, "passport.html", {"battery": battery})
