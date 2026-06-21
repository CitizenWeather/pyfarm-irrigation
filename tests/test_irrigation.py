"""Smoke tests for pyfarm-irrigation."""

import pytest
from datetime import time

from pyfarm.crops import MemoryRegistry
from pyfarm.irrigation import (
    IrrigationBehavior,
    IrrigationCalculator,
    IrrigationEvent,
    IrrigationMethod,
    IrrigationSchedule,
    TriggerType,
    DrainageReading,
)
from pyfarm.soil.models import SoilProfile


def test_irrigation_event_defaults():
    e = IrrigationEvent()
    assert e.duration_min == 10.0


def test_irrigation_event_validation():
    with pytest.raises(ValueError):
        IrrigationEvent(duration_min=0)
    with pytest.raises(ValueError):
        IrrigationEvent(volume_l=-1)


def test_drainage_reading_validation():
    with pytest.raises(ValueError):
        DrainageReading(volume_l=-1)


def test_et_based_volume():
    vol = IrrigationCalculator.et_based_volume(5.0, 0.8, 10.0)
    assert vol == pytest.approx(40.0)


def test_run_time():
    t = IrrigationCalculator.run_time(20.0, 4.0)
    assert t == pytest.approx(5.0)


def test_run_time_zero_flow():
    assert IrrigationCalculator.run_time(20.0, 0.0) == 0.0


def test_drainage_fraction():
    assert IrrigationCalculator.drainage_fraction(10.0, 2.0) == pytest.approx(0.2)


def test_drainage_fraction_zero_applied():
    assert IrrigationCalculator.drainage_fraction(0.0, 1.0) == 0.0


@pytest.mark.asyncio
async def test_compute_schedule():
    registry = MemoryRegistry()
    behavior = IrrigationBehavior(registry)
    profile = SoilProfile(ph=6.5, ec_ms_cm=1.5)
    schedule = await behavior.compute_schedule(
        "radish-microgreen", 0, eto=4.0, soil_profile=profile
    )
    assert isinstance(schedule, IrrigationSchedule)
    assert len(schedule.events) >= 1


@pytest.mark.asyncio
async def test_compute_schedule_high_eto():
    registry = MemoryRegistry()
    behavior = IrrigationBehavior(registry)
    profile = SoilProfile(ph=6.5, ec_ms_cm=1.5)
    schedule = await behavior.compute_schedule(
        "radish-microgreen", 0, eto=10.0, soil_profile=profile, area_m2=5.0
    )
    assert len(schedule.events) == 2


@pytest.mark.asyncio
async def test_deficit_irrigation():
    registry = MemoryRegistry()
    behavior = IrrigationBehavior(registry)
    event = await behavior.deficit_irrigation(
        current_moisture=0.15, field_capacity=0.35, wilting_point=0.10
    )
    assert isinstance(event, IrrigationEvent)
    assert event.trigger == TriggerType.SENSOR_THRESHOLD
    assert event.volume_l > 0


@pytest.mark.asyncio
async def test_missing_cultivar():
    registry = MemoryRegistry()
    behavior = IrrigationBehavior(registry)
    profile = SoilProfile(ph=6.5, ec_ms_cm=1.5)
    with pytest.raises(ValueError):
        await behavior.compute_schedule("nonexistent", 0, eto=4.0, soil_profile=profile)
