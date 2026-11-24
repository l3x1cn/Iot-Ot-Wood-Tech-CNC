"""Strefy i conduity (T05) muszą pokrywać inwentaryzację i przepływy danych, a biuro nie może mieć drogi do OT.

Test czyta tabele z docs/architektura/strefy-i-conduity.md, inwentaryzacja-aktywow.md i przeplywy-danych.md.
Pilnuje kryteriów akceptacji T05:
- każdy przepływ z DFD ma kanały w conduitach, odbywa się w jednej strefie albo jest celowo zablokowany,
- biuro (L4) nie ma kanału ani wspólnej zapory ze strefami OT (L0–L3), a z internetu nie otwiera się żadne połączenie,
oraz spójności tabel: każde aktywo jest w dokładnie jednej strefie, kanał łączy strefy swojego conduitu,
a zapora conduitu ma interfejsy w obu strefach.
"""

import re
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[2]
ARCH = KORZEN / "docs/architektura"
STREFY_MD = ARCH / "strefy-i-conduity.md"

POZIOMY_OT = {"L0–L1", "L2", "L3"}
POZIOMY_IT = {"L4"}
SPOSOBY = {"przez conduit", "przez IDMZ", "zablokowany"}


def tabela(plik: Path, naglowek: str, ktora: int = 0) -> list[dict[str, str]]:
    """Wiersze tabeli Markdown nr `ktora` pod nagłówkiem `## <naglowek>`."""
    tekst = plik.read_text(encoding="utf-8")
    sekcja = tekst.split(f"\n## {naglowek}\n", 1)[1].split("\n## ", 1)[0]
    tabele, biezaca = [], []
    for linia in sekcja.splitlines() + [""]:
        if linia.startswith("|"):
            biezaca.append(linia)
        elif biezaca:
            tabele.append(biezaca)
            biezaca = []
    linie = tabele[ktora]
    kolumny = [k.strip() for k in linie[0].strip("|").split("|")]
    return [dict(zip(kolumny, (k.strip() for k in linia.strip("|").split("|")))) for linia in linie[2:]]


def lista(tekst: str) -> list[str]:
    return [i.strip() for i in tekst.split(",") if i.strip() and i.strip() != "—"]


def bez_gwiazdki(identyfikator: str) -> str:
    return identyfikator.rstrip(" *")


INWENTARZ = {a["ID"] for a in tabela(ARCH / "inwentaryzacja-aktywow.md", "Tabela aktywów")}
ENCJE = {e["ID"] for e in tabela(ARCH / "przeplywy-danych.md", "Encje zewnętrzne")}
DFD = {bez_gwiazdki(p["ID"]): p for p in tabela(ARCH / "przeplywy-danych.md", "Tabela przepływów")}

STREFY = {s["ID"]: s for s in tabela(STREFY_MD, "Strefy")}
NOWE = {a["ID"]: a for a in tabela(STREFY_MD, "Nowe i zmienione aktywa")}
ZAPORY = {z["Zapora"]: set(re.findall(r"Z\d+", z["Interfejsy"])) for z in tabela(STREFY_MD, "Zapory")}
CONDUITY = {k["ID"]: k for k in tabela(STREFY_MD, "Conduity")}
KANALY = {bez_gwiazdki(k["ID"]): k for k in tabela(STREFY_MD, "Kanały")}
NOWE_PRZEPLYWY = {n["ID"]: n for n in tabela(STREFY_MD, "Kanały", ktora=1)}
REALIZACJA = {r["Przepływ"]: r for r in tabela(STREFY_MD, "Przepływy z DFD w `v1`")}
DIAGRAM = STREFY_MD.read_text(encoding="utf-8").split("```mermaid\n", 1)[1].split("```", 1)[0]

STREFA = {element: s for s, wiersz in STREFY.items() for element in lista(wiersz["Aktywa"])}
ZAPORY_AKTYWA = {"A07", "A16"}  # fw-it i fw-ot należą do conduitów, nie do stref
ZASTAPIONE = {"A08"}  # wspólna sieć v0, w v1 zastąpiona sieciami stref


def strony(tekst: str) -> tuple[list[str], list[str]]:
    skad, dokad = tekst.split("→")
    return lista(skad), lista(dokad)


def strefy_kanalu(kanal: dict[str, str]) -> set[str]:
    skad, dokad = strony(kanal["Źródło → cel"])
    return {STREFA[e] for e in skad + dokad}


def poziom(strefa: str) -> str:
    return STREFY[strefa]["Purdue"]


def test_kazde_aktywo_jest_w_jednej_strefie():
    elementy = [e for wiersz in STREFY.values() for e in lista(wiersz["Aktywa"])]
    assert len(elementy) == len(set(elementy)), "aktywo w więcej niż jednej strefie"
    oczekiwane = (INWENTARZ | NOWE.keys() | ENCJE) - ZAPORY_AKTYWA - ZASTAPIONE
    assert set(elementy) == oczekiwane


