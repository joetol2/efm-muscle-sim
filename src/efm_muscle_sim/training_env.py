"""Training environment for the 2-DOF EFM soft arm reach demo.

This file works with Gymnasium when installed. Without Gymnasium, the class still
runs as a light environment for scripted rollouts and smoke tests.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Tuple

import numpy as np

try:  # pragma: no cover, exercised only when gymnasium is installed
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # pragma: no cover
    gym = None
    spaces = None

from .parameters import AntagonisticJointParams, ElectroFluidicMuscleParams
from .soft_arm import SoftArm2D, SoftArm2DParams


@dataclass
class SoftArmReachTaskParams:
    """Task settings for a trainable 2-DOF reaching demo."""

    dt: float = 0.02
    max_steps: int = 300
    target_x_m: float = 0.38
    target_y_m: float = 0.18
    target_radius_m: float = 0.025
    randomize_target: bool = True
    randomize_dynamics: bool = True
    contact_wall_x_m: float | None = None
    contact_stiffness_n_per_m: float = 25.0
    contact_damping_n_s_per_m: float = 0.4
    success_hold_steps: int = 20

    def __post_init__(self) -> None:
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if self.max_steps < 1:
            raise ValueError("max_steps must be positive")
        if self.target_radius_m <= 0:
            raise ValueError("target_radius_m must be positive")


_BaseEnv = gym.Env if gym is not None else object


class SoftArmReachEnv(_BaseEnv):
    """Gymnasium-compatible reaching task for the 2-DOF soft arm.

    Observation vector:
    [q1, q2, q1_dot, q2_dot, wrist_x, wrist_y, target_x, target_y,
     dx, dy, contact_fx, contact_fy, shoulder_flex_act, shoulder_ext_act,
     elbow_flex_act, elbow_ext_act]
    """

    metadata = {"render_modes": []}

    def __init__(self, task_params: SoftArmReachTaskParams | None = None, seed: int | None = None) -> None:
        if gym is not None:
            super().__init__()
        self.task_params = task_params or SoftArmReachTaskParams()
        self.rng = np.random.default_rng(seed)
        self.arm = self._build_arm()
        self.step_count = 0
        self.success_count = 0
        self.target = np.array([self.task_params.target_x_m, self.task_params.target_y_m], dtype=float)
        self.last_action = np.zeros(4, dtype=np.float32)
        self.last_contact_force = np.zeros(2, dtype=float)

        if spaces is not None:
            self.action_space = spaces.Box(low=0.0, high=1.0, shape=(4,), dtype=np.float32)
            obs_high = np.array(
                [
                    math.pi,
                    math.pi,
                    20.0,
                    20.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    100.0,
                    100.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                dtype=np.float32,
            )
            self.observation_space = spaces.Box(low=-obs_high, high=obs_high, dtype=np.float32)

    def _build_arm(self) -> SoftArm2D:
        t = self.task_params
        if t.randomize_dynamics:
            response_time = float(self.rng.uniform(0.20, 0.45))
            max_force = float(self.rng.uniform(0.75, 1.40))
            damping = float(self.rng.uniform(0.04, 0.10))
            stiffness = float(self.rng.uniform(3.5, 8.0))
        else:
            response_time = 0.30
            max_force = 1.0
            damping = 0.05
            stiffness = 5.0

        muscle = ElectroFluidicMuscleParams(
            rest_length_m=0.10,
            max_contraction_strain=0.20,
            response_time_s=response_time,
            max_force_per_fiber_n=max_force,
            bundle_count=6,
            passive_stiffness_n_per_m=stiffness,
            damping_n_s_per_m=damping,
        )
        shoulder = AntagonisticJointParams(
            moment_arm_m=0.030,
            inertia_kg_m2=0.035,
            joint_damping_n_m_s=0.18,
            min_angle_rad=-1.20,
            max_angle_rad=1.80,
        )
        elbow = AntagonisticJointParams(
            moment_arm_m=0.022,
            inertia_kg_m2=0.018,
            joint_damping_n_m_s=0.13,
            min_angle_rad=0.00,
            max_angle_rad=2.35,
        )
        return SoftArm2D(
            SoftArm2DParams(
                link1_length_m=0.30,
                link2_length_m=0.24,
                shoulder_joint=shoulder,
                elbow_joint=elbow,
                muscle=muscle,
            )
        )

    def _sample_target(self) -> np.ndarray:
        if not self.task_params.randomize_target:
            return np.array([self.task_params.target_x_m, self.task_params.target_y_m], dtype=float)
        radius = float(self.rng.uniform(0.25, 0.48))
        theta = float(self.rng.uniform(0.05, 1.15))
        return np.array([radius * math.cos(theta), radius * math.sin(theta)], dtype=float)

    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.arm = self._build_arm()
        self.step_count = 0
        self.success_count = 0
        self.target = self._sample_target()
        shoulder_start = float(self.rng.uniform(-0.15, 0.35))
        elbow_start = float(self.rng.uniform(0.25, 0.85))
        self.arm.reset(shoulder_start, elbow_start)
        self.last_action = np.zeros(4, dtype=np.float32)
        self.last_contact_force = np.zeros(2, dtype=float)
        return self._get_obs(), self._get_info()

    def _compute_contact_force(self) -> np.ndarray:
        t = self.task_params
        if t.contact_wall_x_m is None:
            return np.zeros(2, dtype=float)
        state = self.arm.state()
        penetration = max(0.0, state["wrist_x_m"] - t.contact_wall_x_m)
        if penetration <= 0.0:
            return np.zeros(2, dtype=float)
        wrist_v = self._estimate_wrist_velocity()
        fx = -(t.contact_stiffness_n_per_m * penetration + t.contact_damping_n_s_per_m * max(0.0, wrist_v[0]))
        return np.array([fx, 0.0], dtype=float)

    def _estimate_wrist_velocity(self) -> np.ndarray:
        q_dot = np.array(self.arm.joint_velocities_rad_s, dtype=float)
        return self.arm.endpoint_jacobian() @ q_dot

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        action_arr = np.clip(np.asarray(action, dtype=np.float32), 0.0, 1.0)
        contact_force = self._compute_contact_force()
        self.arm.step(action_arr, self.task_params.dt, endpoint_force_n=contact_force)
        self.last_action = action_arr
        self.last_contact_force = contact_force
        self.step_count += 1

        obs = self._get_obs()
        info = self._get_info()
        distance = info["distance_to_target_m"]
        is_success = bool(distance <= self.task_params.target_radius_m)
        self.success_count = self.success_count + 1 if is_success else 0

        reward = self._reward(distance, action_arr, info)
        terminated = self.success_count >= self.task_params.success_hold_steps
        truncated = self.step_count >= self.task_params.max_steps
        info["is_success"] = is_success
        return obs, reward, terminated, truncated, info

    def _reward(self, distance: float, action: np.ndarray, info: Dict[str, Any]) -> float:
        velocity_cost = 0.015 * (
            abs(info["shoulder_velocity_rad_s"]) + abs(info["elbow_velocity_rad_s"])
        )
        action_cost = 0.025 * float(np.square(action).mean())
        co_contraction = 0.04 * (
            min(action[0], action[1]) + min(action[2], action[3])
        )
        success_bonus = 2.0 if distance <= self.task_params.target_radius_m else 0.0
        return float(-distance - velocity_cost - action_cost - co_contraction + success_bonus)

    def _get_obs(self) -> np.ndarray:
        state = self.arm.state()
        dx = self.target[0] - state["wrist_x_m"]
        dy = self.target[1] - state["wrist_y_m"]
        return np.array(
            [
                state["shoulder_angle_rad"],
                state["elbow_angle_rad"],
                state["shoulder_velocity_rad_s"],
                state["elbow_velocity_rad_s"],
                state["wrist_x_m"],
                state["wrist_y_m"],
                self.target[0],
                self.target[1],
                dx,
                dy,
                self.last_contact_force[0],
                self.last_contact_force[1],
                state["shoulder_flex_activation"],
                state["shoulder_extend_activation"],
                state["elbow_flex_activation"],
                state["elbow_extend_activation"],
            ],
            dtype=np.float32,
        )

    def _get_info(self) -> Dict[str, Any]:
        state = self.arm.state()
        dx = self.target[0] - state["wrist_x_m"]
        dy = self.target[1] - state["wrist_y_m"]
        distance = float(math.hypot(dx, dy))
        return {
            "step_count": self.step_count,
            "target_x_m": float(self.target[0]),
            "target_y_m": float(self.target[1]),
            "wrist_x_m": state["wrist_x_m"],
            "wrist_y_m": state["wrist_y_m"],
            "distance_to_target_m": distance,
            "shoulder_angle_deg": state["shoulder_angle_deg"],
            "elbow_angle_deg": state["elbow_angle_deg"],
            "shoulder_velocity_rad_s": state["shoulder_velocity_rad_s"],
            "elbow_velocity_rad_s": state["elbow_velocity_rad_s"],
            "contact_force_x_n": float(self.last_contact_force[0]),
            "contact_force_y_n": float(self.last_contact_force[1]),
        }
