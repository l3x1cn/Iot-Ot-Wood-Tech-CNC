"""Lab v0: testy, które POTWIERDZAJĄ celowe słabości sieci niebezpiecznej.

Każdy test opisuje jedną podatność z lab/README.md („Celowe słabości v0”) i przechodzi wtedy,
gdy podatność istnieje. W v1 te same scenariusze dostaną testy odwrotne (połączenie odrzucone).
Atakujący to `biuro-pc`, przejęty komputer biurowy w tej samej sieci co hala.

Uruchomienie: make v0-up-atak, potem make test-security.
"""

import json

import pytest

pytestmark = pytest.mark.security


def test_lab_nie_ma_wyjscia_do_internetu(v0):
    """Bezpieczeństwo samego labu: atakujący nie wychodzi poza sieci Dockera."""
    wynik = v0.exec("biuro-pc", "curl", "-s", "-m", "5", "-o", "/dev/null", "https://example.com")
    assert wynik.returncode != 0


def test_telemetria_dochodzi_do_chmury_przez_nat(v0):
    """Funkcjonalnie: maszyny łączą się z brokerem w chmurze przez router (NAT na 203.0.113.2)."""
    assert "New client connected from 203.0.113.2" in v0.logi("chmura-mqtt")


def test_podatnosc_anonimowy_odczyt_mqtt(v0):
    """Słabości 2 i 3: z biura bez hasła czytamy telemetrię wrzecion z brokera w chmurze."""
    wynik = v0.exec(
        "biuro-pc",
        "mosquitto_sub",
        "-h",
        "mqtt.chmura.example",
        "-t",
        "wood-tech/hala1/+/telemetria",
        "-C",
        "1",
        "-W",
        "10",
    )
    assert wynik.returncode == 0, wynik.stderr
    telemetria = json.loads(wynik.stdout)
    assert {"prad_A", "obroty_rpm", "sha256"} <= telemetria.keys()


def test_podatnosc_kradziez_projektu_z_serwera(v0):
    """Słabość 1 i 4: biuro pobiera G-code (własność intelektualna) z serwera projektów bez logowania."""
    wynik = v0.exec("biuro-pc", "curl", "-sf", "-m", "5", "http://serwer/projekty/blat-stolu.nc")
    assert wynik.returncode == 0
    assert "M3 S18000" in wynik.stdout


def test_podatnosc_api_cnc_dostepne_z_biura(v0):
    """Słabość 1 i 4: interfejs CNC przyjmujący programy jest osiągalny z biura bez uwierzytelnienia."""
    wynik = v0.exec("biuro-pc", "curl", "-sf", "-m", "5", "http://cnc-1:8080/status")
    assert wynik.returncode == 0
    assert json.loads(wynik.stdout)["cnc"] == "cnc-1"


def test_podatnosc_modbus_plc_dostepny_z_biura(v0):
    """Słabość 1 i 5: z biura czytamy rejestry PLC odpylania przez Modbus TCP (zapis działałby tak samo)."""
    skrypt = (
        "from pymodbus.client import ModbusTcpClient\n"
        "c = ModbusTcpClient('plc-odpylanie', port=502, timeout=3)\n"
        "assert c.connect()\n"
        "r = c.read_holding_registers(0, 3)\n"
        "print(r.registers)\n"
    )
    wynik = v0.exec("biuro-pc", "python3", "-c", skrypt)
    assert wynik.returncode == 0, wynik.stderr
    assert len(json.loads(wynik.stdout)) == 3
