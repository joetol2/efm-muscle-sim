# Model assumptions

## Actuator model

The ElectroFluidicMuscle class treats a fiber muscle bundle as a lumped,
one-dimensional contractile element. The following assumptions apply:

**Activation dynamics**
Activation follows a single first-order lag with time constant response_time_s.
The same time constant governs both activation and deactivation. In reality,
activation and deactivation may differ due to pump fill/drain asymmetry. A
more accurate model would use separate time constants derived from experimental
data.

**Contraction strain**
Target contraction is proportional to activation. Peak contraction equals
max_contraction_strain at full activation. This is a linear approximation.
Actual contraction behavior may be nonlinear and depend on load, fiber tension,
and pre-pressurization state.

**Force generation**
Active force is proportional to activation and bundle count. Passive force is
a linear spring activated by extension beyond target length. These are both
simplifications. Published results suggest force outputs depend on fiber
geometry, bundle packing, and the fluid circuit state in ways this model
does not capture.

**Bundle count**
bundle_count scales force linearly. Cross-fiber interactions, fluid coupling
between fibers in a bundle, and manufacturing variation are not modeled.

## Joint model

The AntagonisticJoint class treats the joint as a rigid one-degree-of-freedom
hinge with constant moment arm and lumped rotational inertia. The following
assumptions apply:

**Moment arm**
The moment arm is constant and identical for flexor and extensor. In a real
arm or gripper, moment arm varies with joint angle due to tendon geometry.

**Inertia**
Inertia is modeled as a single scalar. Distributed mass, payload variation,
and limb segment geometry are not represented.

**Joint limits**
Hard limits are enforced by zeroing angular velocity at the boundary. This is
a mechanical stop approximation. Real systems may use compliant limiting or
reflex-like control responses.

## Integration

Both the actuator and joint models use explicit Euler integration. This is
first-order accurate and may introduce numerical error at large timesteps.
Use dt values of 0.01 seconds or smaller for reliable behavior. Validation
tests should be re-run if dt is increased.

## What these assumptions imply for use

These assumptions are appropriate for:

- testing whether a muscle-like control architecture can produce desired motion
- comparing relative performance across bundle count and parameter combinations
- generating synthetic motion trajectories for downstream motion planning work

These assumptions are not appropriate for:

- predicting absolute force or contraction outputs
- hardware sizing or actuator specification
- safety-critical analysis
- claiming correspondence with the published experimental results
