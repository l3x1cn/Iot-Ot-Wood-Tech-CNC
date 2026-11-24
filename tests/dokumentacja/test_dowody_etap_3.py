"""Dowody analizy ruchu v0 (T08) w evidence/etap-3/ muszą zgadzać się z ich opisem w README.md.

Test czyta tabelę „Pliki” z evidence/etap-3/README.md. Pilnuje, żeby:
- każdy plik z tabeli był w katalogu, a każdy plik z katalogu miał opis (kryteria akceptacji T08),
- zrzuty, konsola i logi zawierały fragmenty, na które powołuje się opis,
- nagrania były plikami pcap.
"""

import re
from pathlib import Path

import pytest

KATALOG = Path(__file__).resolve().parents[2] / "evidence/etap-3"
PCAP = {b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x0a\x0d\x0d\x0a"}  # pcap (oba porządki bajtów), pcapng


def tabela(plik: Path, naglowek: str) -> list[dict[str, str]]:
    """Wiersze pierwszej tabeli Markdown pod nagłówkiem `naglowek` (razem z #)."""
    tekst = plik.read_text(encoding="utf-8")
    poziom = naglowek.split(" ", 1)[0]
    sekcja = tekst.split(f"\n{naglowek}\n", 1)[1].split(f"\n{poziom} ", 1)[0]
    linie = []
    for linia in sekcja.splitlines():
        if linia.startswith("|"):
            linie.append(linia)
        elif linie:
            break
    kolumny = [k.strip() for k in linie[0].strip("|").split("|")]
    return [dict(zip(kolumny, (k.strip() for k in linia.strip("|").split("|")))) for linia in linie[2:]]


PLIKI = {w["Plik"].strip("`"): w for w in tabela(KATALOG / "README.md", "### Pliki")}


def test_kazdy_plik_ma_opis_i_kazdy_opis_ma_plik():
    w_katalogu = {p.name for p in KATALOG.iterdir() if p.name != "README.md"}
    assert set(PLIKI) == w_katalogu


@pytest.mark.parametrize("nazwa", sorted(PLIKI), ids=str)
def test_plik_zawiera_to_co_opisuje_readme(nazwa):
    plik = KATALOG / nazwa
    assert len(PLIKI[nazwa]["Co widać"]) > 40
    if nazwa.endswith(".pcap"):
        assert plik.read_bytes()[:4] in PCAP
        assert plik.stat().st_size > 10_000
        return
    tekst = plik.read_text(encoding="utf-8")
    fragmenty = re.findall(r"`([^`]+)`", PLIKI[nazwa]["Fragment w pliku"])
    assert fragmenty, f"{nazwa}: brak fragmentów w opisie"
    for fragment in fragmenty:
        assert fragment in tekst, f"{nazwa}: brak „{fragment}”"
