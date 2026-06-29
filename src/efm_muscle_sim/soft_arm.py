"""Two-degree-of-freedom soft arm model driven by antagonistic EFM muscle pairs.

This module is an additive prototype layer on top of the existing one-degree-of-freedom
AntagonisticJoint model. It is intended for control demos and training environments,
not hardware sizing or quantitative performance claims.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Iterable, Tuple

import numpy as np

from .joint import AntagonisticJoint
from .parameters import AntagonisticJointParams, ElectroFluidicMuscleParams


@dataclass
class SoftArm2DParams:
    """Geometry and joint settings for a planar two-link soft arm."""

    link1_length_m: float = 0.30
    link2_length_m: float = 0.24
    shoulder_joint: AntagonisticJointParams | None = None
    elbow_joint: AntagonisticJointParams | None = None
    muscle: ElectroFluidicMuscleParams | None = None

    def __post_init__(self) -> None:
        if self.link1_length_m <= 0:
            raise ValueError("link1_length_m must be positive")
        if self.link2_length_m <= 0:
            raise ValueError("link2_length_m must be positive")

    @property
    def resolved_shoulder_joint(self) -> AntagonisticJointParams:
        return self.shoulder_joint or AntagonisticJointParams(
            moment_arm_m=0.030,
            inertia_kg_m2=0.035,
            joint_damping_n_m_s=0.18,
            min_angle_rad=-1.20,
            max_angle_rad=1.80,
        )

    @property
    def resolved_elbow_joint(self) -> AntagonisticJointParams:
        return self.elbow_joint or AntagonisticJointParams(
            moment_arm_m=0.022,
            inertia_kg_m2=0.018,
            joint_damping_n_m_s=0.13,
            min_angle_rad=0.00,
            max_angle_rad=2.35,
        )

    @property
    def resolved_muscle(self) -> ElectroFluidicMuscleParams:
        return self.muscle or ElectroFluidicMuscleParams(
            rest_length_m=0.10,
            max_contraction_strain=0.20,
            response_time_s=0.30,
            max_force_per_fiber_n=1.0,
            bundle_count=6,
            passive_stiffness_n_per_m=5.0,
            damping_n_s_per_m=0.05,
        )


class SoftArm2D:
    """Planar 2-DOF soft arm with shoulder and elbow antagonistic joints.

    Action order is:
    [shoulder_flex, shoulder_extend, elbow_flex, elbow_extend]

    Each command is clipped to [0, 1]. Positive shoulder torque raises the first link.
    Positive elbow torque bends the second link relative to the first.
    """

    def __init__(self, params: SoftArm2DParams | None = None) -> None:
        self.params = params or SoftArm2DParams()
        muscle_params = self.params.resolved_muscle
        self.shoulder = AntagonisticJoint.from_params(
            muscle_params=muscle_params,
            joint_params=self.params.resolved_shoulder_joint,
        )
        self.elbow = AntagonisticJoint.from_params(
            muscle_params=muscle_params,
            joint_params=self.params.resolved_elbow_joint,
        )
        self._last_endpoint_force_n = np.zeros(2, dtype=float)

    def reset(self, shoulder_angle_rad: float = 0.20, elbow_angle_rad: float = 0.55) -> Dict[str, float]:
        """Reset the arm and return its initial state snapshot."""

        self.shoulder.reset(shoulder_angle_rad)
        self.elbow.reset(elbow_angle_rad)
        self._last_endpoint_force_n = np.zeros(2, dtype=float)
        return self.state()

    @property
    def joint_angles_rad(self) -> Tuple[float, float]:
        return self.shoulder.angle_rad, self.elbow.angle_rad

    @property
    def joint_velocities_rad_s(self) -> Tuple[float, float]:
        return self.shoulder.angular_velocity_rad_s, self.elbow.angular_velocity_rad_s

    def forward_kinematics(self) -> Dict[str, Tuple[float, float]]:
        """Return base, elbow, and wrist positions in metres."""

        q1, q2 = self.joint_angles_rad
        l1 = self.params.link1_length_m
        l2 = self.params.link2_length_m

        base = (0.0, 0.0)
        elbow = (l1 * math.cos(q1), l1 * math.sin(q1))
        wrist = (
            elbow[0] + l2 * math.cos(q1 + q2),
            elbow[1] + l2 * math.sin(q1 + q2),
        )
        return {"base": base, "elbow": elbow, "wrist": wrist}

    def endpoint_jacobian(self) -> np.ndarray:
        """Return the 2x2 planar Jacobian for the wrist position."""

        q1, q2 = self.joint_angles_rad
        l1 = self.params.link1_length_m
        l2 = self.params.link2_length_m
        s1 = math.sin(q1)
        c1 = math.cos(q1)
        s12 = math.sin(q1 + q2)
        c12 = math.cos(q1 + q2)

        return np.array(
            [
                [-l1 * s1 - l2 * s12, -l2 * s12],
                [l1 * c1 + l2 * c12, l2 * c12],
            ],
            dtype=float,
        )

    def endpoint_force_to_joint_torques(self, endpoint_force_n: Iterable[float]) -> Tuple[float, float]:
        """Map an endpoint force into shoulder and elbow torques using J^T F."""

        force = np.asarray(list(endpoint_force_n), dtype=float)
        if force.shape != (2,):
            raise ValueError("endpoint_force_n must contain exactly two values")
        torques = self.endpoint_jacobian().T @ force
        return float(torques[0]), float(torques[1])

    def _apply_external_torque(self, joint: AntagonisticJoint, torque_n_m: float, dt: float) -> None:
        """Apply an external torque after the muscle-driven joint step."""

        if torque_n_m == 0.0:
            return
        p = joint.params
        joint.angular_velocity_rad_s += (torque_n_m / p.inertia_kg_m2) * dt
        joint.angle_rad += joint.angular_velocity_rad_s * dt
        if joint.angle_rad <= p.min_angle_rad:
            joint.angle_rad = p.min_angle_rad
            joint.angular_velocity_rad_s = 0.0
        elif joint.angle_rad >= p.max_angle_rad:
            joint.angle_rad = p.max_angle_rad
            joint.angular_velocity_rad_s = 0.0

    def step(
        self,
        action: Iterable[float],
        dt: float,
        endpoint_force_n: Iterable[float] | None = None,
        external_joint_torques_n_m: Iterable[float] | None = None,
    ) -> Dict[str, float]:
        """Advance the arm by one timestep.

        endpoint_force_n is useful for contact demos. It is converted to joint torques.
        external_joint_torques_n_m can be used for pushback or disturbance events.
        """

        if dt <= 0:
            raise ValueError("dt must be positive")

        cmd = np.clip(np.asarray(list(action), dtype=float), 0.0, 1.0)
        if cmd.shape != (4,):
            raise ValueError("action must contain four values")

        force = np.zeros(2, dtype=float)
        if endpoint_force_n is not None:
            force += np.asarray(list(endpoint_force_n), dtype=float)
        self._last_endpoint_force_n = force.copy()

        torque_from_force = np.array(self.endpoint_force_to_joint_torques(force), dtype=float)
        if external_joint_torques_n_m is not None:
            torque_from_force += np.asarray(list(external_joint_torques_n_m), dtype=float)

        shoulder_state = self.shoulder.step(cmd[0], cmd[1], dt)
        elbow_state = self.elbow.step(cmd[2], cmd[3], dt)

        self._apply_external_torque(self.shoulder, float(torque_from_force[0]), dt)
        self._apply_external_torque(self.elbow, float(torque_from_force[1]), dt)

        state = self.state()
        state.update(
            {
                "shoulder_flex_command": float(cmd[0]),
                "shoulder_extend_command": float(cmd[1]),
                "elbow_flex_command": float(cmd[2]),
                "elbow_extend_command": float(cmd[3]),
                "shoulder_muscle_torque_n_m": float(shoulder_state["torque_n_m"]),
                "elbow_muscle_torque_n_m": float(elbow_state["torque_n_m"]),
                "endpoint_force_x_n": float(force[0]),
                "endpoint_force_y_n": float(force[1]),
                "external_shoulder_torque_n_m": float(torque_from_force[0]),
                "external_elbow_torque_n_m": float(torque_from_force[1]),
            }
        )
        return state

    def state(self) -> Dict[str, float]:
        """Return a flat state dictionary for CSV logging and plotting."""

        q1, q2 = self.joint_angles_rad
        v1, v2 = self.joint_velocities_rad_s
        pts = self.forward_kinematics()
        wrist_x, wrist_y = pts["wrist"]
        elbow_x, elbow_y = pts["elbow"]

        return {
            "shoulder_angle_rad": q1,
            "shoulder_angle_deg": math.degrees(q1),
            "elbow_angle_rad": q2,
            "elbow_angle_deg": math.degrees(q2),
            "shoulder_velocity_rad_s": v1,
            "elbow_velocity_rad_s": v2,
            "elbow_x_m": elbow_x,
            "elbow_y_m": elbow_y,
            "wrist_x_m": wrist_x,
            "wrist_y_m": wrist_y,
            "shoulder_flex_activation": self.shoulder.flexor.activation,
            "shoulder_extend_activation": self.shoulder.extensor.activation,
            "elbow_flex_activation": self.elbow.flexor.activation,
            "elbow_extend_activation": self.elbow.extensor.activation,
            "last_endpoint_force_x_n": float(self._last_endpoint_force_n[0]),
            "last_endpoint_force_y_n": float(self._last_endpoint_force_n[1]),
        }
