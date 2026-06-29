# Repo overlay: 2-DOF soft arm training demo

Copy these files into the root of `joetol2/efm-muscle-sim`.

Files included:

```text
src/efm_muscle_sim/soft_arm.py
src/efm_muscle_sim/training_env.py
examples/run_2dof_soft_arm_rollout.py
examples/train_2dof_soft_arm_ppo.py
tests/test_soft_arm_2d.py
docs/2dof_soft_arm_training_demo.md
```

Suggested package export update in `src/efm_muscle_sim/__init__.py`:

```python
from .soft_arm import SoftArm2D, SoftArm2DParams
from .training_env import SoftArmReachEnv, SoftArmReachTaskParams
```

Suggested optional dependency update in `pyproject.toml`:

```toml
rl = ["gymnasium", "stable-baselines3"]
```

Run smoke checks:

```bash
pytest tests/test_soft_arm_2d.py -v
python examples/run_2dof_soft_arm_rollout.py
```
