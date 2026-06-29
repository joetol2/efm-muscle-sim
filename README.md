# efm-muscle-sim

A Python simulation of electrofluidic fiber muscle (EFM) style actuation for robotics concept work.

Not affiliated with MIT, Politecnico di Bari, Science Robotics, or the original paper authors. This is an independent abstraction built from public information in the paper and MIT news release.

## What it models

Each muscle bundle is treated as a compliant linear actuator with first-order activation lag. You set a control input between 0 and 1, and the model handles contraction rate, force output, passive compliance, and damping. Two muscles in opposition drive a single-joint arm model.

It does not simulate pump internals, fluid pressure, cavitation, or material deformation. The force and damping values are placeholders until someone fits them against the public Zenodo dataset.

## 2-DOF soft arm extension

A two-joint planar arm -- shoulder and elbow -- each driven by an opposing muscle pair, built on top of the same actuator and joint model above. A scripted controller uses inverse kinematics and PD control to reach a target, and a Gymnasium-compatible environment is included for RL training.

This is a simulation and training prototype, not a validated physical simulator. See `docs/2dof_soft_arm_training_demo.md` for the full writeup.

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the optional MuJoCo example:

```
pip install mujoco
```

For the optional 2-DOF PPO training example:

```
pip install gymnasium stable-baselines3
```

## Running the demos

**1-DOF actuator and joint demos**

```
python examples/run_actuator_step_response.py
python examples/run_antagonistic_joint_demo.py
python examples/run_parameter_sweep.py
```

Each script writes a CSV to `outputs/` and a plot to `plots/`. The parameter sweep runs bundle count and force combinations and shows how much the output changes across placeholder assumptions.

**2-DOF soft arm scripted rollout**

```
python examples/run_2dof_soft_arm_rollout.py
```

Writes `outputs/efm_2dof_soft_arm_rollout.csv` and `plots/efm_2dof_soft_arm_rollout.png`. The wrist reaches within 0.009 m of the target in under 300 steps.

**2-DOF soft arm PPO training**

```
python examples/train_2dof_soft_arm_ppo.py
```

Writes a trained policy to `outputs/models/efm_2dof_soft_arm_ppo.zip` and an eval CSV.

**Tests**

```
pytest tests/ -v
```

## Using the Python model directly

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

## MuJoCo

The XML model is at `models/mujoco/efm_biceps_triceps_arm.xml`. It loads and runs, but the actuator gain is a placeholder and the Python model is not yet wired to it. Before using this in a real sim, read `docs/mujoco_integration.md` -- it covers what the gain represents, how to update it after fitting, and how to wire a controller.

## Simulation outputs

**MuJoCo placeholder arm** -- upper arm and forearm as capsules, hinge elbow joint, with flexor (orange) and extensor (yellow) tendons shown at 65 degrees bend. Gain values are placeholders pending parameter fitting.

![MuJoCo arm schematic](docs/images/mujoco_arm_render.png)

**Single muscle step response** -- activation builds with the 0.3 s lag, contraction strain follows, normalized force tracks activation.

![Step response](docs/images/efm_actuator_step_response.png)

**Antagonistic joint demo** -- flexor and extensor activations alternate to bend and release the joint. Joint angle shown in degrees alongside each muscle activation level.

![Antagonistic joint demo](docs/images/efm_antagonistic_joint_demo.png)

**2-DOF soft arm model diagram** -- observation, action, and reward structure for the reaching environment.

![2-DOF arm model diagram](docs/images/efm_2dof_soft_arm_model_diagram.png)

**2-DOF soft arm geometry** -- shoulder and elbow joints, link lengths, and wrist endpoint.

![2-DOF arm render](docs/images/efm_2dof_soft_arm_model_render.png)

**Concept render** -- 3D illustration for presentation context only. Not a photo of hardware and not a validated physical result.

![Concept render](docs/images/robotic_arm_on_sleek_tabletop.png)

## Parameters

The contraction strain (20%), response time (0.3 s), fiber diameter (2 mm), and power density (50 W/kg) come from the public paper summary. Force, stiffness, and damping are placeholders. See `src/efm_muscle_sim/parameters.py` for the full list with comments on which values need fitting.

## Data sources

Science Robotics, DOI: 10.1126/scirobotics.ady6438

MIT News: https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Zenodo v2 dataset (~461 MB): https://zenodo.org/records/18678491

Download the dataset locally with `python scripts/fetch_zenodo_dataset.py`. Do not commit it to the repo.

See NOTICE.md for attribution and non-affiliation details.
