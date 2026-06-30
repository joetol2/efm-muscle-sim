"""Train the 2-DOF soft arm reach task with PPO.

Requires optional dependencies:
    pip install gymnasium stable-baselines3

Produces:
    outputs/models/efm_2dof_soft_arm_ppo.zip   trained policy
    outputs/efm_2dof_soft_arm_ppo_eval.csv      evaluation rollout data
    plots/efm_2dof_soft_arm_ppo_rollout.gif     animated GIF of trained policy
"""

from __future__ import annotations

import csv
import math
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


def render_gif(frames: list[dict], env: SoftArmReachEnv, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    l_total = env.arm.params.link1_length_m + env.arm.params.link2_length_m
    margin = 0.08

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-l_total - margin, l_total + margin)
    ax.set_ylim(-l_total - margin, l_total + margin)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.25)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("2-DOF EFM Soft Arm: Trained PPO Policy")

    target_x, target_y = frames[0]["target"]
    target_circle = plt.Circle(
        (target_x, target_y), env.task_params.target_radius_m,
        color="green", alpha=0.25, zorder=2
    )
    ax.add_patch(target_circle)
    ax.plot(target_x, target_y, "gx", markersize=10, zorder=3, label="target")

    wrist_trail_x: list[float] = []
    wrist_trail_y: list[float] = []
    trail_line, = ax.plot([], [], color="steelblue", alpha=0.4, linewidth=1, zorder=1)
    link1_line, = ax.plot([], [], color="dimgray", linewidth=4, solid_capstyle="round", zorder=4)
    link2_line, = ax.plot([], [], color="steelblue", linewidth=3, solid_capstyle="round", zorder=4)
    wrist_dot, = ax.plot([], [], "o", color="steelblue", markersize=7, zorder=5)
    dist_text = ax.text(0.02, 0.97, "", transform=ax.transAxes,
                        fontsize=9, va="top", ha="left", color="dimgray")
    ax.legend(loc="lower right", fontsize=8)

    def init():
        trail_line.set_data([], [])
        link1_line.set_data([], [])
        link2_line.set_data([], [])
        wrist_dot.set_data([], [])
        dist_text.set_text("")
        return trail_line, link1_line, link2_line, wrist_dot, dist_text

    def update(i: int):
        f = frames[i]
        bx, by = f["base"]
        ex, ey = f["elbow"]
        wx, wy = f["wrist"]
        wrist_trail_x.append(wx)
        wrist_trail_y.append(wy)
        trail_line.set_data(wrist_trail_x, wrist_trail_y)
        link1_line.set_data([bx, ex], [by, ey])
        link2_line.set_data([ex, wx], [ey, wy])
        wrist_dot.set_data([wx], [wy])
        dist_text.set_text(f"dist: {f['distance']:.3f} m")
        return trail_line, link1_line, link2_line, wrist_dot, dist_text

    stride = max(1, len(frames) // 120)
    frame_indices = list(range(0, len(frames), stride))

    ani = animation.FuncAnimation(
        fig, update, frames=frame_indices, init_func=init,
        blit=True, interval=40,
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(path), writer="pillow", fps=25)
    plt.close(fig)


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
    gif_frames: list[dict] = []

    for step in range(eval_env.task_params.max_steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = eval_env.step(action)

        arm_state = eval_env.arm.forward_kinematics()
        gif_frames.append({
            "base": arm_state["base"],
            "elbow": arm_state["elbow"],
            "wrist": arm_state["wrist"],
            "target": (info["target_x_m"], info["target_y_m"]),
            "distance": info["distance_to_target_m"],
        })

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

    gif_path = ROOT / "plots" / "efm_2dof_soft_arm_ppo_rollout.gif"
    render_gif(gif_frames, eval_env, gif_path)
    print(f"GIF written: {gif_path}")

    final = rows[-1]
    print(
        f"Final distance to target: {final['distance_to_target_m']:.3f} m "
        f"at wrist ({final['wrist_x_m']:.3f}, {final['wrist_y_m']:.3f})"
    )


if __name__ == "__main__":
    main()
