# 2-DOF EFM Soft Arm Training Demo

This adds a trainable 2-DOF planar soft arm on top of the existing EFM actuator and antagonistic joint model.

## What this adds

- `src/efm_muscle_sim/soft_arm.py`: shoulder and elbow joints, each driven by opposing muscle pairs.
- `src/efm_muscle_sim/training_env.py`: Gymnasium-compatible reaching environment.
- `examples/run_2dof_soft_arm_rollout.py`: deterministic rollout that writes CSV and PNG outputs.
- `examples/train_2dof_soft_arm_ppo.py`: optional PPO training script using Stable Baselines3.
- `tests/test_soft_arm_2d.py`: smoke tests for the arm and environment.

## Investor demo intent

The demo should show that the actuator model is now connected to visible trainable behavior. Instead of one actuator moving in isolation, multiple opposing muscle pairs coordinate through shoulder and elbow joints to move the wrist toward a target.

The first investor version can show:

1. A 2-DOF soft arm reaching toward a target.
2. A learned policy improving over training.
3. A final rollout where the wrist reaches the target under randomized actuator conditions.
4. A later extension with contact or pushback at the endpoint.

## Run the scripted smoke demo

```bash
python examples/run_2dof_soft_arm_rollout.py
```

Expected outputs:

```text
outputs/efm_2dof_soft_arm_rollout.csv
plots/efm_2dof_soft_arm_rollout.png
```

## Train with PPO

```bash
pip install gymnasium stable-baselines3
python examples/train_2dof_soft_arm_ppo.py
```

Expected outputs:

```text
outputs/models/efm_2dof_soft_arm_ppo.zip
outputs/efm_2dof_soft_arm_ppo_eval.csv
```

## Assets

The following reference images are in `docs/images/`.

**`docs/images/efm_2dof_soft_arm_model_diagram.png`**
Technical overview of the training interface: observation vector, action space, reward structure, and how the 2-DOF environment wraps the existing EFM joint model.

**`docs/images/efm_2dof_soft_arm_model_render.png`**
Simplified diagram of the planar two-link arm geometry. Shows shoulder and elbow joints, link lengths (0.30 m, 0.24 m), and wrist endpoint.

**`docs/images/robotic_arm_on_sleek_tabletop.png`**
Concept render of a physical soft robotic arm. Included for investor presentation context only. This is a 3D concept illustration, not a photo of hardware and not a validated physical result.

## Notes for engineering

This is still a behavioral training prototype. It does not turn the existing EFM model into a validated physical simulator. The force, damping, stiffness, and geometry values still need fitting before anyone uses this for hardware claims.

The model is deliberately simple so the team can get a visible training demo working quickly. Once the basic PPO loop is stable, the next useful additions are contact training, pushback disturbances, and a rollout renderer that exports a short MP4 or GIF.
