"""Lab v1: testy segmentacji sieci zabezpieczonej (stan to-be).

Dwie grupy testów:

* funkcjonalne — dozwolone kanały (conduity z T05) działają: maszyny piszą telemetrię do lokalnego
  brokera A14 w strefie operacji, a stacja CAD wysyła G-code na obrabiarki przez zaporę OT;
* segmentacja — odwrotność celowych słabości v0: z przejętego komputera biurowego (biuro-pc w strefie
  biura Z6) nie ma już drogi do stref OT ani do brokera w chmurze. Te same scenariusze, które w
  `test_v0_podatnosci.py` przechodziły (połączenie udane), tu kończą się odrzuceniem albo brakiem trasy.

Adresujemy po IP: biuro i strefy OT są w różnych sieciach Dockera, więc DNS labu ich nie rozwiązuje.

Uruchomienie: make v1-up-atak, potem make test-segmentacja.
"""

import pytest

pytestmark = pytest.mark.segmentacja

# Adresy ze strefowania v1 (docs/architektura/strefy-i-conduity.md).
CNC_1 = "10.10.11.11"
PLC = "10.10.12.21"
BROKER_LOKALNY = "10.10.30.14"
SERWER = "10.10.30.31"
CHMURA = "203.0.113.10"


# --- Funkcjonalne: dozwolone kanały działają ---------------------------------------------------


def test_zapory_maja_polityke_drop(v1):
    """Obie zapory mają w forward politykę drop: domyślnie nic nie przechodzi, tylko jawne kanały."""
    for zapora in ("fw-ot", "fw-it"):
        reguly = v1.exec(zapora, "nft", "list", "chain", "inet", "filter", "forward")
        assert reguly.returncode == 0, reguly.stderr
        assert "policy drop" in reguly.stdout, f"{zapora}: forward powinien mieć policy drop"


def test_telemetria_na_lokalnym_brokerze(v1):
    """Kanały C02/C04: obrabiarki i PLC publikują do lokalnego brokera A14, nie wprost do chmury."""
    logi = v1.logi("broker-lokalny")
    for klient in ("cnc-1", "cnc-2", "plc-odpylanie"):
        assert f"as {klient}" in logi, f"{klient} nie połączył się z lokalnym brokerem A14"


def test_telemetria_nie_idzie_do_chmury(v1):
    """W v1 maszyny nie łączą się już z brokerem w chmurze — robi to dopiero bramka z IDMZ (T12)."""
    logi = v1.logi("chmura-mqtt")
    for klient in ("cnc-1", "cnc-2", "plc-odpylanie"):
        assert f"as {klient}" not in logi, f"{klient} nie powinien łączyć się z chmurą w v1"


def test_cad_wysyla_gcode_na_obrabiarki(v1):
    """Kanał C01: stacja CAD wysyła G-code na obrabiarki przez zaporę OT (jedyne źródło na 8080)."""
    wczytane = v1.logi("cnc-1").count("program_wczytany") + v1.logi("cnc-2").count("program_wczytany")
    assert wczytane > 0, "żadna obrabiarka nie odebrała programu ze stacji CAD przez zaporę OT"


# --- Segmentacja: z biura nie ma drogi do OT ani do chmury (odwrotność słabości v0) -------------


def test_segmentacja_api_cnc_niedostepne_z_biura(v1):
    """Odwrotność słabości 1/4: interfejs CNC na 8080 nie jest już osiągalny z biura."""
    wynik = v1.exec("biuro-pc", "curl", "-s", "-m", "5", "-o", "/dev/null", f"http://{CNC_1}:8080/status")
    assert wynik.returncode != 0, "z biura wciąż da się dojść do API obrabiarki"


def test_segmentacja_serwer_projektow_niedostepny_z_biura(v1):
    """Odwrotność słabości 1/4: serwer projektów (własność intelektualna) jest poza zasięgiem biura."""
    wynik = v1.exec("biuro-pc", "curl", "-s", "-m", "5", "-o", "/dev/null", f"http://{SERWER}/projekty/blat-stolu.nc")
    assert wynik.returncode != 0, "z biura wciąż da się pobrać G-code z serwera projektów"


def test_segmentacja_modbus_plc_niedostepny_z_biura(v1):
    """Odwrotność słabości 1/5: Modbus PLC odpylania nie jest już osiągalny z biura."""
    skrypt = (
        "from pymodbus.client import ModbusTcpClient\n"
        f"c = ModbusTcpClient('{PLC}', port=502, timeout=5)\n"
        "print('connected' if c.connect() else 'refused')\n"
        "c.close()\n"
    )
    wynik = v1.exec("biuro-pc", "python3", "-c", skrypt, timeout=20)
    assert "connected" not in wynik.stdout, "z biura wciąż da się połączyć z PLC po Modbus"


def test_segmentacja_lokalny_broker_niedostepny_z_biura(v1):
    """Lokalny broker A14 w strefie operacji nie przyjmuje połączeń z biura."""
    wynik = v1.exec("biuro-pc", "mosquitto_sub", "-h", BROKER_LOKALNY, "-t", "#", "-C", "1", "-W", "5", timeout=20)
    assert wynik.returncode != 0, "z biura wciąż da się czytać lokalny broker A14"


def test_segmentacja_broker_w_chmurze_niedostepny_z_biura(v1):
    """Kanał do chmury (C09) jest tylko dla bramki z IDMZ — biuro nie publikuje wprost do chmury."""
    wynik = v1.exec(
        "biuro-pc",
        "mosquitto_pub",
        "-h",
        CHMURA,
        "-t",
        "wood-tech/hala1/cnc-1/komenda",
        "-m",
        "STOP",
        "-W",
        "5",
        timeout=20,
    )
    assert wynik.returncode != 0, "z biura wciąż da się wstrzyknąć komendę przez broker w chmurze"
