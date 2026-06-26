"""
Plotting utilities for simulation outputs.

All functions save PNG files to disk and do not display windows. This avoids
display dependencies in headless environments.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict


def plot_actuator_response(
    history: List[Dict[str, float]],
    output_path: Path,
    title: str = "Actuator Step Response",
) -> None:
    """
    Plot activation, contraction strain, and total force over time.

    Parameters
    ----------
    history:
        Output from run_simulation() for a single actuator.
    output_path:
        PNG file path to write. Parent directories are created if needed.
    title:
        Figure title string.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    time = [row["time_s"] for row in history]
    activation = [row["activation"] for row in history]
    contraction = [row["current_contraction_strain"] for row in history]
    force = [row["total_force_n"] for row in history]
    control = [row.get("control", 0.0) for row in history]

    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    fig.suptitle(title, fontsize=12)

    axes[0].plot(time, control, color="grey", linestyle="--", label="control command")
    axes[0].plot(time, activation, color="steelblue", label="activation")
    axes[0].set_ylabel("Activation")
    axes[0].set_ylim(-0.05, 1.1)
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(time, contraction, color="darkorange")
    axes[1].set_ylabel("Contraction strain")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(time, force, color="crimson")
    axes[2].set_ylabel("Total force (N)")
    axes[2].set_xlabel("Time (s)")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)


def plot_joint_response(
    history: List[Dict[str, float]],
    output_path: Path,
    title: str = "Antagonistic Joint Response",
) -> None:
    """
    Plot joint angle, angular velocity, and muscle activations over time.

    Parameters
    ----------
    history:
        Output from run_simulation() for an antagonistic joint.
    output_path:
        PNG file path to write. Parent directories are created if needed.
    title:
        Figure title string.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    time = [row["time_s"] for row in history]
    angle_deg = [row["angle_deg"] for row in history]
    ang_vel = [row["angular_velocity_rad_s"] for row in history]
    flex_act = [row["flex_activation"] for row in history]
    ext_act = [row["ext_activation"] for row in history]

    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    fig.suptitle(title, fontsize=12)

    axes[0].plot(time, angle_deg, color="steelblue")
    axes[0].set_ylabel("Joint angle (deg)")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(time, ang_vel, color="darkorange")
    axes[1].set_ylabel("Angular velocity (rad/s)")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(time, flex_act, color="crimson", label="flexor")
    axes[2].plot(time, ext_act, color="seagreen", label="extensor")
    axes[2].set_ylabel("Activation")
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylim(-0.05, 1.1)
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
