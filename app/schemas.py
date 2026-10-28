"""Pydantic models: the API contract. They validate input and shape output."""

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.qr import passport_url as build_passport_url


class Chemistry(StrEnum):
    LFP = "LFP"
    NMC = "NMC"
    NCA = "NCA"
    LTO = "LTO"
    LEAD_ACID = "LEAD_ACID"
    NIMH = "NIMH"


class LifecycleStatus(StrEnum):
    MANUFACTURED = "manufactured"
    IN_SERVICE = "in_service"
    SECOND_LIFE = "second_life"
    END_OF_LIFE = "end_of_life"
    RECYCLED = "recycled"


PRODUCT_ID_PATTERN = r"^[A-Z0-9][A-Z0-9-]{2,63}$"

Percentage = Annotated[float, Field(ge=0, le=100)]


class BatteryBase(BaseModel):
    product_id: str = Field(
        pattern=PRODUCT_ID_PATTERN,
        examples=["DBW-IB-LFP-2025-000123"],
        description="Unique public identifier: uppercase letters, digits and hyphens, 3-64 chars.",
    )
    manufacturer: str = Field(min_length=1, max_length=120)
    model: str = Field(min_length=1, max_length=120)
    serial_number: str = Field(min_length=1, max_length=64)
    chemistry: Chemistry
    capacity_kwh: float = Field(gt=0)
    manufacturing_date: date
    lifecycle_status: LifecycleStatus = LifecycleStatus.MANUFACTURED

    nominal_voltage_v: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    expected_cycle_life: int = Field(gt=0)

    carbon_footprint_kg_co2e_per_kwh: float = Field(ge=0)
    recycled_cobalt_pct: Percentage | None = None
    recycled_lithium_pct: Percentage | None = None
    recycled_nickel_pct: Percentage | None = None
    recycled_lead_pct: Percentage | None = None
    end_of_life_info: str = Field(min_length=1)
    is_demo_data: bool = True


class BatteryCreate(BatteryBase):
    model_config = ConfigDict(extra="forbid")

    @field_validator("manufacturing_date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("manufacturing_date must not be in the future")
        return value


class BatteryRead(BatteryBase):
    # Allows BatteryRead.model_validate(orm_object)
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def passport_url(self) -> str:
        return build_passport_url(self.product_id)


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lifecycle_status: LifecycleStatus
