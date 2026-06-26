"""
Step-response demo for a single electrofluidic fiber muscle bundle.

Applies a step command at t=1 s and holds until t=4 s, then releases.
Writes state history to outputs/ and a plot to plots/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim import (
    ElectroFluidicMuscle,
    ElectroFluidicMuscleParams,
    plot_actuator_response,
    run_simulation,
    save_csv,
)

DT = 0.01          # seconds per step
DURATION = 6.0     # total simulation time in seconds
STEP_ON = 1.0      # time when step command goes to 1.0
STEP_OFF = 4.0     # time when step command returns to 0.0


def build_control_sequence() -> list[float]:
    steps = int(DURATION / DT)
    controls = []
    for i in range(steps):
        t = i * DT
        if STEP_ON <= t < STEP_OFF:
            controls.append(1.0)
        else:
            controls.append(0.0)
    return controls


def main() -> None:
    params = ElectroFluidicMuscleParams(
        rest_length_m=0.10,
        max_contraction_strain=0.20,
        response_time_s=0.30,
        max_force_per_fiber_n=1.0,
        bundle_count=4,
        passive_stiffness_n_per_m=5.0,
        damping_n_s_per_m=0.05,
    )
    muscle = ElectroFluidicMuscle(params)

    controls = build_control_sequence()
    history = run_simulation(
        step_fn=lambda ctrl: muscle.step(ctrl, DT),
        control_sequence=controls,
        dt=DT,
    )

    out_csv = ROOT / "outputs" / "efm_actuator_step_response.csv"
    out_png = ROOT / "plots" / "efm_actuator_step_response.png"

    save_csv(history, out_csv)
    print(f"CSV written: {out_csv}")

    plot_actuator_response(history, out_png, title="EFM Actuator Step Response")
    print(f"Plot written: {out_png}")

    final = history[-1]
    print(
        f"Final state: activation={final['activation']:.3f}  "
        f"contraction_strain={final['current_contraction_strain']:.4f}  "
        f"force={final['total_force_n']:.4f} N"
    )


if __name__ == "__main__":
    main()
