"""Tests for parameter dataclasses."""

from __future__ import annotations

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from efm_muscle_sim import ElectroFluidicMuscleParams, AntagonisticJointParams


class TestElectroFluidicMuscleParams:
    def test_default_construction(self):
        p = ElectroFluidicMuscleParams()
        assert p.max_contraction_strain == pytest.approx(0.20)
        assert p.bundle_count == 1

    def test_invalid_rest_length_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(rest_length_m=0.0)

    def test_invalid_strain_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(max_contraction_strain=1.0)

    def test_negative_strain_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(max_contraction_strain=-0.1)

    def test_negative_response_time_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(response_time_s=-0.1)

    def test_negative_force_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(max_force_per_fiber_n=-1.0)

    def test_zero_bundle_count_raises(self):
        with pytest.raises(ValueError):
            ElectroFluidicMuscleParams(bundle_count=0)

    def test_valid_nondefault_params(self):
        p = ElectroFluidicMuscleParams(
            rest_length_m=0.15,
            bundle_count=4,
            max_force_per_fiber_n=2.5,
        )
        assert p.rest_length_m == pytest.approx(0.15)
        assert p.bundle_count == 4


class TestAntagonisticJointParams:
    def test_default_construction(self):
        p = AntagonisticJointParams()
        assert p.moment_arm_m == pytest.approx(0.025)

    def test_invalid_moment_arm_raises(self):
        with pytest.raises(ValueError):
            AntagonisticJointParams(moment_arm_m=0.0)

    def test_invalid_inertia_raises(self):
        with pytest.raises(ValueError):
            AntagonisticJointParams(inertia_kg_m2=0.0)

    def test_inverted_angle_limits_raises(self):
        with pytest.raises(ValueError):
            AntagonisticJointParams(min_angle_rad=1.0, max_angle_rad=0.5)
