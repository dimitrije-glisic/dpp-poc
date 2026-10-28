"""SQLAlchemy ORM model. This describes how data is stored, not how it is validated."""

from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Battery(Base):
    __tablename__ = "batteries"
    __table_args__ = (
        UniqueConstraint("manufacturer", "serial_number", name="uq_manufacturer_serial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Product identity
    manufacturer: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(120))
    serial_number: Mapped[str] = mapped_column(String(64))
    chemistry: Mapped[str] = mapped_column(String(20))
    capacity_kwh: Mapped[float] = mapped_column(Float)
    manufacturing_date: Mapped[date] = mapped_column(Date)
    lifecycle_status: Mapped[str] = mapped_column(String(20), index=True)

    # Technical specifications
    nominal_voltage_v: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    expected_cycle_life: Mapped[int] = mapped_column(Integer)

    # Passport / sustainability information (illustrative demo values)
    carbon_footprint_kg_co2e_per_kwh: Mapped[float] = mapped_column(Float)
    recycled_cobalt_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    recycled_lithium_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    recycled_nickel_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    recycled_lead_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_of_life_info: Mapped[str] = mapped_column(Text)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
