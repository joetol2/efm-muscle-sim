# Engineering notes

## Intended use

This package models electrofluidic fiber muscles as a system-level actuator abstraction.
It is appropriate for early robotics simulation, control architecture sketches, and
design feasibility discussion. It is not a fluid solver, electrohydrodynamic pump
model, cavitation model, CAD file, or validated hardware replica.

## Why the abstraction is appropriate for early robotics work

The published research system combines thin McKibben-style fluidic actuators with
electrohydrodynamic fiber pumps in a sealed circuit. For robot motion planning and
control design, the first useful layer is the actuator behavior at the limb or joint
level: how much it contracts, how quickly it responds, how much force it produces,
and how it behaves as a compliant element.

This package provides that layer. A deeper physics layer would require solving
electrohydrodynamic flow, pressure dynamics, and material deformation, which is
outside the scope of a system-level robotics simulation tool.

## Default public parameters used

The defaults in `ElectroFluidicMuscleParams` are seeded from the public paper and
MIT news release:

- max_contraction_strain: 0.20 (20% contraction, public reference)
- response_time_s: 0.30 (approximately 0.3 s, public reference)
- fiber_diameter_m: 0.002 (2 mm reference fiber)
- power_density_w_per_kg: 50.0 (50 W/kg, public reference)

The force, stiffness, and damping values are placeholders. They require fitting
from the Zenodo v2 dataset or from direct hardware measurements.

## Model chain

```
control input
  -> first-order activation lag (response_time_s)
  -> target contraction strain (activation * max_contraction_strain)
  -> active force (activation * max_force_per_fiber_n * bundle_count)
  -> passive force (passive_stiffness_n_per_m * length_error)
  -> damping force (-damping_n_s_per_m * velocity)
  -> total pull force
  -> joint torque (moment_arm * force_difference)
```

## Known limitations

The model does not simulate internal pump behavior, fluid pressure, pump charge
injection, dielectric fluid dynamics, or cavitation. The bias pressure effect
described in the original research is not represented. The MuJoCo XML is a
mechanical approximation for the biceps/triceps demonstration geometry, not a
reconstruction of the experimental hardware or its calibration.

Variable moment arm geometry, tendon wrapping, and anatomical routing are not
modeled.

For MuJoCo-specific integration gaps and how to address them, see
`docs/mujoco_integration.md`.

## Recommended next steps

1. Download the Zenodo v2 dataset using `scripts/fetch_zenodo_dataset.py`.
2. Inspect force-displacement and step-response curves in the dataset.
3. Fit `max_force_per_fiber_n`, `passive_stiffness_n_per_m`, and `damping_n_s_per_m`
   to a specific experimental condition.
4. Validate the fitted model by comparing simulated step responses to measured ones.
5. Update the MuJoCo XML actuator gain to match fitted force values.

See `docs/validation_plan.md` for a more detailed validation workflow.