def test_zapory_sa_nowymi_aktywami_bez_strefy():
    assert ZAPORY_AKTYWA <= NOWE.keys()
    assert all(NOWE[a]["Strefa"] == "—" for a in ZAPORY_AKTYWA)
    assert all(NOWE[a]["Strefa"] == STREFA[a] for a in NOWE.keys() - ZAPORY_AKTYWA)


def test_strefy_maja_wlasciciela_poziom_i_siec():
    for s in STREFY.values():
        assert s["Właściciel"] in {"IT", "OT", "zewnętrzna"}
        assert s["Purdue"] in POZIOMY_OT | POZIOMY_IT | {"L3.5", "L5"}
        assert re.fullmatch(r"\d+\.\d+\.\d+\.0/24", s["Sieć v1"])


def test_kazda_strefa_ma_interfejs_zapory():
    assert set(STREFY) == set().union(*ZAPORY.values())


@pytest.mark.parametrize("przeplyw", sorted(DFD), ids=str)
def test_przeplyw_z_dfd_ma_realizacje_w_v1(przeplyw):
    realizacja = REALIZACJA[przeplyw]
    sposob, kanaly = realizacja["W v1"], lista(realizacja["Kanały"])
    skad, dokad = strony(DFD[przeplyw]["Skąd → dokąd"])
    if m := re.fullmatch(r"w strefie (Z\d+)", sposob):
        assert not kanaly
        assert {STREFA[e] for e in skad + dokad} == {m.group(1)}
        return
    assert sposob in SPOSOBY
    if sposob == "zablokowany":
        assert not kanaly
        assert all(przeplyw not in lista(k["Przepływy"]) for k in KANALY.values())
        return
    assert kanaly, f"{przeplyw}: brak kanałów"
    for k in kanaly:
        assert przeplyw in lista(KANALY[k]["Przepływy"]), f"kanał {k} nie wymienia {przeplyw}"
    konce = {e for k in kanaly for e in sum(strony(KANALY[k]["Źródło → cel"]), [])}
    assert set(skad + dokad) <= konce
    if sposob == "przez IDMZ":
        assert any("Z5" in strefy_kanalu(KANALY[k]) for k in kanaly)


def test_realizacja_obejmuje_tylko_przeplywy_z_dfd():
    assert set(REALIZACJA) == set(DFD)


@pytest.mark.parametrize("kanal", sorted(KANALY), ids=str)
def test_kanal_laczy_strefy_swojego_conduitu(kanal):
    k = KANALY[kanal]
    conduit = CONDUITY[k["Conduit"]]
    strefy = strefy_kanalu(k)
    assert len(strefy) == 2, f"{kanal} nie przekracza granicy strefy"
    assert strefy == set(lista(conduit["Strefy"]))
    assert strefy <= ZAPORY[conduit["Zapora"]]
    assert kanal in lista(conduit["Kanały"])
    skad, _ = strony(k["Źródło → cel"])
    assert set(lista(k["Inicjator"])) <= set(skad)
    for p in lista(k["Przepływy"]):
        assert p in DFD or p in NOWE_PRZEPLYWY


def test_conduity_wymieniaja_istniejace_kanaly():
    for k in CONDUITY.values():
        assert set(lista(k["Kanały"])) <= KANALY.keys()


def test_biuro_nie_ma_kanalu_do_ot():
    for kanal, k in KANALY.items():
        poziomy = {poziom(s) for s in strefy_kanalu(k)}
        assert not (poziomy & POZIOMY_IT and poziomy & POZIOMY_OT), f"{kanal} łączy IT z OT"


def test_zadna_zapora_nie_laczy_biura_z_ot():
    for zapora, strefy in ZAPORY.items():
        poziomy = {poziom(s) for s in strefy}
        assert not (poziomy & POZIOMY_IT and poziomy & POZIOMY_OT), f"{zapora} ma interfejsy w IT i w OT"


def test_z_internetu_nie_otwiera_sie_zadne_polaczenie():
    for kanal, k in KANALY.items():
        assert all(poziom(STREFA[e]) != "L5" for e in lista(k["Inicjator"])), kanal


def test_nowe_przeplywy_maja_kanaly():
    for n in NOWE_PRZEPLYWY.values():
        for k in lista(n["Kanały"]):
            assert n["ID"] in lista(KANALY[k]["Przepływy"])


def test_strefy_i_zapory_sa_na_diagramie():
    for s in STREFY:
        assert f'subgraph {s}["{s} ' in DIAGRAM
    for zapora in ZAPORY:
        assert f'"{zapora} (' in DIAGRAM
    for conduit in CONDUITY:
        assert re.search(rf"\b{conduit}\b", DIAGRAM), f"{conduit} nie ma na diagramie"
