# Future work

This document lists known gaps and potential extensions to the simulation package.

## Parameter fitting

The most immediate priority is fitting the placeholder parameter values against
the public Zenodo dataset. Until this is done, force and contraction outputs are
not quantitatively meaningful. See docs/validation_plan.md for the process.

## Nonlinear force model

The current active force model is linear in activation. Published data on
pneumatic artificial muscles and compliant actuators generally shows nonlinear
force-length relationships. A more accurate model might use:

- a Hill-type force-velocity curve
- a contraction-dependent stiffness term
- separate activation and deactivation time constants

These additions should be based on fitted experimental data rather than assumed.

## Variable moment arm

The antagonistic joint model uses a constant moment arm. A more accurate joint
model would use angle-dependent moment arm geometry derived from the actual tendon
routing in the target hardware.

## Multi-joint simulation

The current model supports a single joint. Extension to a multi-joint arm or
gripper would require chaining joint models and propagating forces through a
kinematic chain. This is a significant architectural addition.

## MuJoCo integration

The MuJoCo XML model is a mechanical approximation. Useful next steps:

- validate the elbow joint range and tendon geometry against the target hardware
- tune the actuator gain parameters (gainprm) to match fitted force values
- add a contact model if gripper or manipulation simulations are planned

## Data inspection tooling

scripts/inspect_dataset_placeholder.py is a stub. It should be developed into
a tool that parses the Zenodo dataset format, plots raw experimental curves, and
exports reference curves for parameter fitting comparison.

## Packaging and distribution

The package is currently installed in editable mode only. If distribution is
needed, consider:

- adding version metadata and a changelog
- setting up a CI workflow for automated testing
- publishing to PyPI if external collaborators need to install it
