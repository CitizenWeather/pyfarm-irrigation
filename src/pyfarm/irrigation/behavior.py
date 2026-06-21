"""Irrigation behavior."""

from __future__ import annotations

from datetime import time

from pyfarm.crops.registry import CultivarRegistry
from pyfarm.irrigation.calculator import IrrigationCalculator
from pyfarm.irrigation.models import (
    IrrigationEvent,
    IrrigationMethod,
    IrrigationSchedule,
    TriggerType,
)
from pyfarm.soil.models import SoilProfile

_CROP_COEFFICIENTS: dict[str, float] = {
    "mushroom": 0.6,
    "microgreen": 1.0,
    "default": 0.8,
}


class IrrigationBehavior:

    def __init__(self, registry: CultivarRegistry):
        self.registry = registry
        self.calculator = IrrigationCalculator()

    async def compute_schedule(
        self,
        cultivar_id: str,
        stage_index: int,
        eto: float,
        soil_profile: SoilProfile,
        area_m2: float = 1.0,
        flow_rate_l_min: float = 2.0,
    ) -> IrrigationSchedule:
        """Compute an ET-based daily irrigation schedule."""
        cultivar = await self.registry.get_cultivar(cultivar_id)
        if not cultivar:
            raise ValueError(f"Cultivar {cultivar_id} not found")

        kc = _CROP_COEFFICIENTS.get(cultivar.crop_type.value, _CROP_COEFFICIENTS["default"])
        volume = self.calculator.et_based_volume(eto, kc, area_m2)
        duration = self.calculator.run_time(volume, flow_rate_l_min)

        events = [
            IrrigationEvent(
                start_time=time(6, 0),
                duration_min=duration,
                volume_l=volume,
                trigger=TriggerType.ET_BASED,
            )
        ]

        if volume > 5.0:
            events.append(IrrigationEvent(
                start_time=time(14, 0),
                duration_min=duration / 2,
                volume_l=volume / 2,
                trigger=TriggerType.ET_BASED,
            ))

        return IrrigationSchedule(
            events=events,
            daily_budget_l=volume if len(events) == 1 else volume * 1.5,
            notes=f"ETo={eto:.2f} Kc={kc}",
        )

    async def deficit_irrigation(
        self,
        current_moisture: float,
        field_capacity: float,
        wilting_point: float,
        flow_rate_l_min: float = 2.0,
        area_m2: float = 1.0,
        depth_m: float = 0.25,
    ) -> IrrigationEvent:
        """Compute a single event to refill soil to field capacity."""
        deficit = max(0.0, field_capacity - current_moisture)
        volume_l = deficit * depth_m * area_m2 * 1000
        duration = self.calculator.run_time(volume_l, flow_rate_l_min)
        return IrrigationEvent(
            start_time=time(6, 0),
            duration_min=max(1.0, duration),
            volume_l=volume_l,
            trigger=TriggerType.SENSOR_THRESHOLD,
        )
