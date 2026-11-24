"""Ustawia trasę domyślną przez router labu (zamiast bramy Dockera), potem uruchamia podane polecenie.

Użycie: python -m wtsim.brama <polecenie...>. Adres routera bierze ze zmiennej BRAMA.
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
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
