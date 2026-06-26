"""
Behavioral model for a single electrofluidic fiber muscle bundle.

This is a first-order system-level abstraction. It does not simulate internal
pump dynamics, fluid pressure, cavitation, or material deformation. Use it for
robotics control sketches and early feasibility exploration only.
"""

from __future__ import annotations

from typing import Dict

from .parameters import ElectroFluidicMuscleParams


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class ElectroFluidicMuscle:
    """
    Compliant linear actuator abstraction for an electrofluidic fiber muscle bundle.

    Control input is normalized to [0, 1]. Activation follows a first-order lag
    using the response_time_s parameter. Force scales linearly with activation
    and bundle_count. A passive spring and velocity damper approximate compliance.

    The model integrates forward in discrete time via explicit Euler.
    """

    def __init__(self, params: ElectroFluidicMuscleParams | None = None) -> None:
        self.params = params or ElectroFluidicMuscleParams()
        self._activation: float = 0.0
        self._current_length_m: float = self.params.rest_length_m
        self._prev_length_m: float = self.params.rest_length_m

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def activation(self) -> float:
        """Current activation level in [0, 1]."""
        return self._activation

    @property
    def current_length_m(self) -> float:
        """Current fiber length in metres."""
        return self._current_length_m

    @property
    def current_contraction(self) -> float:
        """Current contraction as a strain fraction relative to rest length."""
        return (self.params.rest_length_m - self._current_length_m) / self.params.rest_length_m

    @property
    def current_force_n(self) -> float:
        """
        Instantaneous force estimate in Newtons based on current activation.

        This is the active contribution only; passive and damping terms are
        computed inside step().
        """
        return self._activation * self.params.max_force_per_fiber_n * self.params.bundle_count

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the actuator to the fully relaxed state."""
        self._activation = 0.0
        self._current_length_m = self.params.rest_length_m
        self._prev_length_m = self.params.rest_length_m

    def step(self, control: float, dt: float) -> Dict[str, float]:
        """
        Advance the actuator model by one timestep.

        Parameters
        ----------
        control:
            Normalized activation command in [0, 1]. Values outside this range
            are clamped silently.
        dt:
            Timestep in seconds. Must be positive.

        Returns
        -------
        dict
            State snapshot with keys:
            - activation
            - target_contraction_strain
            - current_length_m
            - current_contraction_strain
            - active_force_n
            - passive_force_n
            - damping_force_n
            - total_force_n
        """
        if dt <= 0:
            raise ValueError("dt must be positive")

        p = self.params
        control = _clamp(control, 0.0, 1.0)

        # First-order activation lag
        tau = p.response_time_s
        self._activation += (dt / tau) * (control - self._activation)
        self._activation = _clamp(self._activation, 0.0, 1.0)

        # Target contraction determines the length the muscle is pulling toward
        target_contraction_strain = self._activation * p.max_contraction_strain
        target_length_m = p.rest_length_m * (1.0 - target_contraction_strain)
        min_length_m = p.rest_length_m * p.min_length_fraction
        target_length_m = max(target_length_m, min_length_m)

        # Update current length by stepping toward target (Euler, full pull this step)
        # The current length follows the target with lag from the activation filter
        self._prev_length_m = self._current_length_m
        self._current_length_m = target_length_m

        # Velocity estimate from length change
        velocity_m_s = (self._current_length_m - self._prev_length_m) / dt

        # Force components
        length_error_m = self._current_length_m - target_length_m
        active_force_n = self._activation * p.max_force_per_fiber_n * p.bundle_count
        passive_force_n = max(0.0, p.passive_stiffness_n_per_m * length_error_m)
        damping_force_n = -p.damping_n_s_per_m * velocity_m_s
        total_force_n = max(0.0, active_force_n + passive_force_n + damping_force_n)

        current_contraction_strain = (p.rest_length_m - self._current_length_m) / p.rest_length_m

        return {
            "activation": self._activation,
            "target_contraction_strain": target_contraction_strain,
            "current_length_m": self._current_length_m,
            "current_contraction_strain": current_contraction_strain,
            "active_force_n": active_force_n,
            "passive_force_n": passive_force_n,
            "damping_force_n": damping_force_n,
            "total_force_n": total_force_n,
        }
