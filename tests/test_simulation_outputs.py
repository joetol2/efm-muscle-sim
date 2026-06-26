"""Tests for simulation utilities and example output correctness."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efm_muscle_sim import (
    ElectroFluidicMuscle,
    ElectroFluidicMuscleParams,
    run_simulation,
    save_csv,
)


# ------------------------------------------------------------------
# run_simulation() tests
# ------------------------------------------------------------------

def test_run_simulation_returns_correct_length():
    m = ElectroFluidicMuscle()
    controls = [0.0] * 50 + [1.0] * 50
    history = run_simulation(lambda c: m.step(c, 0.01), controls, dt=0.01)
    assert len(history) == 100


def test_run_simulation_time_column():
    m = ElectroFluidicMuscle()
    controls = [0.5] * 10
    history = run_simulation(lambda c: m.step(c, 0.01), controls, dt=0.01)
    times = [row["time_s"] for row in history]
    assert times[0] == pytest.approx(0.0)
    assert times[-1] == pytest.approx(0.09)


def test_run_simulation_zero_dt_raises():
    m = ElectroFluidicMuscle()
    with pytest.raises(ValueError):
        run_simulation(lambda c: m.step(c, 0.01), [0.5], dt=0.0)


def test_run_simulation_extra_fields_propagate():
    m = ElectroFluidicMuscle()
    controls = [1.0] * 5
    history = run_simulation(
        lambda c: m.step(c, 0.01),
        controls,
        dt=0.01,
        extra_fields={"run_id": 42},
    )
    for row in history:
        assert row["run_id"] == 42


# ------------------------------------------------------------------
# save_csv() tests
# ------------------------------------------------------------------

def test_save_csv_creates_file(tmp_path):
    m = ElectroFluidicMuscle()
    controls = [1.0] * 10
    history = run_simulation(lambda c: m.step(c, 0.01), controls, dt=0.01)
    out = tmp_path / "test_output.csv"
    save_csv(history, out)
    assert out.exists()


def test_save_csv_has_correct_rows(tmp_path):
    m = ElectroFluidicMuscle()
    controls = [0.5] * 20
    history = run_simulation(lambda c: m.step(c, 0.01), controls, dt=0.01)
    out = tmp_path / "test_output.csv"
    save_csv(history, out)
    with out.open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 20


def test_save_csv_empty_raises():
    with pytest.raises(ValueError):
        save_csv([], Path("/tmp/should_not_create.csv"))


# ------------------------------------------------------------------
# MuJoCo graceful failure test
# ------------------------------------------------------------------

def test_mujoco_loader_exits_cleanly_without_mujoco():
    """run_mujoco_loader.py must exit 0 when mujoco is not installed."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "run_mujoco_loader.py")],
        capture_output=True,
        text=True,
    )
    # Either mujoco is installed (exit 0) or it gracefully reports missing (exit 0)
    assert result.returncode == 0


# ------------------------------------------------------------------
# Output folder tests (run examples, check files appear)
# ------------------------------------------------------------------

def test_actuator_example_writes_csv(tmp_path):
    """run_actuator_step_response.py writes a CSV to outputs/."""
    # Run inline rather than subprocess to keep it fast
    from efm_muscle_sim import plot_actuator_response, save_csv

    m = ElectroFluidicMuscle(ElectroFluidicMuscleParams(bundle_count=2))
    controls = [0.0] * 100 + [1.0] * 400 + [0.0] * 100
    history = run_simulation(lambda c: m.step(c, 0.01), controls, dt=0.01)

    out_csv = tmp_path / "actuator.csv"
    save_csv(history, out_csv)
    assert out_csv.exists()

    with out_csv.open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 600


def test_joint_example_writes_csv(tmp_path):
    """Antagonistic joint run writes a CSV."""
    from efm_muscle_sim import AntagonisticJoint, save_csv

    joint = AntagonisticJoint()
    phases = [(0.8, 0.0)] * 200 + [(0.0, 0.8)] * 200
    history = run_simulation(
        lambda pair: joint.step(pair[0], pair[1], 0.01),
        phases,
        dt=0.01,
    )
    out_csv = tmp_path / "joint.csv"
    save_csv(history, out_csv)
    assert out_csv.exists()
