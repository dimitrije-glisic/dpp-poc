"""Database access functions. Routers call these; they never build queries themselves."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Battery
from app.schemas import BatteryCreate, LifecycleStatus


class DuplicateBatteryError(Exception):
    """Raised when product_id or manufacturer + serial_number already exists."""


def get_battery(db: Session, product_id: str) -> Battery | None:
    return db.scalar(select(Battery).where(Battery.product_id == product_id))


def list_batteries(
    db: Session,
    status: LifecycleStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Battery]:
    query = select(Battery).order_by(Battery.product_id)
    if status is not None:
        query = query.where(Battery.lifecycle_status == status.value)
    return list(db.scalars(query.limit(limit).offset(offset)))


def create_battery(db: Session, data: BatteryCreate) -> Battery:
    # Check explicitly so the caller gets a clear message instead of a raw IntegrityError.
    existing = db.scalar(
        select(Battery).where(
            or_(
                Battery.product_id == data.product_id,
                (Battery.manufacturer == data.manufacturer)
                & (Battery.serial_number == data.serial_number),
            )
        )
    )
    if existing is not None:
        if existing.product_id == data.product_id:
            raise DuplicateBatteryError(f"product_id '{data.product_id}' already exists")
        raise DuplicateBatteryError(
            f"serial_number '{data.serial_number}' already exists for '{data.manufacturer}'"
        )

    battery = Battery(**data.model_dump(mode="python"))
    db.add(battery)
    db.commit()
    db.refresh(battery)
    return battery


def update_status(db: Session, battery: Battery, status: LifecycleStatus) -> Battery:
    battery.lifecycle_status = status.value
    db.commit()
    db.refresh(battery)
    return battery
