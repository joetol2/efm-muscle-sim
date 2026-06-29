# Quick Start

## Install

```
git clone https://github.com/joetol2/efm-muscle-sim.git
cd efm-muscle-sim
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

## Run the 2-DOF soft arm scripted demo

```
python examples/run_2dof_soft_arm_rollout.py
```

Expected output:

```
CSV written: outputs/efm_2dof_soft_arm_rollout.csv
Plot written: plots/efm_2dof_soft_arm_rollout.png
Final distance to target: 0.009 m at wrist (0.367, 0.244)
```

This runs a deterministic IK + PD controller (not a trained policy). It proves the two-joint arm, the muscle model, and the environment are all wired together.

## Run the 1-DOF actuator and joint demos

```
python examples/run_actuator_step_response.py
python examples/run_antagonistic_joint_demo.py
python examples/run_parameter_sweep.py
```

Each writes a CSV to `outputs/` and a plot to `plots/`.

## Train a policy with PPO

```
pip install gymnasium stable-baselines3
python examples/train_2dof_soft_arm_ppo.py
```

Writes `outputs/models/efm_2dof_soft_arm_ppo.zip` and an eval CSV.

## Render a rollout as a GIF

```
python examples/render_2dof_soft_arm_gif.py
```

Writes `plots/efm_2dof_soft_arm_rollout.gif`. Requires matplotlib only (no extra dependencies).

## Run the tests

```
pip install pytest
pytest tests/ -v
```

All 43 tests should pass.

## Repo layout

```
src/efm_muscle_sim/
    parameters.py       -- ElectroFluidicMuscleParams, AntagonisticJointParams
    actuator.py         -- ElectroFluidicMuscle (single bundle)
    joint.py            -- AntagonisticJoint (flexor/extensor pair)
    soft_arm.py         -- SoftArm2D (2-DOF planar arm)
    training_env.py     -- SoftArmReachEnv (Gymnasium environment)

examples/
    run_actuator_step_response.py       -- single muscle step response
    run_antagonistic_joint_demo.py      -- 1-DOF joint alternating control
    run_parameter_sweep.py              -- bundle count and force sweep
    run_2dof_soft_arm_rollout.py        -- 2-DOF scripted IK+PD demo
    render_2dof_soft_arm_gif.py         -- GIF renderer for the rollout
    train_2dof_soft_arm_ppo.py          -- PPO training with stable-baselines3

models/mujoco/
    efm_biceps_triceps_arm.xml          -- MuJoCo placeholder arm (gain = placeholder)

docs/
    mujoco_integration.md               -- how to wire Python model to MuJoCo
    2dof_soft_arm_training_demo.md      -- full 2-DOF engineering writeup
    repo_handoff.md                     -- engineer orientation doc

tests/                                  -- 43 pytest tests
outputs/                                -- CSV outputs (git-ignored)
plots/                                  -- plot and GIF outputs (git-ignored)
```

## What the values mean

The contraction strain (20%), response time (0.3 s), fiber diameter (2 mm), and power density (50 W/kg) come from the published paper. Force, stiffness, and damping are placeholders -- see `src/efm_muscle_sim/parameters.py` for which values need fitting and `scripts/fit_parameters.py` for the fitting workflow once you have the Zenodo dataset.
