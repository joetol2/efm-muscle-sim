# efm-muscle-sim

Independent behavioral simulation abstraction for electrofluidic fiber muscle style actuation.

## What this is

This repository contains an independent behavioral simulation abstraction for electrofluidic fiber muscle style actuation. It is not an official model from MIT, Politecnico di Bari, Science Robotics, or the original authors. It does not reproduce the full electrofluidic pump, fluid circuit, pressure, cavitation, or material behavior of the published actuator.

The package models each muscle bundle as a compliant linear actuator with:

- first-order activation lag
- contraction strain bounded by a configurable maximum
- force scaling by bundle count
- passive spring stiffness
- velocity damping

It provides an antagonistic joint model that drives a one-degree-of-freedom hinge with opposing flexor and extensor muscles.

## What this is NOT

This is not a validated physical model. It does not simulate:

- electrohydrodynamic pump charge injection
- dielectric fluid pressure dynamics
- cavitation or pre-pressurization effects
- McKibben actuator wall mechanics
- thermal behavior or material fatigue
- the sealed fluid circuit behavior described in the original research

Do not use default parameter values for hardware design, safety analysis, or quantitative performance claims. Default force and damping values are placeholders requiring fitting against experimental data.

## Installation

```
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the optional MuJoCo example:

```
pip install mujoco
```

## Quick start

```python
from efm_muscle_sim import ElectroFluidicMuscle, ElectroFluidicMuscleParams

params = ElectroFluidicMuscleParams(bundle_count=4, max_force_per_fiber_n=1.0)
muscle = ElectroFluidicMuscle(params)

for _ in range(100):
    state = muscle.step(control=1.0, dt=0.01)

print(state["activation"])
print(state["current_contraction_strain"])
print(state["total_force_n"])
```

## Run the demos

Step response for a single bundle:

```
python examples/run_actuator_step_response.py
```

Flex/extend cycle for an antagonistic joint:

```
python examples/run_antagonistic_joint_demo.py
```

Parameter sweep over bundle count and force:

```
python examples/run_parameter_sweep.py
```

Outputs are written to `outputs/` (CSV) and `plots/` (PNG).

## Run tests

```
pytest tests/ -v
```

## Data sources

Primary paper:
Science Robotics, DOI: 10.1126/scirobotics.ady6438

MIT News:
https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Public Zenodo v2 dataset (not bundled, ~461 MB):
https://zenodo.org/records/18678491

To download the dataset locally:

```
python scripts/fetch_zenodo_dataset.py
```

See NOTICE.md for attribution and non-affiliation details.

## License

MIT. See LICENSE.
