"""Render a 2-DOF soft arm rollout as an animated GIF.

Runs the same scripted IK+PD controller as the rollout demo and writes
a GIF showing the arm sweeping to the target.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim.training_env import SoftArmReachEnv, SoftArmReachTaskParams


def inverse_kinematics(target_x: float, target_y: float) -> tuple[float, float]:
    l1, l2 = 0.30, 0.24
    r2 = target_x ** 2 + target_y ** 2
    cos_q2 = float(np.clip((r2 - l1**2 - l2**2) / (2.0 * l1 * l2), -0.95, 0.95))
    q2 = float(np.arccos(cos_q2))
    q1 = float(np.arctan2(target_y, target_x) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2)))
    return q1, q2


def agonist_antagonist_command(error: float, velocity: float, kp: float, kd: float) -> tuple[float, float]:
    effort = kp * error - kd * velocity
    if effort >= 0.0:
        return float(np.clip(effort, 0.0, 1.0)), 0.0
    return 0.0, float(np.clip(-effort, 0.0, 1.0))


def scripted_controller(obs: np.ndarray) -> np.ndarray:
    q1, q2, q1_dot, q2_dot = float(obs[0]), float(obs[1]), float(obs[2]), float(obs[3])
    target_x, target_y = float(obs[6]), float(obs[7])
    q1_des, q2_des = inverse_kinematics(target_x, target_y)
    sf, se = agonist_antagonist_command(q1_des - q1, q1_dot, kp=2.4, kd=0.25)
    ef, ee = agonist_antagonist_command(q2_des - q2, q2_dot, kp=1.7, kd=0.18)
    return np.array([sf, se, ef, ee], dtype=np.float32)


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

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
    obs, _ = env.reset(seed=7)

    frames: list[dict] = []
    for _ in range(env.task_params.max_steps):
        action = scripted_controller(obs)
        obs, _, terminated, truncated, info = env.step(action)
        arm_state = env.arm.forward_kinematics()
        frames.append({
            "base": arm_state["base"],
            "elbow": arm_state["elbow"],
            "wrist": arm_state["wrist"],
            "target": (info["target_x_m"], info["target_y_m"]),
            "distance": info["distance_to_target_m"],
        })
        if terminated or truncated:
            break

    l_total = env.arm.params.link1_length_m + env.arm.params.link2_length_m
    margin = 0.08

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-l_total - margin, l_total + margin)
    ax.set_ylim(-l_total - margin, l_total + margin)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.25)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("2-DOF EFM Soft Arm Reach")

    target_x, target_y = frames[0]["target"]
    target_circle = plt.Circle((target_x, target_y), env.task_params.target_radius_m,
                                color="green", alpha=0.25, zorder=2)
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

    out_path = ROOT / "plots" / "efm_2dof_soft_arm_rollout.gif"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(out_path), writer="pillow", fps=25)
    plt.close(fig)
    print(f"GIF written: {out_path}")
    final = frames[-1]
    print(f"Final distance to target: {final['distance']:.3f} m at wrist "
          f"({final['wrist'][0]:.3f}, {final['wrist'][1]:.3f})")


if __name__ == "__main__":
    main()
