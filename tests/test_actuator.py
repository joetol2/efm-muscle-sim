"""Tests for ElectroFluidicMuscle."""

from __future__ import annotations

import math
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from efm_muscle_sim import ElectroFluidicMuscle, ElectroFluidicMuscleParams


def make_muscle(**kwargs) -> ElectroFluidicMuscle:
    return ElectroFluidicMuscle(ElectroFluidicMuscleParams(**kwargs))


# ------------------------------------------------------------------
# Basic activation behavior
# ------------------------------------------------------------------

def test_contraction_increases_with_control():
    """Activation grows toward control=1 over time."""
    m = make_muscle()
    strain_before = m.current_contraction
    for _ in range(50):
        m.step(1.0, dt=0.02)
    assert m.current_contraction > strain_before


def test_contraction_bounded_by_max_strain():
    """Contraction strain never exceeds max_contraction_strain."""
    m = make_muscle(max_contraction_strain=0.20)
    for _ in range(500):
        m.step(1.0, dt=0.01)
    assert m.current_contraction <= 0.20 + 1e-9


def test_bundle_count_scales_force():
    """Doubling bundle_count should double total force at steady state."""
    steps = 300

    m1 = make_muscle(bundle_count=1, max_force_per_fiber_n=1.0)
    for _ in range(steps):
        s1 = m1.step(1.0, dt=0.01)

    m2 = make_muscle(bundle_count=2, max_force_per_fiber_n=1.0)
    for _ in range(steps):
        s2 = m2.step(1.0, dt=0.01)

    assert abs(s2["total_force_n"] - 2.0 * s1["total_force_n"]) < 1e-6


def test_reset_clears_state():
    """reset() should return the actuator to zero activation and rest length."""
    m = make_muscle()
    for _ in range(100):
        m.step(1.0, dt=0.01)
    assert m.current_contraction > 0.01

    m.reset()
    assert m.activation == pytest.approx(0.0)
    assert m.current_length_m == pytest.approx(m.params.rest_length_m)
    assert m.current_contraction == pytest.approx(0.0)


def test_control_clamped_above_one():
    """Control values > 1 should be silently clamped to 1."""
    m = make_muscle()
    state = m.step(control=5.0, dt=0.01)
    assert 0.0 <= state["activation"] <= 1.0


def test_control_clamped_below_zero():
    """Control values < 0 should be silently clamped to 0."""
    m = make_muscle()
    state = m.step(control=-2.0, dt=0.01)
    assert state["activation"] >= 0.0


def test_zero_dt_raises():
    """dt=0 must raise ValueError."""
    m = make_muscle()
    with pytest.raises(ValueError):
        m.step(0.5, dt=0.0)


def test_negative_dt_raises():
    """Negative dt must raise ValueError."""
    m = make_muscle()
    with pytest.raises(ValueError):
        m.step(0.5, dt=-0.01)


def test_no_nan_in_outputs():
    """State dict values must not be NaN after any standard sequence."""
    m = make_muscle()
    for i in range(200):
        ctrl = 1.0 if i < 100 else 0.0
        state = m.step(ctrl, dt=0.01)
        for key, val in state.items():
            assert not math.isnan(val), f"NaN found in key '{key}' at step {i}"


def test_step_returns_expected_keys():
    """step() should return a dict with all required keys."""
    m = make_muscle()
    state = m.step(0.5, dt=0.01)
    required = {
        "activation",
        "target_contraction_strain",
        "current_length_m",
        "current_contraction_strain",
        "active_force_n",
        "passive_force_n",
        "damping_force_n",
        "total_force_n",
    }
    assert required.issubset(state.keys())
