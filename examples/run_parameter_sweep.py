"""
Parameter sweep over bundle_count and max_force_per_fiber_n.

For each combination, runs a step response and records the peak force and
peak contraction strain. Writes a summary CSV to outputs/.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim import ElectroFluidicMuscle, ElectroFluidicMuscleParams

DT = 0.01
DURATION = 5.0
STEP_ON = 1.0
BUNDLE_COUNTS = [1, 2, 4, 8]
FORCE_VALUES = [0.5, 1.0, 2.0, 5.0]


def run_case(bundle_count: int, max_force: float) -> dict:  # type: ignore[type-arg]
    params = ElectroFluidicMuscleParams(
        rest_length_m=0.10,
        max_contraction_strain=0.20,
        response_time_s=0.30,
        max_force_per_fiber_n=max_force,
        bundle_count=bundle_count,
    )
    muscle = ElectroFluidicMuscle(params)
    steps = int(DURATION / DT)
    peak_force = 0.0
    peak_contraction = 0.0
    for i in range(steps):
        t = i * DT
        control = 1.0 if t >= STEP_ON else 0.0
        state = muscle.step(control, DT)
        if state["total_force_n"] > peak_force:
            peak_force = state["total_force_n"]
        if state["current_contraction_strain"] > peak_contraction:
            peak_contraction = state["current_contraction_strain"]
    return {
        "bundle_count": bundle_count,
        "max_force_per_fiber_n": max_force,
        "peak_force_n": round(peak_force, 6),
        "peak_contraction_strain": round(peak_contraction, 6),
    }


def main() -> None:
    results = []
    for bundle_count in BUNDLE_COUNTS:
        for max_force in FORCE_VALUES:
            row = run_case(bundle_count, max_force)
            results.append(row)
            print(
                f"bundles={bundle_count:2d}  force/fiber={max_force:.1f} N  "
                f"peak_force={row['peak_force_n']:.4f} N  "
                f"peak_strain={row['peak_contraction_strain']:.4f}"
            )

    out_path = ROOT / "outputs" / "parameter_sweep.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(results[0].keys())
    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Sweep CSV written: {out_path}")


if __name__ == "__main__":
    main()
