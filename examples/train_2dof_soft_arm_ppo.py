"""Train the 2-DOF soft arm reach task with PPO.

Requires optional dependencies:
    pip install gymnasium stable-baselines3

This produces a saved policy and a quick evaluation CSV. It is the first training
version engineering can tune for the investor demo.
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim.training_env import SoftArmReachEnv, SoftArmReachTaskParams


def save_csv(rows: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.monitor import Monitor
    except ImportError as exc:
        raise SystemExit(
            "Missing training dependencies. Run: pip install gymnasium stable-baselines3"
        ) from exc

    model_dir = ROOT / "outputs" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    env = Monitor(
        SoftArmReachEnv(
            SoftArmReachTaskParams(
                randomize_target=True,
                randomize_dynamics=True,
                max_steps=300,
            ),
            seed=11,
        )
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=1024,
        batch_size=256,
        gamma=0.98,
        learning_rate=3e-4,
    )
    model.learn(total_timesteps=80_000)
    model_path = model_dir / "efm_2dof_soft_arm_ppo"
    model.save(model_path)
    print(f"Model written: {model_path}.zip")

    eval_env = SoftArmReachEnv(
        SoftArmReachTaskParams(
            randomize_target=False,
            randomize_dynamics=False,
            target_x_m=0.36,
            target_y_m=0.25,
            max_steps=300,
        ),
        seed=17,
    )
    obs, info = eval_env.reset(seed=17)
    rows: list[dict[str, float]] = []
    for step in range(eval_env.task_params.max_steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = eval_env.step(action)
        rows.append(
            {
                "time_s": step * eval_env.task_params.dt,
                "reward": float(reward),
                "action0": float(action[0]),
                "action1": float(action[1]),
                "action2": float(action[2]),
                "action3": float(action[3]),
                **{k: float(v) for k, v in info.items() if isinstance(v, (int, float, np.floating))},
            }
        )
        if terminated or truncated:
            break

    eval_csv = ROOT / "outputs" / "efm_2dof_soft_arm_ppo_eval.csv"
    save_csv(rows, eval_csv)
    print(f"Evaluation CSV written: {eval_csv}")


if __name__ == "__main__":
    main()
