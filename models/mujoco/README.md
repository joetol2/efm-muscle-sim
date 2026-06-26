# MuJoCo models

## efm_biceps_triceps_arm.xml

A mechanical approximation of a biceps/triceps style arm driven by two electrofluidic fiber muscle style actuators.

This is a placeholder for concept exploration. It is not a reconstruction of the MIT experimental hardware, calibration setup, or tendon routing.

### What the model contains

- Upper arm and forearm bodies connected by a hinge joint (elbow)
- Spatial tendons connecting muscle origin sites to insertion sites
- Two general actuators with first-order filter dynamics approximating 0.3 s response time
- Joint range limited to -20 to 130 degrees

### Known gaps before real use

The actuator gain (`gainprm="30"`) is a placeholder. It should be updated after fitting the Python `ElectroFluidicMuscle` model to experimental data and computing the equivalent MuJoCo force gain.

Moment arm geometry uses fixed site positions. Variable moment arm effects are not modeled.

Body mass and inertia are derived from MuJoCo density defaults, not from any specific robot hardware.

For a full walkthrough of what to do before integrating this into a real simulation, see `docs/mujoco_integration.md`.

### Requirements

MuJoCo 2.3 or later:

```
pip install mujoco
```

### Quick load test

```
python examples/run_mujoco_loader.py
```
