"""
Antagonistic joint model driven by two electrofluidic fiber muscle instances.

This is a one-degree-of-freedom hinge approximation. The flexor and extensor
muscles act in opposition through a fixed moment arm. The model integrates
angular dynamics with explicit Euler.
"""

from __future__ import annotations

import math
from typing import Dict

from .actuator import ElectroFluidicMuscle, _clamp
from .parameters import AntagonisticJointParams, ElectroFluidicMuscleParams


class AntagonisticJoint:
    """
    A one-degree-of-freedom joint driven by a flexor/extensor pair.

    Positive torque bends the joint (increasing angle). Joint angle is bounded
    by min_angle_rad and max_angle_rad. When a limit is reached, angular velocity
    is zeroed to prevent bouncing.

    This model is intended for behavioral exploration only. It does not replicate
    tendon routing, wrapping, or variable moment arm geometry.
    """

    def __init__(
        self,
        flexor: ElectroFluidicMuscle | None = None,
        extensor: ElectroFluidicMuscle | None = None,
        joint_params: AntagonisticJointParams | None = None,
    ) -> None:
        self.flexor = flexor or ElectroFluidicMuscle()
        self.extensor = extensor or ElectroFluidicMuscle()
        self.params = joint_params or AntagonisticJointParams()
        self.angle_rad: float = 0.0
        self.angular_velocity_rad_s: float = 0.0

    @classmethod
    def from_params(
        cls,
        muscle_params: ElectroFluidicMuscleParams | None = None,
        joint_params: AntagonisticJointParams | None = None,
    ) -> "AntagonisticJoint":
        """Convenience constructor that creates matched flexor and extensor."""
        p = muscle_params or ElectroFluidicMuscleParams()
        return cls(
            flexor=ElectroFluidicMuscle(p),
            extensor=ElectroFluidicMuscle(p),
            joint_params=joint_params,
        )

    def reset(self, angle_rad: float = 0.0) -> None:
        """Reset the joint to a given angle with zero velocity."""
        p = self.params
        self.angle_rad = _clamp(angle_rad, p.min_angle_rad, p.max_angle_rad)
        self.angular_velocity_rad_s = 0.0
        self.flexor.reset()
        self.extensor.reset()

    def step(self, flex_control: float, extend_control: float, dt: float) -> Dict[str, float]:
        """
        Advance the joint model by one timestep.

        Parameters
        ----------
        flex_control:
            Flexor activation command in [0, 1].
        extend_control:
            Extensor activation command in [0, 1].
        dt:
            Timestep in seconds. Must be positive.

        Returns
        -------
        dict
            State snapshot including angle, angular velocity, muscle forces,
            activations, and torques.
        """
        if dt <= 0:
            raise ValueError("dt must be positive")

        p = self.params

        flex_state = self.flexor.step(flex_control, dt)
        ext_state = self.extensor.step(extend_control, dt)

        torque_n_m = p.moment_arm_m * (flex_state["total_force_n"] - ext_state["total_force_n"])
        damping_n_m = -p.joint_damping_n_m_s * self.angular_velocity_rad_s
        net_torque_n_m = torque_n_m + damping_n_m

        angular_accel = net_torque_n_m / p.inertia_kg_m2
        self.angular_velocity_rad_s += angular_accel * dt
        self.angle_rad += self.angular_velocity_rad_s * dt

        if self.angle_rad <= p.min_angle_rad:
            self.angle_rad = p.min_angle_rad
            self.angular_velocity_rad_s = 0.0
        elif self.angle_rad >= p.max_angle_rad:
            self.angle_rad = p.max_angle_rad
            self.angular_velocity_rad_s = 0.0

        return {
            "angle_rad": self.angle_rad,
            "angle_deg": math.degrees(self.angle_rad),
            "angular_velocity_rad_s": self.angular_velocity_rad_s,
            "flex_force_n": flex_state["total_force_n"],
            "ext_force_n": ext_state["total_force_n"],
            "flex_activation": flex_state["activation"],
            "ext_activation": ext_state["activation"],
            "torque_n_m": torque_n_m,
            "net_torque_n_m": net_torque_n_m,
        }
