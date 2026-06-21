"""pyfarm-irrigation: ET-based and sensor-triggered irrigation scheduling."""

from pyfarm.irrigation.behavior import IrrigationBehavior
from pyfarm.irrigation.calculator import IrrigationCalculator
from pyfarm.irrigation.models import (
    DrainageReading,
    IrrigationEvent,
    IrrigationMethod,
    IrrigationSchedule,
    TriggerType,
)

__version__ = "0.1.0"

__all__ = [
    "IrrigationMethod",
    "TriggerType",
    "IrrigationEvent",
    "IrrigationSchedule",
    "DrainageReading",
    "IrrigationCalculator",
    "IrrigationBehavior",
]
