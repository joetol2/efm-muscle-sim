"""Run a scripted 2-DOF soft arm rollout and save investor-friendly outputs.

This is not an RL-trained policy. It is a deterministic smoke demo that proves the
2-DOF model, target task, CSV logging, and plot output are wired together.
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim.training_env import SoftArmReachEnv, SoftArmReachTaskParams


def inverse_kinematics(target_x: float, target_y: float) -> tuple[float, float]:
    """Closed-form IK for the default two-link arm geometry."""

    l1 = 0.30
    l2 = 0.24
    r2 = target_x * target_x + target_y * target_y
    cos_q2 = (r2 - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    cos_q2 = float(np.clip(cos_q2, -0.95, 0.95))
    q2 = float(np.arccos(cos_q2))
    q1 = float(np.arctan2(target_y, target_x) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2)))
    return q1, q2


def agonist_antagonist_command(error: float, velocity: float, kp: float, kd: float) -> tuple[float, float]:
    """Convert a joint error into flexor/extensor commands."""

    effort = kp * error - kd * velocity
    if effort >= 0.0:
        return float(np.clip(effort, 0.0, 1.0)), 0.0
    return 0.0, float(np.clip(-effort, 0.0, 1.0))


def scripted_controller(obs: np.ndarray) -> np.ndarray:
    """IK plus PD controller for a visible reaching rollout."""

    q1 = float(obs[0])
    q2 = float(obs[1])
    q1_dot = float(obs[2])
    q2_dot = float(obs[3])
    target_x = float(obs[6])
    target_y = float(obs[7])
    q1_des, q2_des = inverse_kinematics(target_x, target_y)

    shoulder_flex, shoulder_extend = agonist_antagonist_command(
        q1_des - q1,
        q1_dot,
        kp=2.4,
        kd=0.25,
    )
    elbow_flex, elbow_extend = agonist_antagonist_command(
        q2_des - q2,
        q2_dot,
        kp=1.7,
        kd=0.18,
    )
    return np.array([shoulder_flex, shoulder_extend, elbow_flex, elbow_extend], dtype=np.float32)


def save_csv(rows: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("no rows to write")
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_plot(rows: list[dict[str, float]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    t = [r["time_s"] for r in rows]
    wrist_x = [r["wrist_x_m"] for r in rows]
    wrist_y = [r["wrist_y_m"] for r in rows]
    dist = [r["distance_to_target_m"] for r in rows]
    shoulder = [r["shoulder_angle_deg"] for r in rows]
    elbow = [r["elbow_angle_deg"] for r in rows]

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    fig.suptitle("2-DOF EFM Soft Arm Reach Demo", fontsize=12)

    axes[0].plot(wrist_x, wrist_y, label="wrist path")
    axes[0].scatter([rows[0]["target_x_m"]], [rows[0]["target_y_m"]], marker="x", label="target")
    axes[0].set_xlabel("x (m)")
    axes[0].set_ylabel("y (m)")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, dist)
    axes[1].set_ylabel("distance to target (m)")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, shoulder, label="shoulder")
    axes[2].plot(t, elbow, label="elbow")
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("joint angle (deg)")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> None:
    env = SoftArmReachEnv(
        SoftArmReachTaskParams(
            randomize_target=False,
            randomize_dynamics=False,
            target_x_m=0.36,
            target_y_m=0.25,
            max_steps=300,
        ),
        seed=7,
    )
    obs, info = env.reset(seed=7)
    rows: list[dict[str, float]] = []

    for step in range(env.task_params.max_steps):
        action = scripted_controller(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        rows.append(
            {
                "time_s": step * env.task_params.dt,
                "reward": float(reward),
                "shoulder_cmd_flex": float(action[0]),
                "shoulder_cmd_extend": float(action[1]),
                "elbow_cmd_flex": float(action[2]),
                "elbow_cmd_extend": float(action[3]),
                **{k: float(v) for k, v in info.items() if isinstance(v, (int, float, np.floating))},
            }
        )
        if terminated or truncated:
            break

    out_csv = ROOT / "outputs" / "efm_2dof_soft_arm_rollout.csv"
    out_png = ROOT / "plots" / "efm_2dof_soft_arm_rollout.png"
    save_csv(rows, out_csv)
    save_plot(rows, out_png)
    final = rows[-1]
    print(f"CSV written: {out_csv}")
    print(f"Plot written: {out_png}")
    print(
        "Final distance to target: "
        f"{final['distance_to_target_m']:.3f} m at wrist "
        f"({final['wrist_x_m']:.3f}, {final['wrist_y_m']:.3f})"
    )


if __name__ == "__main__":
    main()
