# efm-muscle-sim

A Python simulation of electrofluidic fiber muscle (EFM) style actuation for robotics concept work.

Not affiliated with MIT, Politecnico di Bari, Science Robotics, or the original paper authors. This is an independent abstraction built from public information in the paper and MIT news release.

## 2-DOF soft arm training demo

![2-DOF arm model diagram](docs/images/efm_2dof_soft_arm_model_diagram.png)

A two-joint planar arm -- shoulder and elbow -- each driven by an opposing pair of EFM muscles, built directly on top of the actuator and joint model described below. Instead of a single actuator moving in isolation, four muscles coordinate through two joints to move a wrist endpoint toward a target.

This is a simulation and training prototype. It proves the actuator model is wired into trainable, visible behavior. It does not turn the EFM model into a validated physical simulator, and the concept render further down is for presentation context only, not hardware.

**Geometry.** Two rigid links (0.30 m upper arm, 0.24 m forearm) connected by a shoulder joint and an elbow joint. Each joint has its own moment arm, inertia, and damping, and is driven by a flexor/extensor muscle pair using the same `AntagonisticJoint` model used in the 1-DOF demo.

**Control interface.** A 4-value action in [0, 1]: `[shoulder_flex, shoulder_extend, elbow_flex, elbow_extend]`. Co-contracting both muscles in a pair stiffens the joint without necessarily moving it, the same way it would on the physical actuator.

**Training environment.** `SoftArmReachEnv` is a Gymnasium-compatible environment with:
- a 16-value observation: joint angles, joint velocities, wrist position, target position, position error, contact force, and all four muscle activation levels
- a reward that combines distance to target, a velocity penalty, an action-effort penalty, and a co-contraction penalty, with a bonus for holding the target
- optional dynamics randomization (muscle response time, max force, stiffness, damping) so a trained policy is not overfit to one fixed actuator
- optional contact, modeled as a spring-damper wall, so the arm can be trained against pushback at the endpoint, not just free-space reaching

**Scripted demo result.** A deterministic inverse-kinematics-plus-PD controller (not a trained policy, just a smoke test) reaches within 0.009 m of the target in under 300 simulation steps.

### Run the scripted rollout

```
pip install -e .
python examples/run_2dof_soft_arm_rollout.py
```

Writes `outputs/efm_2dof_soft_arm_rollout.csv` and `plots/efm_2dof_soft_arm_rollout.png`.

### Train a policy with PPO

```
pip install gymnasium stable-baselines3
python examples/train_2dof_soft_arm_ppo.py
```

Writes a trained policy to `outputs/models/efm_2dof_soft_arm_ppo.zip` and an evaluation CSV.

Full writeup, including the engineering caveats on what still needs fitting before this touches hardware claims: `docs/2dof_soft_arm_training_demo.md`.

**2-DOF soft arm geometry** -- shoulder and elbow joints, link lengths, and wrist endpoint.

![2-DOF arm render](docs/images/efm_2dof_soft_arm_model_render.png)

**Concept render** -- 3D illustration for presentation context only. Not a photo of hardware and not a validated physical result.

![Concept render](docs/images/robotic_arm_on_sleek_tabletop.png)

---

## What it models

Each muscle bundle is treated as a compliant linear actuator with first-order activation lag. You set a control input between 0 and 1, and the model handles contraction rate, force output, passive compliance, and damping. Two muscles in opposition drive a single-joint arm model.

It does not simulate pump internals, fluid pressure, cavitation, or material deformation. The force and damping values are placeholders until someone fits them against the public Zenodo dataset.

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

**Tests**

```
pytest tests/ -v
```

43 tests cover the actuator, joint, parameters, simulation outputs, and the 2-DOF arm and environment.

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

**MuJoCo placeholder arm** -- upper arm and forearm as capsules, hinge elbow joint, with flexor (orange) and extensor (yellow) tendons shown at 65 degrees bend. Gain values are placeholders pending parameter fitting.

![MuJoCo arm schematic](docs/images/mujoco_arm_render.png)

## Simulation outputs

**Single muscle step response** -- activation builds with the 0.3 s lag, contraction strain follows, normalized force tracks activation.

![Step response](docs/images/efm_actuator_step_response.png)

**Antagonistic joint demo** -- flexor and extensor activations alternate to bend and release the joint. Joint angle shown in degrees alongside each muscle activation level.

![Antagonistic joint demo](docs/images/efm_antagonistic_joint_demo.png)

## Parameters

The contraction strain (20%), response time (0.3 s), fiber diameter (2 mm), and power density (50 W/kg) come from the public paper summary. Force, stiffness, and damping are placeholders. See `src/efm_muscle_sim/parameters.py` for the full list with comments on which values need fitting.

## Data sources

Science Robotics, DOI: 10.1126/scirobotics.ady6438

MIT News: https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Zenodo v2 dataset (~461 MB): https://zenodo.org/records/18678491

Download the dataset locally with `python scripts/fetch_zenodo_dataset.py`. Do not commit it to the repo.

See NOTICE.md for attribution and non-affiliation details.
