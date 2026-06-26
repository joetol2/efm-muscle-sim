"""
Parameter dataclasses for the electrofluidic fiber muscle simulation.

Public reference values are sourced from publicly available paper summaries and
the MIT news release. Placeholder values require fitting against experimental data
before use in hardware design or quantitative claims.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ElectroFluidicMuscleParams:
    """
    Parameters for a single electrofluidic fiber muscle bundle.

    Values marked PLACEHOLDER should be fitted from the Zenodo dataset or
    lab measurements before drawing quantitative conclusions.
    """

    # Public reference values from published paper summaries:
    max_contraction_strain: float = 0.20       # 20% strain (public reference)
    response_time_s: float = 0.30              # ~0.3 s response time constant (public reference)
    fiber_diameter_m: float = 0.002            # 2 mm reference fiber diameter (public reference)
    power_density_w_per_kg: float = 50.0       # 50 W/kg reference power density (public reference)

    # Geometry:
    rest_length_m: float = 0.10

    # Force and mechanical parameters -- PLACEHOLDER values:
    max_force_per_fiber_n: float = 1.0         # PLACEHOLDER -- fit from dataset
    bundle_count: int = 1
    passive_stiffness_n_per_m: float = 5.0     # PLACEHOLDER
    damping_n_s_per_m: float = 0.05            # PLACEHOLDER
    min_length_fraction: float = 0.75

    def __post_init__(self) -> None:
        if self.rest_length_m <= 0:
            raise ValueError("rest_length_m must be positive")
        if not 0.0 <= self.max_contraction_strain < 1.0:
            raise ValueError("max_contraction_strain must be in [0, 1)")
        if self.response_time_s <= 0:
            raise ValueError("response_time_s must be positive")
        if self.max_force_per_fiber_n < 0:
            raise ValueError("max_force_per_fiber_n must be non-negative")
        if self.bundle_count < 1:
            raise ValueError("bundle_count must be at least 1")
        if self.passive_stiffness_n_per_m < 0:
            raise ValueError("passive_stiffness_n_per_m must be non-negative")
        if self.damping_n_s_per_m < 0:
            raise ValueError("damping_n_s_per_m must be non-negative")
        if not 0.0 < self.min_length_fraction <= 1.0:
            raise ValueError("min_length_fraction must be in (0, 1]")


@dataclass
class AntagonisticJointParams:
    """
    Parameters for a one-degree-of-freedom antagonistic joint.

    Values are placeholders for a generic arm-scale joint. Adjust for
    specific hardware geometry before use in quantitative analysis.
    """

    moment_arm_m: float = 0.025           # PLACEHOLDER
    inertia_kg_m2: float = 0.015          # PLACEHOLDER
    joint_damping_n_m_s: float = 0.12     # PLACEHOLDER
    min_angle_rad: float = -0.35
    max_angle_rad: float = 2.25

    def __post_init__(self) -> None:
        if self.moment_arm_m <= 0:
            raise ValueError("moment_arm_m must be positive")
        if self.inertia_kg_m2 <= 0:
            raise ValueError("inertia_kg_m2 must be positive")
        if self.joint_damping_n_m_s < 0:
            raise ValueError("joint_damping_n_m_s must be non-negative")
        if self.min_angle_rad >= self.max_angle_rad:
            raise ValueError("min_angle_rad must be less than max_angle_rad")
