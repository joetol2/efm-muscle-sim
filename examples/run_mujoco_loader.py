"""
Attempt to load the MuJoCo XML arm model.

This script gracefully reports whether MuJoCo is available and, if so,
loads the biceps/triceps arm model and prints basic model information.

MuJoCo is an optional dependency. Install it with:
    pip install mujoco

The XML model is a mechanical approximation for concept exploration.
It is not a validated reconstruction of the MIT experimental hardware.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT / "models" / "mujoco" / "efm_biceps_triceps_arm.xml"


def main() -> None:
    try:
        import mujoco  # type: ignore[import]
    except ImportError:
        print("MuJoCo is not installed.")
        print("Install it with:  pip install mujoco")
        print("Exiting without error.")
        return

    if not XML_PATH.exists():
        print(f"Model file not found: {XML_PATH}")
        sys.exit(1)

    model = mujoco.MjModel.from_xml_path(str(XML_PATH))
    data = mujoco.MjData(model)

    print(f"Model loaded: {XML_PATH.name}")
    print(f"  Bodies      : {model.nbody}")
    print(f"  Joints      : {model.njnt}")
    print(f"  Actuators   : {model.nu}")
    print(f"  Timestep    : {model.opt.timestep} s")

    # Step once to confirm the model runs
    mujoco.mj_step(model, data)
    print("One simulation step completed successfully.")
    print("Time after step:", round(data.time, 6), "s")


if __name__ == "__main__":
    main()
