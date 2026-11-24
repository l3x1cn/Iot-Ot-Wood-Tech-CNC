"""Inwentaryzacja aktywów (T03) musi nadążać za labem v0.

Test czyta lab/v0/compose.yaml i tabelę w docs/architektura/inwentaryzacja-aktywow.md. Pilnuje, żeby:
- każdy kontener labu był w tabeli z adresem z compose,
- każde aktywo miało poziom Purdue, właściciela (IT/OT) i krytyczność ze skali,
- każde aktywo miało opis funkcji i danych.
Compose czytamy prostym parserem (klucze z wcięciem 2 spacji w sekcjach services i networks), bez zależności od PyYAML.
"""

import re
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[2]
COMPOSE = KORZEN / "lab/v0/compose.yaml"
DOKUMENT = KORZEN / "docs/architektura/inwentaryzacja-aktywow.md"

KOLUMNY = ["ID", "Aktywo", "W labie", "Purdue", "Adres v0", "Protokoły i porty", "Właściciel", "Krytyczność"]
WLASCICIELE = {"IT", "OT"}
KRYTYCZNOSC = {"Krytyczna", "Wysoka", "Średnia", "Niska"}


def wczytaj_compose() -> tuple[dict[str, set[str]], set[str]]:
    """Zwraca {usługa: adresy IPv4} i nazwy sieci z compose."""
    uslugi: dict[str, set[str]] = {}
    sieci: set[str] = set()
    sekcja = usluga = None
    for linia in COMPOSE.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^([A-Za-z][\w-]*):", linia):
            sekcja, usluga = m.group(1), None
        elif m := re.match(r"^  ([\w.-]+):", linia):
            if sekcja == "services":
                usluga = m.group(1)
                uslugi[usluga] = set()
            elif sekcja == "networks":
                sieci.add(m.group(1))
        elif usluga and (m := re.search(r"ipv4_address:\s*([\d.]+)", linia)):
            uslugi[usluga].add(m.group(1))
    return uslugi, sieci


def tabela(naglowek: str) -> list[dict[str, str]]:
    """Wiersze pierwszej tabeli Markdown pod nagłówkiem `## <naglowek>`."""
    tekst = DOKUMENT.read_text(encoding="utf-8")
    sekcja = tekst.split(f"\n## {naglowek}\n", 1)[1].split("\n## ", 1)[0]
    linie = [linia for linia in sekcja.splitlines() if linia.startswith("|")]
    kolumny = [k.strip() for k in linie[0].strip("|").split("|")]
    return [dict(zip(kolumny, (k.strip() for k in linia.strip("|").split("|")))) for linia in linie[2:]]


USLUGI, SIECI = wczytaj_compose()
AKTYWA = tabela("Tabela aktywów")


def test_parser_compose_widzi_lab():
    assert {"router", "chmura-mqtt", "cnc-1", "plc-odpylanie"} <= USLUGI.keys()
    assert {"zaklad", "internet"} <= SIECI
    assert USLUGI["cnc-1"] == {"10.10.0.11"}


def test_tabela_ma_wymagane_kolumny():
    assert list(AKTYWA[0]) == KOLUMNY


def test_identyfikatory_sa_unikalne():
    identyfikatory = [a["ID"] for a in AKTYWA]
    assert len(identyfikatory) == len(set(identyfikatory))
    assert all(re.fullmatch(r"A\d{2}", i) for i in identyfikatory)


def test_kazdy_kontener_labu_jest_w_tabeli():
    w_tabeli = {m.group(1) for a in AKTYWA if (m := re.fullmatch(r"`([\w-]+)`", a["W labie"]))}
    assert w_tabeli == set(USLUGI)


@pytest.mark.parametrize("aktywo", AKTYWA, ids=lambda a: a["ID"])
def test_odpowiednik_w_labie(aktywo):
    w_labie = aktywo["W labie"]
    if m := re.fullmatch(r"`([\w-]+)`", w_labie):
        for adres in USLUGI[m.group(1)]:
            assert adres in aktywo["Adres v0"], f"{aktywo['ID']}: brak adresu {adres} z compose"
    elif m := re.fullmatch(r"sieć `([\w-]+)`", w_labie):
        assert m.group(1) in SIECI
    else:
        assert w_labie == "poza symulacją"


@pytest.mark.parametrize("aktywo", AKTYWA, ids=lambda a: a["ID"])
def test_aktywo_ma_purdue_wlasciciela_i_krytycznosc(aktywo):
    assert re.match(r"L[0-5](\.5)?\b", aktywo["Purdue"]), aktywo["Purdue"]
    assert aktywo["Właściciel"] in WLASCICIELE
    assert aktywo["Krytyczność"] in KRYTYCZNOSC


def test_kazde_aktywo_ma_opis_funkcji_i_danych():
    opisane = set()
    for wiersz in tabela("Funkcja i przetwarzane dane"):
        assert wiersz["Funkcja"] and wiersz["Przetwarzane dane"] and wiersz["Uzasadnienie krytyczności"]
        opisane |= {i.strip() for i in wiersz["ID"].split(",")}
    assert opisane == {a["ID"] for a in AKTYWA}
