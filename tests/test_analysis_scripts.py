import subprocess
import sys
from pathlib import Path


def test_sensitivity_experiments_script_runs():
    result = subprocess.run(
        [sys.executable, "notes/sensitivity_experiments.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Sensitivity experiments" in result.stdout
    assert "baseline" in result.stdout.lower()
    assert "weight-shift" in result.stdout.lower()
    assert "mood-off" in result.stdout.lower()


def test_fairness_diagnostics_script_runs():
    result = subprocess.run(
        [sys.executable, "notes/fairness_diagnostics.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Fairness diagnostics" in result.stdout
    assert "average top-5 score" in result.stdout.lower()
