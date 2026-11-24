"""SL-T (T06) musi obejmować każdą strefę i każdy conduit z T05 i trzymać się reguły z dokumentu.

Test czyta docs/architektura/sl-t.md, strefy-i-conduity.md i inwentaryzacja-aktywow.md. Pilnuje, żeby:
- każda strefa z T05 miała wektor FR1–FR7, SL-T, atakującego i uzasadnienie (kryterium akceptacji T06),
- SL-T strefy był najwyższą wartością wektora, a SL-T conduitu wyższym z SL-T łączonych stref,
- strefy systemu sterowania miały SL-T co najmniej 2, strefa z aktywem krytycznym miała FR na poziomie 3,
  a strefa internetu SL-T 0.
"""

import re
from pathlib import Path

import pytest

ARCH = Path(__file__).resolve().parents[2] / "docs/architektura"
FR = [f"FR{i}" for i in range(1, 8)]
SYSTEM_STEROWANIA = {"L0–L1", "L2", "L3", "L3.5"}


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


STREFY = {s["ID"]: s for s in tabela(ARCH / "strefy-i-conduity.md", "Strefy")}
CONDUITY = {k["ID"]: k for k in tabela(ARCH / "strefy-i-conduity.md", "Conduity")}
KRYTYCZNOSC = {a["ID"]: a["Krytyczność"] for a in tabela(ARCH / "inwentaryzacja-aktywow.md", "Tabela aktywów")}

SL_T = {s["Strefa"]: s for s in tabela(ARCH / "sl-t.md", "SL-T stref")}
SL_T_CONDUITOW = {k["Conduit"]: k for k in tabela(ARCH / "sl-t.md", "SL-T conduitów")}
PROFILE = {p["Profil"] for p in tabela(ARCH / "sl-t.md", "Metoda")}
LUKA = {w["FR"]: w for w in tabela(ARCH / "sl-t.md", "Luka: stan `v0` i co ją zamyka")}


def wektor(strefa: str) -> list[int]:
    return [int(SL_T[strefa][fr]) for fr in FR]


def test_kazda_strefa_z_t05_ma_sl_t():
    assert set(SL_T) == set(STREFY)


@pytest.mark.parametrize("strefa", sorted(STREFY), ids=str)
def test_wektor_sl_t_i_uzasadnienie(strefa):
    wiersz = SL_T[strefa]
    assert all(0 <= v <= 4 for v in wektor(strefa))
    assert int(wiersz["SL-T"]) == max(wektor(strefa))
    assert set(lista(wiersz["Atakujący"])) <= PROFILE
    assert len(wiersz["Uzasadnienie"]) > 40


@pytest.mark.parametrize("strefa", sorted(STREFY), ids=str)
def test_regula_z_metody(strefa):
    sl_t = int(SL_T[strefa]["SL-T"])
    if STREFY[strefa]["Purdue"] in SYSTEM_STEROWANIA:
        assert sl_t >= 2, f"{strefa} należy do systemu sterowania, a ma SL-T {sl_t}"
        assert lista(SL_T[strefa]["Atakujący"]), f"{strefa}: brak atakującego"
    aktywa = [a for a in lista(STREFY[strefa]["Aktywa"]) if a in KRYTYCZNOSC]
    if STREFY[strefa]["Purdue"] in SYSTEM_STEROWANIA and any(KRYTYCZNOSC[a] == "Krytyczna" for a in aktywa):
        assert 3 in wektor(strefa), f"{strefa} ma aktywo krytyczne, a żaden FR nie ma poziomu 3"
    if STREFY[strefa]["Purdue"] == "L5":
        assert sl_t == 0


def test_kazdy_conduit_ma_sl_t_wyzszej_strefy():
    assert set(SL_T_CONDUITOW) == set(CONDUITY)
    for conduit, wiersz in SL_T_CONDUITOW.items():
        strefy = lista(CONDUITY[conduit]["Strefy"])
        assert lista(wiersz["Strefy"]) == strefy
        assert int(wiersz["SL-T"]) == max(int(SL_T[s]["SL-T"]) for s in strefy)


def test_luka_obejmuje_wszystkie_fr():
    assert list(LUKA) == FR
    for wiersz in LUKA.values():
        assert re.match(r"[0-4]: ", wiersz["SL-A w `v0`"])
