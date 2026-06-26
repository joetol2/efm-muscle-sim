# Repository handoff notes

This document is a plain-language orientation for taking over or continuing
work on this repository.

## What this repo is

efm-muscle-sim is a Python simulation package that models electrofluidic fiber
muscles as compliant linear actuators. The goal is to give you a way to test
how muscle-like actuation behaves in a robot arm or gripper simulation before
committing to hardware experiments.

It is based on the MIT / Politecnico di Bari electrofluidic fiber muscle research
(Science Robotics, DOI: 10.1126/scirobotics.ady6438). The package uses only public
information. It does not reproduce the internal pump, fluid circuit, or pressure
physics of the real system.

## What works right now

Install the package:

    pip install -e .

Run the demos:

    python examples/run_actuator_step_response.py
    python examples/run_antagonistic_joint_demo.py
    python examples/run_parameter_sweep.py

Each demo writes a CSV to outputs/ and a plot to plots/.

Run the test suite:

    pytest tests/ -v

All tests should pass. The test suite covers actuator behavior, joint dynamics,
parameter validation, and simulation output correctness.

## What does NOT work yet

The placeholder force and damping values have not been fitted to experimental data.
This means the simulation produces plausible motion behavior but the absolute force
and contraction numbers are not meaningful for hardware design.

The MuJoCo XML model is a mechanical approximation for the biceps/triceps arm
geometry. It has not been validated in a full simulation environment.

## First engineering task

Download the public Zenodo v2 dataset:

    python scripts/fetch_zenodo_dataset.py

The dataset is approximately 461 MB. It contains experimental measurements from
the original research. Use it to fit:

- max_force_per_fiber_n
- passive_stiffness_n_per_m
- damping_n_s_per_m
- response_time_s (for specific fiber conditions)

See docs/validation_plan.md for the step-by-step fitting process.

## File map for orientation

src/efm_muscle_sim/parameters.py
Start here. All tunable parameters are defined in ElectroFluidicMuscleParams
and AntagonisticJointParams. Placeholder values are labeled with PLACEHOLDER comments.

src/efm_muscle_sim/actuator.py
The ElectroFluidicMuscle class. Implements the step() method that advances the model
by one timestep and returns a state dictionary.

src/efm_muscle_sim/joint.py
The AntagonisticJoint class. Two muscles driving a hinge with a fixed moment arm.

examples/run_actuator_step_response.py
The simplest starting point for understanding what the model produces.

docs/engineering_notes.md
Explains the model chain and limitations in more detail.

docs/validation_plan.md
The step-by-step process for fitting parameters to experimental data.

## Questions to resolve

- What specific hardware configuration will this model be used for? Bundle count,
  fiber length, and target load will determine which experimental condition to fit.
- Is the goal to use this model for arm control, gripper design, or something else?
  This affects whether the joint model is the right abstraction or whether a
  different geometry is needed.
- Is MuJoCo the right downstream simulator, or is the Python model sufficient for
  the control work being planned?
