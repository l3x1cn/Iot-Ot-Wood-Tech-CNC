"""Przepływy danych (T04) muszą zgadzać się z inwentaryzacją i z ruchem nagranym w labie v0.

Test czyta tabele z docs/architektura/przeplywy-danych.md i inwentaryzacja-aktywow.md oraz listę połączeń
z evidence/etap-1-2/v0-polaczenia.txt (wynik `make v0-przeplywy`). Pilnuje, żeby:
- każdy przepływ łączył aktywa z inwentaryzacji albo encje zewnętrzne i był na diagramie,
- każde połączenie nagrane w labie należało do jakiegoś przepływu z labu,
- każdy przepływ z labu (bez `*`) było widać w nagraniu.
"""

import importlib.util
import re
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[2]
INWENTARZ = KORZEN / "docs/architektura/inwentaryzacja-aktywow.md"
DFD = KORZEN / "docs/architektura/przeplywy-danych.md"
POLACZENIA = KORZEN / "evidence/etap-1-2/v0-polaczenia.txt"
NAT = "A07"  # router: po stronie internetu połączenia mają jego adres

KOLUMNY = ["ID", "Skąd → dokąd", "Inicjator", "Protokół i port", "Dane", "Szyfrowanie", "Uwierzytelnienie", "Granice"]


def tabela(plik: Path, naglowek: str) -> list[dict[str, str]]:
    """Wiersze pierwszej tabeli Markdown pod nagłówkiem `## <naglowek>`."""
    tekst = plik.read_text(encoding="utf-8")
    sekcja = tekst.split(f"\n## {naglowek}\n", 1)[1].split("\n## ", 1)[0]
    linie = [linia for linia in sekcja.splitlines() if linia.startswith("|")]
    kolumny = [k.strip() for k in linie[0].strip("|").split("|")]
    return [dict(zip(kolumny, (k.strip() for k in linia.strip("|").split("|")))) for linia in linie[2:]]


def lista(tekst: str) -> set[str]:
    return {i.strip() for i in tekst.split(",")}


AKTYWA = {a["ID"]: a for a in tabela(INWENTARZ, "Tabela aktywów")}
ADRESY = {adres: i for i, a in AKTYWA.items() for adres in lista(a["Adres v0"]) if re.fullmatch(r"[\d.]+", adres)}
ENCJE = {e["ID"] for e in tabela(DFD, "Encje zewnętrzne")}
GRANICE = {g["ID"] for g in tabela(DFD, "Granice zaufania")}
PRZEPLYWY = tabela(DFD, "Tabela przepływów")
Z_LABU = [p for p in PRZEPLYWY if not p["ID"].endswith("*")]
DIAGRAM = DFD.read_text(encoding="utf-8").split("```mermaid\n", 1)[1].split("```", 1)[0]


def strony(przeplyw: dict[str, str]) -> set[str]:
    skad, dokad = przeplyw["Skąd → dokąd"].split("→")
    return lista(skad) | lista(dokad)


def nagrane() -> list[tuple[str, str, str, int]]:
    """Połączenia z pliku jako (protokół, inicjator, serwer, port), strony jako identyfikatory aktywów."""
    wynik = []
    for linia in POLACZENIA.read_text(encoding="utf-8").splitlines():
        if linia and not linia.startswith("#"):
            _interfejs, proto, src, _, cel, _ile = linia.split()
            dst, port = cel.rsplit(":", 1)
            wynik.append((proto, ADRESY[src], ADRESY[dst], int(port)))
    return wynik


def pasuje(przeplyw: dict[str, str], proto: str, inicjator: str, serwer: str, port: int) -> bool:
    if f"{port}/{proto}" not in przeplyw["Protokół i port"] or serwer not in strony(przeplyw):
        return False
    if inicjator == NAT:  # połączenie po NAT: inicjator jest w zakładzie, przepływ przechodzi przez GZ1
        return "GZ1" in przeplyw["Granice"]
    return inicjator in lista(przeplyw["Inicjator"])


def test_tabela_ma_wymagane_kolumny():
    assert list(PRZEPLYWY[0]) == KOLUMNY


def test_identyfikatory_sa_unikalne():
    identyfikatory = [p["ID"] for p in PRZEPLYWY]
    assert len(identyfikatory) == len(set(identyfikatory))
    assert all(re.fullmatch(r"F\d{2}( \*)?", i) for i in identyfikatory)


@pytest.mark.parametrize("przeplyw", PRZEPLYWY, ids=lambda p: p["ID"])
def test_przeplyw_laczy_znane_elementy_i_jest_na_diagramie(przeplyw):
    assert strony(przeplyw) <= AKTYWA.keys() | ENCJE
    assert lista(przeplyw["Inicjator"]) <= strony(przeplyw)
    assert przeplyw["Granice"] == "—" or lista(przeplyw["Granice"]) <= GRANICE
    assert f'"{przeplyw["ID"].rstrip(" *")} ' in DIAGRAM
    for element in strony(przeplyw):
        assert re.search(rf"\b{element}\b", DIAGRAM), f"{element} nie ma na diagramie"


@pytest.mark.parametrize("polaczenie", nagrane(), ids=lambda p: f"{p[1]}-{p[2]}:{p[3]}")
def test_kazde_nagrane_polaczenie_nalezy_do_przeplywu(polaczenie):
    assert any(pasuje(p, *polaczenie) for p in Z_LABU), f"połączenie {polaczenie} nie ma przepływu w tabeli"


@pytest.mark.parametrize("przeplyw", Z_LABU, ids=lambda p: p["ID"])
def test_kazdy_przeplyw_z_labu_widac_w_nagraniu(przeplyw):
    assert any(pasuje(przeplyw, *p) for p in nagrane())


def test_skrypt_wyciaga_polaczenia_z_tcpdump():
    spec = importlib.util.spec_from_file_location("przeplywy", KORZEN / "scripts/przeplywy.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    linie = [
        "19:30:21.1 IP 10.10.0.11.40112 > 203.0.113.10.1883: tcp 0",
        "19:30:51.2 IP 10.10.0.41.51234 > 10.10.0.31.80: tcp 0",
        "19:31:21.3 IP 10.10.0.41.51240 > 10.10.0.31.80: tcp 0",
        "19:31:22.0 IP 10.10.0.66.5353 > 224.0.0.251.5353: udp 40",
        "19:31:23.0 ARP, Request who-has 10.10.0.41 tell 10.10.0.12, length 28",
    ]
    assert modul.polaczenia(linie) == {
        ("tcp", "10.10.0.11", "203.0.113.10", 1883): 1,
        ("tcp", "10.10.0.41", "10.10.0.31", 80): 2,
        ("udp", "10.10.0.66", "224.0.0.251", 5353): 1,
    }
