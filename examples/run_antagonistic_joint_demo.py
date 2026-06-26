"""
Antagonistic joint demo: flex/extend cycle.

Drives the flexor and extensor in alternating phases to show joint oscillation.
Writes state history to outputs/ and a plot to plots/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim import (
    AntagonisticJoint,
    AntagonisticJointParams,
    ElectroFluidicMuscleParams,
    plot_joint_response,
    run_simulation,
    save_csv,
)

DT = 0.01
DURATION = 8.0


def build_phase_sequence(duration: float, dt: float) -> list[tuple[float, float]]:
    """Return (flex_ctrl, extend_ctrl) pairs for a flex/neutral/extend/neutral cycle."""
    steps = int(duration / dt)
    phase_len = steps // 4
    pairs = []
    for i in range(steps):
        phase = i // phase_len
        if phase == 0:
            pairs.append((0.8, 0.0))   # flex
        elif phase == 1:
            pairs.append((0.0, 0.0))   # relax
        elif phase == 2:
            pairs.append((0.0, 0.8))   # extend
        else:
            pairs.append((0.0, 0.0))   # relax
    return pairs


def main() -> None:
    muscle_params = ElectroFluidicMuscleParams(
        rest_length_m=0.10,
        max_contraction_strain=0.20,
        response_time_s=0.30,
        max_force_per_fiber_n=1.0,
        bundle_count=4,
    )
    joint_params = AntagonisticJointParams(
        moment_arm_m=0.025,
        inertia_kg_m2=0.015,
        joint_damping_n_m_s=0.12,
    )
    joint = AntagonisticJoint.from_params(muscle_params, joint_params)

    phases = build_phase_sequence(DURATION, DT)

    def step_fn(ctrl_pair: tuple[float, float]) -> dict:  # type: ignore[type-arg]
        return joint.step(ctrl_pair[0], ctrl_pair[1], DT)

    history = run_simulation(
        step_fn=step_fn,
        control_sequence=phases,
        dt=DT,
    )

    out_csv = ROOT / "outputs" / "efm_antagonistic_joint_demo.csv"
    out_png = ROOT / "plots" / "efm_antagonistic_joint_demo.png"

    save_csv(history, out_csv)
    print(f"CSV written: {out_csv}")

    plot_joint_response(history, out_png, title="Antagonistic Joint Flex/Extend Cycle")
    print(f"Plot written: {out_png}")

    final = history[-1]
    print(
        f"Final state: angle={final['angle_deg']:.2f} deg  "
        f"flex_act={final['flex_activation']:.3f}  "
        f"ext_act={final['ext_activation']:.3f}"
    )


if __name__ == "__main__":
    main()
