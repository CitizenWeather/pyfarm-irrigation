"""Data models for irrigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional


class IrrigationMethod(str, Enum):
    DRIP = "drip"
    FLOOD_DRAIN = "flood_drain"
    OVERHEAD = "overhead"
    SUBSURFACE = "subsurface"


class TriggerType(str, Enum):
    TIME = "time"
    SENSOR_THRESHOLD = "sensor_threshold"
    ET_BASED = "et_based"


@dataclass
class IrrigationEvent:
    start_time: time = field(default_factory=lambda: time(6, 0))
    duration_min: float = 10.0
    volume_l: float = 0.0
    trigger: TriggerType = TriggerType.TIME
    method: IrrigationMethod = IrrigationMethod.DRIP

    def __post_init__(self):
        if self.duration_min <= 0:
            raise ValueError("duration_min must be positive")
        if self.volume_l < 0:
            raise ValueError("volume_l must be non-negative")


@dataclass
class IrrigationSchedule:
    events: list[IrrigationEvent] = field(default_factory=list)
    daily_budget_l: Optional[float] = None
    notes: str = ""


@dataclass
class DrainageReading:
    volume_l: float = 0.0
    ec_ms_cm: float = 0.0
    ph: float = 7.0

    def __post_init__(self):
        if self.volume_l < 0:
            raise ValueError("volume_l must be non-negative")
