# MuJoCo integration notes

## Current state

The Python model (`ElectroFluidicMuscle`) and the MuJoCo XML (`efm_biceps_triceps_arm.xml`) are parallel but not connected. The XML loads and runs in MuJoCo viewer, but it is not wired to the Python simulation, and the actuator gain has not been derived from any experimental data.

This document explains what the XML does, what needs to change before it is useful in a real sim, and how to wire a controller to it.

## What the XML currently does

Two spatial tendons span from origin sites on the upper arm body to insertion sites on the forearm body. Each tendon is driven by a `general` actuator with `dyntype="filter"`, which gives first-order activation lag inside MuJoCo's own integrator. The time constant (`dynprm="0.30"`) matches the public reference response time for these muscles. The gain (`gainprm="30"`) is a placeholder -- it was not derived from the paper or dataset.

## What needs to happen before this is useful

**Fit the gain value.**

`gainprm` maps a normalized control signal in [0, 1] to force in Newtons. Once `max_force_per_fiber_n` is fitted from the Zenodo dataset (see `docs/validation_plan.md`), update the XML gain using:

```
gainprm = max_force_per_fiber_n * bundle_count
```

After that update, the Python model and the MuJoCo actuator will share the same force assumption. Until then, the XML will produce whatever joint motion the placeholder gain happens to give.

**Check moment arm geometry.**

The tendon attachment sites are fixed positions set by `site` elements in the XML. This means the effective moment arm is constant across the joint range. Real muscle geometry produces a variable moment arm as the joint moves. For early concept work this approximation is acceptable, but it will affect how accurately torque scales at the extremes of the joint range.

**Review body mass and inertia.**

The upper arm and forearm masses come from MuJoCo's default capsule density. They are not calibrated to any specific robot. Update the `density` or add explicit `mass` attributes before using this model for dynamics analysis.

## Wiring a controller

To drive the MuJoCo model, set `data.ctrl[0]` (flexor) and `data.ctrl[1]` (extensor) in your step loop. The filter dynamics in the XML handle activation lag, so you pass the raw normalized command directly.

Minimal example:

```python
import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("models/mujoco/efm_biceps_triceps_arm.xml")
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    t = 0.0
    while viewer.is_running():
        # Simple flex command from t=0.5 to t=2.5
        flex_cmd = 1.0 if 0.5 <= t < 2.5 else 0.1
        ext_cmd = 0.1

        data.ctrl[0] = flex_cmd
        data.ctrl[1] = ext_cmd
        mujoco.mj_step(model, data)
        viewer.sync()
        t += model.opt.timestep
```

To compare against the Python model, run `examples/run_antagonistic_joint_demo.py` with the same flex/extend timing and check whether joint angle trajectories are similar. A large mismatch indicates the gain or moment arm needs adjustment.

## Suggested order of operations

1. Fit the Python actuator model against Zenodo data (see `docs/validation_plan.md`)
2. Compute the fitted gain and update `gainprm` in the XML for both actuators
3. Run the controller sketch above and compare joint angle output to the Python demo
4. Adjust body mass and geometry to match your specific robot segment
5. Integrate the XML into your full robot model once the isolated arm behavior looks reasonable
