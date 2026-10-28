from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas import BatteryCreate


def test_valid_payload(battery_payload):
    battery = BatteryCreate.model_validate(battery_payload)
    assert battery.capacity_kwh == 10.0
    assert battery.is_demo_data is True


def test_lifecycle_status_defaults_to_manufactured(battery_payload):
    del battery_payload["lifecycle_status"]
    assert BatteryCreate.model_validate(battery_payload).lifecycle_status == "manufactured"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("product_id", "lowercase-id"),
        ("product_id", "AB"),
        ("product_id", "HAS SPACE"),
        ("capacity_kwh", 0),
        ("capacity_kwh", -5),
        ("recycled_lithium_pct", 101),
        ("recycled_lithium_pct", -1),
        ("chemistry", "UNOBTAINIUM"),
        ("lifecycle_status", "lost"),
        ("expected_cycle_life", 0),
        ("manufacturing_date", (date.today() + timedelta(days=1)).isoformat()),
    ],
)
def test_invalid_values_rejected(battery_payload, field, value):
    battery_payload[field] = value
    with pytest.raises(ValidationError):
        BatteryCreate.model_validate(battery_payload)


def test_unknown_field_rejected(battery_payload):
    battery_payload["colour"] = "blue"
    with pytest.raises(ValidationError):
        BatteryCreate.model_validate(battery_payload)
