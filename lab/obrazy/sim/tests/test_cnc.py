"""Testy jednostkowe symulatora CNC: parser G-code i model prądu wrzeciona."""

import hashlib
import statistics

from wtsim.cnc import CZAS_RUCHU, Maszyna

PROGRAM = """; test
G21 G90
M3 S18000
G0 Z5
G1 Z-6 F1500 (wejście w materiał)
G1 X1200 F3000
G0 Z5
M5
"""


def srednia_pradu(maszyna: Maszyna, kroki: int = 5) -> float:
    pomiary = []
    for _ in range(kroki):
        maszyna.krok(0.1)
        pomiary.append(maszyna.prad)
    return statistics.mean(pomiary)


def test_parser_liczy_ruchy_i_skrot():
    m = Maszyna()
    wynik = m.wczytaj(PROGRAM, "test.nc")
    assert wynik["ruchy"] == 4  # G0, G1, G1, G0
    assert wynik["sha256"] == hashlib.sha256(PROGRAM.encode()).hexdigest()
    assert m.pracuje


def test_komentarze_nie_sa_parsowane():
    m = Maszyna()
    m.wczytaj("G1 Z-3 F1000 ; G1 Z-99\nG1 X10 (G1 Z-99)\n", None)
    assert [r["Z"] for r in m.ruchy] == [-3.0, -3.0]


def test_prad_rosnie_z_glebokoscia_skrawania():
    plytko, gleboko = Maszyna(), Maszyna()
    plytko.wczytaj("M3 S18000\nG1 Z-3 F3000\nG1 X100\n", None)
    gleboko.wczytaj("M3 S18000\nG1 Z-12 F3000\nG1 X100\n", None)
    assert srednia_pradu(gleboko) > srednia_pradu(plytko) * 1.5


def test_bez_programu_prad_spoczynkowy():
    m = Maszyna()
    assert srednia_pradu(m) < 0.5


def test_program_konczy_sie_i_wylacza_wrzeciono():
    m = Maszyna()
    m.wczytaj("M3 S18000\nG1 Z-6 F3000\nG0 Z5\nM5\n", None)
    for _ in range(int(2 * CZAS_RUCHU / 0.1) + 2):
        m.krok(0.1)
    assert not m.pracuje
    assert not m.wrzeciono
