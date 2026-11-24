"""Lista połączeń widocznych w ruchu labu, do porównania z tabelą przepływów (docs/architektura).

Czyta ze standardowego wejścia wyjście tcpdump ograniczone do początków połączeń TCP (SYN) i datagramów UDP
i wypisuje każde połączenie raz: protokół, strona inicjująca → serwer:port, liczba połączeń albo datagramów.

    tcpdump -nn -q -r plik.pcap 'tcp[tcpflags] == tcp-syn or udp' | python3 scripts/przeplywy.py

`make v0-przeplywy PCAP=plik.pcap` robi to samo.
"""

import re
import sys
from collections import Counter

# Format tcpdump -nn -q: "... IP 10.10.0.41.51234 > 10.10.0.31.80: tcp 0"
PAKIET = re.compile(r"IP (\d+\.\d+\.\d+\.\d+)\.\d+ > (\d+\.\d+\.\d+\.\d+)\.(\d+): (tcp|udp)\b")


def polaczenia(linie) -> Counter:
    licznik: Counter = Counter()
    for linia in linie:
        if m := PAKIET.search(linia):
            src, dst, port, proto = m.groups()
            licznik[(proto, src, dst, int(port))] += 1
    return licznik


def main() -> None:
    for (proto, src, dst, port), ile in sorted(polaczenia(sys.stdin).items()):
        print(f"{proto} {src} -> {dst}:{port} {ile}")


if __name__ == "__main__":
    main()
