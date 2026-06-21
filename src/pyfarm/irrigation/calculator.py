"""Irrigation calculations."""

from __future__ import annotations


class IrrigationCalculator:

    @staticmethod
    def et_based_volume(
        eto: float,
        crop_coefficient: float,
        area_m2: float,
    ) -> float:
        """Irrigation volume in litres based on reference ETo (mm/day)."""
        etc = eto * crop_coefficient
        volume_mm = etc
        return round(volume_mm * area_m2, 2)

    @staticmethod
    def run_time(volume_l: float, flow_rate_l_min: float) -> float:
        """Irrigation run time in minutes."""
        if flow_rate_l_min <= 0:
            return 0.0
        return round(volume_l / flow_rate_l_min, 2)

    @staticmethod
    def drainage_fraction(applied_l: float, drainage_l: float) -> float:
        """Fraction of applied water that drains (0-1)."""
        if applied_l <= 0:
            return 0.0
        return round(min(1.0, drainage_l / applied_l), 4)
