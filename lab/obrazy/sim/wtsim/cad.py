"""Stacja CAD/CAM: cyklicznie pobiera projekty z serwera plików i wysyła G-code na obrabiarki.

W v0 oba przepływy (serwer → stacja, stacja → CNC) idą jawnym HTTP bez uwierzytelnienia
i bez kontroli integralności. Stacja loguje SHA-256 wysłanego pliku, a CNC loguje SHA-256 odebranego,
więc porównanie logów pokazuje, czy plik zmienił się po drodze.
"""

import hashlib
import itertools
import os
import time
import urllib.request

from wtsim.wspolne import log

STACJA = "cad-stacja"
SERWER = os.environ.get("SERWER_URL", "http://serwer/projekty")
ZADANIA = [z.split("=") for z in os.environ.get("ZADANIA", "cnc-1=blat-stolu.nc,cnc-2=front-szafki.nc").split(",")]
OKRES = float(os.environ.get("OKRES", "60"))


def main() -> None:
    log(STACJA, "start", serwer=SERWER, zadania=ZADANIA, okres_s=OKRES)
    for cnc, plik in itertools.cycle(ZADANIA):
        try:
            with urllib.request.urlopen(f"{SERWER}/{plik}", timeout=5) as odp:
                gcode = odp.read()
            skrot = hashlib.sha256(gcode).hexdigest()
            zadanie = urllib.request.Request(
                f"http://{cnc}:8080/program", data=gcode, method="POST", headers={"X-Program": plik}
            )
            with urllib.request.urlopen(zadanie, timeout=5) as odp:
                odpowiedz = odp.read().decode()
            log(STACJA, "program_wyslany", cnc=cnc, nazwa=plik, sha256=skrot, odpowiedz=odpowiedz)
        except OSError as blad:
            log(STACJA, "blad_wysylki", cnc=cnc, nazwa=plik, blad=str(blad))
        time.sleep(OKRES / len(ZADANIA))


if __name__ == "__main__":
    main()
