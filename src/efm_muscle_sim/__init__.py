"""
efm_muscle_sim -- behavioral simulation for electrofluidic fiber muscle style actuation.

This package provides a system-level abstraction. It does not reproduce the
internal electrofluidic pump, fluid circuit, pressure, cavitation, or material
behavior of the published actuator.

Main classes
------------
ElectroFluidicMuscle  -- single bundle actuator model
AntagonisticJoint     -- two-muscle antagonistic joint model
ElectroFluidicMuscleParams  -- actuator parameter dataclass
AntagonisticJointParams     -- joint parameter dataclass

Simulation utilities
--------------------
run_simulation  -- drive a model through a control sequence
save_csv        -- write state history to CSV

Plotting
--------
plot_actuator_response  -- activation, contraction, force over time
plot_joint_response     -- angle, angular velocity, activations over time
"""

from .actuator import ElectroFluidicMuscle
from .joint import AntagonisticJoint
from .parameters import AntagonisticJointParams, ElectroFluidicMuscleParams
from .plotting import plot_actuator_response, plot_joint_response
from .simulation import run_simulation, save_csv
from .units import deg_to_rad, kgf_to_n, m_to_mm, mm_to_m, n_to_kgf, rad_to_deg

__version__ = "0.1.0"

__all__ = [
    "ElectroFluidicMuscle",
    "AntagonisticJoint",
    "ElectroFluidicMuscleParams",
    "AntagonisticJointParams",
    "run_simulation",
    "save_csv",
    "plot_actuator_response",
    "plot_joint_response",
    "rad_to_deg",
    "deg_to_rad",
    "n_to_kgf",
    "kgf_to_n",
    "m_to_mm",
    "mm_to_m",
]
