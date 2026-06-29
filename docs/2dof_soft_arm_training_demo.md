# 2-DOF EFM Soft Arm Training Demo

## Purpose

This demo extends the existing one-joint EFM antagonistic actuator model into a two-joint planar arm that can reach a target in 2D space. The goal is to show that the actuator model is wired into visible, trainable behavior, not just a single actuator running in isolation.

This is a simulation and training prototype. It does not validate sim-to-real transfer, hardware performance, or physical actuator parameters. Force, damping, stiffness, and geometry values still need fitting against experimental data before any hardware claims can be made.

## What this adds

| File | Purpose |
|---|---|
| `src/efm_muscle_sim/soft_arm.py` | `SoftArm2D` and `SoftArm2DParams` |
| `src/efm_muscle_sim/training_env.py` | `SoftArmReachEnv` and `SoftArmReachTaskParams` |
| `examples/run_2dof_soft_arm_rollout.py` | Scripted IK+PD demo, writes CSV and PNG |
| `examples/render_2dof_soft_arm_gif.py` | Animated GIF renderer |
| `examples/train_2dof_soft_arm_ppo.py` | PPO training via stable-baselines3 |
| `tests/test_soft_arm_2d.py` | Smoke tests for arm and environment |

## Model structure

![2-DOF arm model diagram](images/efm_2dof_soft_arm_model_diagram.png)

The arm has two rigid links connected at a shoulder and an elbow joint. Each joint is driven by the same `AntagonisticJoint` model already in the repo: a flexor and extensor muscle pair, each an `ElectroFluidicMuscle` with first-order activation lag.

**Link geometry (placeholder values pending fitting):**

| Parameter | Value |
|---|---|
| Upper arm length | 0.30 m |
| Forearm length | 0.24 m |
| Shoulder moment arm | 0.030 m |
| Elbow moment arm | 0.022 m |
| Shoulder angle range | -1.20 to 1.80 rad |
| Elbow angle range | 0.00 to 2.35 rad |

![Simplified arm geometry](images/efm_2dof_soft_arm_model_render.png)

## Action space

The arm takes a 4-value action vector, one value per muscle, all in [0, 1]:

```
[shoulder_flex, shoulder_extend, elbow_flex, elbow_extend]
```

Setting both values in a pair above zero co-contracts both muscles, stiffening the joint without necessarily producing net rotation. This matches the physical behavior of antagonistic actuators.

## Observation space

`SoftArmReachEnv` produces a 16-value observation at each step:

| Index | Value |
|---|---|
| 0 | Shoulder angle (rad) |
| 1 | Elbow angle (rad) |
| 2 | Shoulder angular velocity (rad/s) |
| 3 | Elbow angular velocity (rad/s) |
| 4 | Wrist x position (m) |
| 5 | Wrist y position (m) |
| 6 | Target x position (m) |
| 7 | Target y position (m) |
| 8 | dx: target x minus wrist x (m) |
| 9 | dy: target y minus wrist y (m) |
| 10 | Contact force x (N) |
| 11 | Contact force y (N) |
| 12 | Shoulder flexor activation |
| 13 | Shoulder extensor activation |
| 14 | Elbow flexor activation |
| 15 | Elbow extensor activation |

## Reward design

At each step:

```
reward = -distance_to_target
       - 0.015 * (|shoulder_velocity| + |elbow_velocity|)
       - 0.025 * mean(action^2)
       - 0.04 * (min(sh_flex, sh_ext) + min(el_flex, el_ext))
       + 2.0 * (1 if distance <= target_radius else 0)
```

The velocity and action-effort penalties discourage aggressive oscillatory behavior. The co-contraction penalty discourages wasting activation by fighting both muscles against each other. The success bonus rewards holding the wrist within the target radius for `success_hold_steps` consecutive steps (default 20).

## Dynamics randomization

When `randomize_dynamics=True`, each episode samples new actuator parameters:

| Parameter | Range |
|---|---|
| Response time | 0.20 to 0.45 s |
| Max force per fiber | 0.75 to 1.40 N |
| Damping | 0.04 to 0.10 N·s/m |
| Passive stiffness | 3.5 to 8.0 N/m |

This prevents a trained policy from overfitting to one fixed actuator and is the first step toward robustness across units with manufacturing variation.

## Optional contact

Setting `contact_wall_x_m` in `SoftArmReachTaskParams` adds a vertical wall. When the wrist penetrates the wall, a spring-damper contact force pushes back and enters the observation. This enables training policies that can push against a surface, not just reach in free space.

## Scripted rollout vs RL training

**Scripted rollout** (`run_2dof_soft_arm_rollout.py`): A deterministic closed-form IK solver computes desired joint angles from the target position, and a PD controller converts joint angle errors into muscle commands. This is not a trained policy. It is a smoke test that confirms the arm model, forward kinematics, and logging are all wired correctly.

**RL training** (`train_2dof_soft_arm_ppo.py`): Uses Proximal Policy Optimization (PPO) from stable-baselines3 to learn a control policy from scratch. The policy is a neural network that maps observations to actions. Training takes minutes to hours depending on hardware and the number of timesteps.

## Running the demos

### Scripted rollout (no optional dependencies)

```bash
pip install -e .
python examples/run_2dof_soft_arm_rollout.py
```

Expected output:

```
CSV written: outputs/efm_2dof_soft_arm_rollout.csv
Plot written: plots/efm_2dof_soft_arm_rollout.png
Final distance to target: 0.009 m at wrist (0.367, 0.244)
```

Sample rollout plot:

![Sample rollout](images/2dof_soft_arm_sample_rollout.png)

### Animated GIF

```bash
python examples/render_2dof_soft_arm_gif.py
```

Writes `plots/efm_2dof_soft_arm_rollout.gif`.

### PPO training

```bash
pip install "efm-muscle-sim[training]"
python examples/train_2dof_soft_arm_ppo.py
```

Or install dependencies manually:

```bash
pip install gymnasium stable-baselines3
```

Expected outputs:

```
outputs/models/efm_2dof_soft_arm_ppo.zip
outputs/efm_2dof_soft_arm_ppo_eval.csv
```

## PNG assets in docs/images/

| File | What it shows |
|---|---|
| `efm_2dof_soft_arm_model_diagram.png` | Technical overview: obs/action/reward structure and environment wiring |
| `efm_2dof_soft_arm_model_render.png` | Simplified arm geometry: joint layout, link lengths, wrist endpoint |
| `robotic_arm_on_sleek_tabletop.png` | Concept render for presentation context only. Not a physical prototype or hardware result. |
| `2dof_soft_arm_sample_rollout.png` | Actual output from `run_2dof_soft_arm_rollout.py`: wrist path, distance over time, joint angles |

## What this demo does not prove

- It does not validate that the force or stiffness values match the physical actuator.
- It does not demonstrate sim-to-real transfer.
- It does not show that a trained policy will generalize to hardware.
- The concept render is a 3D illustration only and does not represent a built system.

Next steps before hardware relevance: fit `max_force_per_fiber_n`, `passive_stiffness_n_per_m`, and `damping_n_s_per_m` against the Zenodo dataset using `scripts/fit_parameters.py`, then re-run the rollout and training with those values.
