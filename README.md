# efm-muscle-sim

A Python simulation of electrofluidic fiber muscle (EFM) style actuation for robotics concept work.

**New here? Start with [QUICKSTART.md](QUICKSTART.md).**

Not affiliated with MIT, Politecnico di Bari, Science Robotics, or the original paper authors. This is an independent abstraction built from public information in the paper and MIT news release.

---

## 2-DOF soft arm training demo

![2-DOF arm model diagram](docs/images/efm_2dof_soft_arm_model_diagram.png)

A two-joint planar arm -- shoulder and elbow -- each driven by an opposing pair of EFM muscles, built directly on top of the actuator and joint model below. Instead of a single actuator moving in isolation, four muscles coordinate through two joints to move a wrist endpoint toward a target.

This is a simulation and training prototype, not a validated physical simulator. The concept render below is for presentation context only, not hardware.

**Geometry.** Two rigid links (0.30 m upper arm, 0.24 m forearm) connected at shoulder and elbow joints. Each joint has its own moment arm, inertia, and damping, and is driven by a flexor/extensor muscle pair using the same `AntagonisticJoint` model as the 1-DOF demo.

**Control interface.** A 4-value action in [0, 1]: `[shoulder_flex, shoulder_extend, elbow_flex, elbow_extend]`. Co-contracting both muscles in a pair stiffens the joint without moving it, matching physical actuator behavior.

**Training environment.** `SoftArmReachEnv` is a Gymnasium-compatible environment with:
- a 16-value observation: joint angles, joint velocities, wrist position, target position, position error, contact force, and all four muscle activation levels
- a reward combining distance to target, velocity penalty, action-effort penalty, and co-contraction penalty, with a bonus for holding the target
- optional dynamics randomization (response time, max force, stiffness, damping) to avoid overfitting to a single fixed actuator
- optional contact wall modeled as a spring-damper, for training against endpoint pushback

**Scripted demo result.** A deterministic IK + PD controller reaches within 0.009 m of the target in under 300 steps.

![2-DOF soft arm rollout](docs/images/efm_2dof_soft_arm_rollout.gif)

**2-DOF arm geometry** -- shoulder and elbow joints, link lengths, and wrist endpoint.

![2-DOF arm render](docs/images/efm_2dof_soft_arm_model_render.png)

**Concept render** -- 3D illustration for presentation context only. Not a photo of hardware.

![Concept render](docs/images/robotic_arm_on_sleek_tabletop.png)

Full engineering writeup: `docs/2dof_soft_arm_training_demo.md`

---

## What it models

Each muscle bundle is a compliant linear actuator with first-order activation lag. You set a control input between 0 and 1, and the model handles contraction rate, force output, passive compliance, and damping. Two muscles in opposition drive a single-joint arm model.

It does not simulate pump internals, fluid pressure, cavitation, or material deformation. Force and damping values are placeholders until fitted against the Zenodo dataset (`scripts/fit_parameters.py`).

## Setup

```
git clone https://github.com/joetol2/efm-muscle-sim.git
cd efm-muscle-sim
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Optional extras:

```
pip install mujoco                          # MuJoCo example
pip install gymnasium stable-baselines3     # PPO training
pip install scipy                           # parameter fitting
```

See [QUICKSTART.md](QUICKSTART.md) for run commands, expected outputs, and the full repo layout.

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

The XML model is at `models/mujoco/efm_biceps_triceps_arm.xml`. It loads and runs, but the actuator gain is a placeholder and the Python model is not yet wired to it. Read `docs/mujoco_integration.md` before using this in a real sim -- it covers gain calculation, controller wiring, and what still needs fitting.

![MuJoCo placeholder arm](docs/images/mujoco_arm_render.png)

## Simulation outputs

**Single muscle step response** -- activation builds with the 0.3 s lag, contraction strain follows, force tracks activation.

![Step response](docs/images/efm_actuator_step_response.png)

**Antagonistic joint demo** -- flexor and extensor activations alternate to bend and release the joint.

![Antagonistic joint demo](docs/images/efm_antagonistic_joint_demo.png)

## Parameters

Contraction strain (20%), response time (0.3 s), fiber diameter (2 mm), and power density (50 W/kg) come from the published paper. Force, stiffness, and damping are placeholders. See `src/efm_muscle_sim/parameters.py` for the full list and `scripts/fit_parameters.py` for the fitting workflow.

## Data sources

Science Robotics, DOI: 10.1126/scirobotics.ady6438

MIT News: https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Zenodo v2 dataset (~461 MB): https://zenodo.org/records/18678491

Download locally with `python scripts/fetch_zenodo_dataset.py`. Do not commit it to the repo.

See NOTICE.md for attribution and non-affiliation details.
