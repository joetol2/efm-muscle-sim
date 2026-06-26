"""
Simulation loop utilities.

These functions drive actuator or joint models forward in time, collect state
history, and optionally write results to CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence


def run_simulation(
    step_fn: Callable[[float], Dict[str, float]],
    control_sequence: Sequence[float],
    dt: float,
    extra_fields: Optional[Dict[str, float]] = None,
) -> List[Dict[str, float]]:
    """
    Run a time-stepped simulation loop and return the state history.

    Parameters
    ----------
    step_fn:
        Callable that accepts a control value (float) and returns a state dict.
    control_sequence:
        Ordered sequence of control values, one per timestep.
    dt:
        Timestep duration in seconds.
    extra_fields:
        Optional fixed-value fields to merge into every row (e.g., sweep params).

    Returns
    -------
    List of state dicts, one per step, each including a "time_s" key.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")

    history: List[Dict[str, float]] = []
    extra = extra_fields or {}

    for i, control in enumerate(control_sequence):
        state = step_fn(control)
        row = {"time_s": i * dt, "control": control}
        row.update(state)
        row.update(extra)
        history.append(row)

    return history


def save_csv(history: List[Dict[str, float]], path: Path) -> None:
    """
    Write a list of state dicts to a CSV file.

    Parameters
    ----------
    history:
        Output from run_simulation().
    path:
        Destination file path. Parent directories are created if needed.
    """
    if not history:
        raise ValueError("history is empty")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(history[0].keys())
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history)
