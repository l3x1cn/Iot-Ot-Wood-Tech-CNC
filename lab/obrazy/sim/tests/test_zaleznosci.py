"""Obraz symulatorów (requirements.txt) i środowisko testów (pyproject.toml) muszą mieć te same wersje."""

import tomllib
from pathlib import Path

KATALOG_GLOWNY = Path(__file__).resolve().parents[4]


def test_requirements_obrazu_zgodne_z_pyproject():
    projekt = tomllib.loads((KATALOG_GLOWNY / "pyproject.toml").read_text())
    obraz = (KATALOG_GLOWNY / "lab/obrazy/sim/requirements.txt").read_text().split()
    assert sorted(projekt["project"]["dependencies"]) == sorted(obraz)
