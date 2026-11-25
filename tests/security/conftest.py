"""Wspólne narzędzia testów na działającym labie: polecenia w kontenerach przez docker compose."""

import subprocess
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[2]


class Lab:
    def __init__(self, wersja: str) -> None:
        self.compose = ["docker", "compose", "-f", str(KORZEN / "lab" / wersja / "compose.yaml"), "--profile", "atak"]

    def exec(self, usluga: str, *polecenie: str, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            [*self.compose, "exec", "-T", usluga, *polecenie],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def logi(self, usluga: str) -> str:
        return subprocess.run([*self.compose, "logs", "--no-log-prefix", usluga], capture_output=True, text=True).stdout


@pytest.fixture(scope="session")
def v0() -> Lab:
    lab = Lab("v0")
    wynik = subprocess.run([*lab.compose, "ps", "--status", "running", "--services"], capture_output=True, text=True)
    if "biuro-pc" not in wynik.stdout.split():
        pytest.fail("lab v0 nie działa: najpierw make v0-up-atak")
    return lab


@pytest.fixture(scope="session")
def v1() -> Lab:
    lab = Lab("v1")
    wynik = subprocess.run([*lab.compose, "ps", "--status", "running", "--services"], capture_output=True, text=True)
    if "biuro-pc" not in wynik.stdout.split():
        pytest.fail("lab v1 nie działa: najpierw make v1-up-atak")
    return lab
