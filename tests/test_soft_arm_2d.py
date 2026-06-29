from __future__ import annotations

import numpy as np

from efm_muscle_sim.soft_arm import SoftArm2D
from efm_muscle_sim.training_env import SoftArmReachEnv, SoftArmReachTaskParams


def test_soft_arm_forward_kinematics_returns_wrist() -> None:
    arm = SoftArm2D()
    state = arm.reset(shoulder_angle_rad=0.0, elbow_angle_rad=0.0)
    assert state["wrist_x_m"] > 0.0
    assert abs(state["wrist_y_m"]) < 1e-9


def test_soft_arm_step_accepts_four_commands() -> None:
    arm = SoftArm2D()
    arm.reset()
    state = arm.step([0.7, 0.0, 0.3, 0.0], dt=0.02)
    assert "shoulder_angle_rad" in state
    assert "elbow_angle_rad" in state
    assert 0.0 <= state["shoulder_flex_activation"] <= 1.0


def test_reach_env_step_shape() -> None:
    env = SoftArmReachEnv(
        SoftArmReachTaskParams(randomize_target=False, randomize_dynamics=False),
        seed=1,
    )
    obs, info = env.reset(seed=1)
    assert obs.shape == (16,)
    obs, reward, terminated, truncated, info = env.step(np.array([0.5, 0.0, 0.5, 0.0], dtype=np.float32))
    assert obs.shape == (16,)
    assert isinstance(float(reward), float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
