"""Sprawozdanie Etapów 1–2 (T07) musi zgadzać się z dokumentami, które streszcza.

Test czyta docs/sprawozdania/etap-1-2.md oraz inwentaryzację (T03), strefy (T05) i SL-T (T06). Pilnuje, żeby:
- sprawozdanie miało tabelę inwentaryzacji i schematy sieci (kryterium akceptacji T07),
- tabela inwentaryzacji i tabela SL-T w sprawozdaniu nie rozjechały się z dokumentami źródłowymi,
- linki względne w sprawozdaniu prowadziły do istniejących plików.
"""

import re
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[2]
ARCH = KORZEN / "docs/architektura"
SPRAWOZDANIE = KORZEN / "docs/sprawozdania/etap-1-2.md"
FR = [f"FR{i}" for i in range(1, 8)]


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


def lista(tekst: str) -> list[str]:
    return [i.strip() for i in tekst.split(",") if i.strip() and i.strip() != "—"]


TEKST = SPRAWOZDANIE.read_text(encoding="utf-8")
INWENTARZ = {a["ID"]: a for a in tabela(ARCH / "inwentaryzacja-aktywow.md", "## Tabela aktywów")}
STREFY = {s["ID"]: s for s in tabela(ARCH / "strefy-i-conduity.md", "## Strefy")}
STREFA = {a: s for s, wiersz in STREFY.items() for a in lista(wiersz["Aktywa"])}
SL_T = {s["Strefa"]: s for s in tabela(ARCH / "sl-t.md", "## SL-T stref")}


def test_ma_tabele_inwentaryzacji_zgodna_z_t03_i_t05():
    raport = {a["ID"]: a for a in tabela(SPRAWOZDANIE, "### Tabela inwentaryzacji")}
    assert raport.keys() == INWENTARZ.keys()
    for i, a in raport.items():
        zrodlo = INWENTARZ[i]
        assert a["W labie"] == zrodlo["W labie"], i
        assert zrodlo["Purdue"].startswith(a["Purdue"]), i
        assert (a["Właściciel"], a["Krytyczność"]) == (zrodlo["Właściciel"], zrodlo["Krytyczność"]), i
        if i in STREFA:
            assert a["Strefa w `v1`"].startswith(f"{STREFA[i]} {STREFY[STREFA[i]]['Strefa'].rstrip(' *')}"), i
        else:
            assert i in {"A07", "A08"} and a["Strefa w `v1`"] in {"zapora fw-it", "zastąpiona sieciami stref"}, i


def test_ma_schematy_sieci_as_is_i_to_be():
    assert "### Schemat sieci as-is (`v0`)\n\n```mermaid\n" in TEKST
    assert "### Schemat sieci to-be (`v1`)\n\n```mermaid\n" in TEKST


def test_tabela_sl_t_zgodna_z_t06():
    raport = {s["Strefa"]: s for s in tabela(SPRAWOZDANIE, "### SL-T stref")}
    assert raport.keys() == SL_T.keys()
    for strefa, wiersz in raport.items():
        zrodlo = SL_T[strefa]
        assert wiersz["Purdue"] == STREFY[strefa]["Purdue"]
        assert wiersz["SL-T"] == zrodlo["SL-T"]
        assert wiersz["Atakujący"] == zrodlo["Atakujący"]
        assert lista(wiersz["FR na poziomie 3"]) == [fr for fr in FR if zrodlo[fr] == "3"]


def test_linki_wzgledne_prowadza_do_plikow():
    for cel in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", TEKST):
        if not cel.startswith("http"):
            assert (SPRAWOZDANIE.parent / cel).exists(), cel
