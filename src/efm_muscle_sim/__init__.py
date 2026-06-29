"""
efm_muscle_sim: behavioral simulation for electrofluidic fiber muscle style actuation.

This package provides a system-level abstraction. It does not reproduce the
internal electrofluidic pump, fluid circuit, pressure, cavitation, or material
behavior of the published actuator.

Core classes
------------
ElectroFluidicMuscle        single bundle actuator model
AntagonisticJoint           two-muscle antagonistic joint model
ElectroFluidicMuscleParams  actuator parameter dataclass
AntagonisticJointParams     joint parameter dataclass

2-DOF soft arm (no optional dependencies required)
--------------------------------------------------
SoftArm2D           planar two-link arm with shoulder and elbow antagonistic joints
SoftArm2DParams     geometry and joint settings for the arm

Training environment (requires gymnasium)
-----------------------------------------
SoftArmReachEnv         Gymnasium-compatible reaching task
SoftArmReachTaskParams  task configuration dataclass

SoftArmReachEnv is imported lazily. If gymnasium is not installed, importing
it directly will raise ImportError with install instructions.

Simulation utilities
--------------------
run_simulation  drive a model through a control sequence
save_csv        write state history to CSV

Plotting
--------
plot_actuator_response  activation, contraction, force over time
plot_joint_response     angle, angular velocity, activations over time
"""

from .actuator import ElectroFluidicMuscle
from .joint import AntagonisticJoint
from .parameters import AntagonisticJointParams, ElectroFluidicMuscleParams
from .plotting import plot_actuator_response, plot_joint_response
from .simulation import run_simulation, save_csv
from .soft_arm import SoftArm2D, SoftArm2DParams
from .units import deg_to_rad, kgf_to_n, m_to_mm, mm_to_m, n_to_kgf, rad_to_deg

__version__ = "0.2.0"

__all__ = [
    "ElectroFluidicMuscle",
    "AntagonisticJoint",
    "ElectroFluidicMuscleParams",
    "AntagonisticJointParams",
    "SoftArm2D",
    "SoftArm2DParams",
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

def _import_training():
    """Lazy import for gymnasium-dependent training classes."""
    try:
        from .training_env import SoftArmReachEnv, SoftArmReachTaskParams
        return SoftArmReachEnv, SoftArmReachTaskParams
    except ImportError:
        raise ImportError(
            "SoftArmReachEnv requires gymnasium. Install it with:\n"
            "  pip install gymnasium"
        )
