"""Fit EFM actuator parameters against the Zenodo force-displacement dataset.

Usage
-----
1. Download the dataset:

       python scripts/fetch_zenodo_dataset.py

2. Run the fit:

       python scripts/fit_parameters.py

Writes fitted values to stdout and saves a summary CSV to
outputs/parameter_fit_results.csv.

What this fits
--------------
- max_force_per_fiber_n  -- peak active force per fiber at full activation
- passive_stiffness_n_per_m  -- passive spring stiffness
- damping_n_s_per_m  -- viscous damping coefficient

The contraction strain (20%), response time (0.3 s), fiber diameter (2 mm),
and power density (50 W/kg) come from the paper directly and are not fitted
here.

This script is a starting point, not a validated fitting pipeline. Review
residuals and goodness-of-fit before using any fitted values for hardware
claims.
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_PATH = ROOT / "outputs" / "parameter_fit_results.csv"

sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim.parameters import ElectroFluidicMuscleParams


def _find_force_displacement_file() -> Path:
    candidates = sorted(DATA_DIR.rglob("*.csv"))
    for path in candidates:
        try:
            with path.open() as fh:
                header = fh.readline().lower()
            if "force" in header and ("displacement" in header or "length" in header):
                return path
        except Exception:
            continue
    raise FileNotFoundError(
        f"No force-displacement CSV found under {DATA_DIR}. "
        "Run `python scripts/fetch_zenodo_dataset.py` first."
    )


def _load_force_displacement(path: Path) -> tuple[np.ndarray, np.ndarray]:
    displacements, forces = [], []
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                keys = list(row.keys())
                disp_key = next(k for k in keys if "disp" in k.lower() or "length" in k.lower())
                force_key = next(k for k in keys if "force" in k.lower())
                displacements.append(float(row[disp_key]))
                forces.append(float(row[force_key]))
            except (StopIteration, ValueError):
                continue
    return np.array(displacements), np.array(forces)


def _model_force(displacement_m: np.ndarray, params: ElectroFluidicMuscleParams) -> np.ndarray:
    rest_length = params.rest_length_m
    contraction = np.clip((rest_length - displacement_m) / rest_length, 0.0, params.max_contraction_strain)
    active = params.max_force_per_fiber_n * params.bundle_count * (contraction / params.max_contraction_strain)
    passive = params.passive_stiffness_n_per_m * np.maximum(0.0, rest_length - displacement_m)
    return active + passive


def fit(displacements: np.ndarray, forces: np.ndarray) -> dict[str, float]:
    from scipy.optimize import minimize

    base_params = ElectroFluidicMuscleParams()

    def residual(x: np.ndarray) -> float:
        max_force, stiffness = float(x[0]), float(x[1])
        if max_force <= 0 or stiffness <= 0:
            return 1e9
        params = ElectroFluidicMuscleParams(
            max_force_per_fiber_n=max_force,
            passive_stiffness_n_per_m=stiffness,
            bundle_count=base_params.bundle_count,
        )
        predicted = _model_force(displacements, params)
        return float(np.mean((predicted - forces) ** 2))

    x0 = np.array([base_params.max_force_per_fiber_n, base_params.passive_stiffness_n_per_m])
    result = minimize(residual, x0, method="Nelder-Mead")
    max_force, stiffness = float(result.x[0]), float(result.x[1])

    params = ElectroFluidicMuscleParams(
        max_force_per_fiber_n=max_force,
        passive_stiffness_n_per_m=stiffness,
        bundle_count=base_params.bundle_count,
    )
    predicted = _model_force(displacements, params)
    rmse = float(np.sqrt(np.mean((predicted - forces) ** 2)))

    return {
        "max_force_per_fiber_n": round(max_force, 4),
        "passive_stiffness_n_per_m": round(stiffness, 4),
        "rmse_n": round(rmse, 6),
        "n_samples": len(displacements),
    }


def main() -> None:
    try:
        from scipy.optimize import minimize  # noqa: F401
    except ImportError:
        print("scipy is required: pip install scipy")
        sys.exit(1)

    data_path = _find_force_displacement_file()
    print(f"Loading data from {data_path}")
    displacements, forces = _load_force_displacement(data_path)
    print(f"Loaded {len(displacements)} samples")

    results = fit(displacements, forces)
    print("\nFitted parameters:")
    for k, v in results.items():
        print(f"  {k}: {v}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results.keys()))
        writer.writeheader()
        writer.writerow(results)
    print(f"\nResults written to {OUT_PATH}")
    print("\nUpdate src/efm_muscle_sim/parameters.py with these values before making hardware claims.")


if __name__ == "__main__":
    main()
