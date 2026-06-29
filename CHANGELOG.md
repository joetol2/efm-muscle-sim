# Changelog

## 0.2.0  2026-06-29

### Added
- `SoftArm2D`: 2-DOF planar soft arm with shoulder and elbow antagonistic joints, forward kinematics, endpoint Jacobian, and optional contact/disturbance input (`src/efm_muscle_sim/soft_arm.py`)
- `SoftArmReachEnv`: Gymnasium-compatible reaching environment with 16-dim observation, 4-dim action, distance/effort/co-contraction reward, dynamics randomization, and optional contact wall (`src/efm_muscle_sim/training_env.py`)
- Scripted IK+PD rollout demo writing CSV and plot (`examples/run_2dof_soft_arm_rollout.py`)
- Animated GIF renderer for the rollout (`examples/render_2dof_soft_arm_gif.py`)
- PPO training script via stable-baselines3 (`examples/train_2dof_soft_arm_ppo.py`)
- Parameter fitting script against Zenodo force-displacement data (`scripts/fit_parameters.py`)
- GitHub Actions CI across Python 3.10, 3.11, 3.12 (`.github/workflows/ci.yml`)
- `QUICKSTART.md` with copy-paste setup and run instructions
- `CHANGELOG.md`
- 3 new smoke tests for the arm and environment (43 total)

## 0.1.0  2026-06-26

### Added
- `ElectroFluidicMuscle`: single-bundle actuator model with first-order activation lag, passive compliance, and damping
- `AntagonisticJoint`: flexor/extensor pair on a 1-DOF hinge with angle limits
- `ElectroFluidicMuscleParams`, `AntagonisticJointParams`: validated parameter dataclasses
- Simulation utilities: `run_simulation`, `save_csv`
- Plotting utilities: `plot_actuator_response`, `plot_joint_response`
- Unit conversion helpers
- MuJoCo placeholder XML arm with spatial tendons and filter actuators
- `docs/mujoco_integration.md`: gain calculation and controller wiring guide
- `docs/repo_handoff.md`: engineer orientation
- 40 pytest tests
