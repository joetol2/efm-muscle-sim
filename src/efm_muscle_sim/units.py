"""
Unit conversion helpers.

These are thin convenience functions. They do not perform dimensional analysis
or track units through calculations.
"""

from __future__ import annotations

import math


def rad_to_deg(angle_rad: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(angle_rad)


def deg_to_rad(angle_deg: float) -> float:
    """Convert degrees to radians."""
    return math.radians(angle_deg)


def n_to_kgf(force_n: float) -> float:
    """Convert Newtons to kilogram-force (kgf). 1 kgf = 9.80665 N."""
    return force_n / 9.80665


def kgf_to_n(force_kgf: float) -> float:
    """Convert kilogram-force (kgf) to Newtons."""
    return force_kgf * 9.80665


def m_to_mm(length_m: float) -> float:
    """Convert metres to millimetres."""
    return length_m * 1000.0


def mm_to_m(length_mm: float) -> float:
    """Convert millimetres to metres."""
    return length_mm / 1000.0
