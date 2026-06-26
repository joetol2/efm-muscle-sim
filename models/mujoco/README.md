# MuJoCo models

## efm_biceps_triceps_arm.xml

A mechanical approximation of a biceps/triceps style arm driven by two
electrofluidic fiber muscle style actuators.

This model is a placeholder for concept exploration. It is not a reconstruction
of the MIT experimental hardware, calibration setup, or tendon routing.

### What the model contains

- Upper arm and forearm bodies connected by a hinge joint (elbow)
- Spatial tendons connecting muscle origin sites to insertion sites
- Two general actuators with first-order filter dynamics approximating 0.3 s
  response time
- Joint range limited to -20 to 130 degrees

### Known limitations

The actuator gain (gainprm="30") is a placeholder. It should be updated after
fitting the Python ElectroFluidicMuscle model to experimental data from the
Zenodo dataset and converting fitted force values to MuJoCo actuator units.

Moment arm geometry is a fixed-site approximation. Real tendon wrapping and
variable moment arm effects are not modeled.

### Requirements

MuJoCo 2.3 or later. Install with:

    pip install mujoco

### Quick test

    python examples/run_mujoco_loader.py
