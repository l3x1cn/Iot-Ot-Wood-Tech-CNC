"""Ustawia trasę domyślną przez router labu (zamiast bramy Dockera), porzuca uprawnienia roota
i uruchamia podane polecenie jako użytkownik `sim` (UID 10001).

Użycie: python -m wtsim.brama <polecenie...>. Adres routera bierze ze zmiennej BRAMA.
Root jest potrzebny tylko do zmiany trasy (CAP_NET_ADMIN); sam symulator działa bez niego.
"""

import os
import sys

from pyroute2 import IPRoute


def main() -> None:
    brama = os.environ.get("BRAMA")
    if brama:
        with IPRoute() as ip:
            ip.route("replace", dst="0.0.0.0/0", gateway=brama)
        print(f"brama: trasa domyslna przez {brama}", flush=True)
    if os.getuid() == 0:
        uid = int(os.environ.get("SIM_UID", "10001"))
        os.setgroups([])
        os.setgid(uid)
        os.setuid(uid)
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
