"""Tests for AntagonisticJoint."""

from __future__ import annotations

import math
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from efm_muscle_sim import AntagonisticJoint, AntagonisticJointParams, ElectroFluidicMuscleParams


def make_joint(**joint_kwargs) -> AntagonisticJoint:
    return AntagonisticJoint.from_params(joint_params=AntagonisticJointParams(**joint_kwargs))


def test_joint_angle_changes_under_flexor():
    """Driving the flexor with zero extensor should increase joint angle."""
    joint = make_joint()
    initial_angle = joint.angle_rad
    for _ in range(200):
        joint.step(0.8, 0.0, dt=0.01)
    assert joint.angle_rad > initial_angle


def test_joint_angle_changes_under_extensor():
    """Driving the extensor from a positive angle should decrease angle."""
    joint = make_joint()
    # Pre-flex
    for _ in range(200):
        joint.step(0.8, 0.0, dt=0.01)
    flexed_angle = joint.angle_rad

    for _ in range(300):
        joint.step(0.0, 0.8, dt=0.01)
    assert joint.angle_rad < flexed_angle


def test_min_angle_limit_respected():
    """Joint angle must not go below min_angle_rad."""
    joint = make_joint(min_angle_rad=-0.5, max_angle_rad=2.0)
    for _ in range(1000):
        joint.step(0.0, 1.0, dt=0.01)
    assert joint.angle_rad >= -0.5 - 1e-9


def test_max_angle_limit_respected():
    """Joint angle must not exceed max_angle_rad."""
    joint = make_joint(min_angle_rad=-0.5, max_angle_rad=2.0)
    for _ in range(1000):
        joint.step(1.0, 0.0, dt=0.01)
    assert joint.angle_rad <= 2.0 + 1e-9


def test_reset_zeroes_joint():
    """reset() must zero angle and angular velocity."""
    joint = make_joint()
    for _ in range(200):
        joint.step(0.8, 0.0, dt=0.01)

    joint.reset()
    assert joint.angle_rad == pytest.approx(0.0)
    assert joint.angular_velocity_rad_s == pytest.approx(0.0)


def test_zero_dt_raises():
    joint = make_joint()
    with pytest.raises(ValueError):
        joint.step(0.5, 0.5, dt=0.0)


def test_no_nan_in_joint_outputs():
    """No NaN values should appear in joint state during a flex/extend cycle."""
    joint = make_joint()
    for i in range(400):
        flex = 0.8 if i < 100 else 0.0
        ext = 0.8 if 200 <= i < 300 else 0.0
        state = joint.step(flex, ext, dt=0.01)
        for key, val in state.items():
            assert not math.isnan(val), f"NaN in key '{key}' at step {i}"


def test_asymmetric_control_produces_net_rotation():
    """Asymmetric flex vs extend control must produce a nonzero final angle."""
    joint = make_joint()
    for _ in range(300):
        joint.step(0.9, 0.1, dt=0.01)
    assert abs(joint.angle_rad) > 0.01
