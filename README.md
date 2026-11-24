# Iot-Ot-Wood-Tech-CNC

Cyber-Ochrona IoT/OT — projekt laboratoryjny, Scenariusz 4: zautomatyzowana fabryka mebli „Wood-Tech CNC”.

Całe środowisko jest symulowane w Dockerze na jednej maszynie wirtualnej z Debianem (8 GB RAM, 4 CPU): obrabiarki CNC, PLC odpylania, węzeł ESP32 z czujnikiem prądu, router, broker MQTT, bramka Node-RED i „chmura”. Pracujemy w dwóch krokach: najpierw stawiamy sieć celowo niebezpieczną (`v0`, stan as-is z opisu scenariusza), szukamy w niej podatności i atakujemy ją, a potem budujemy wersję zabezpieczoną (`v1`) i powtarzamy te same testy.

- Karta projektu (zespół, scenariusz, zakres, kryteria oceny): [docs/karta-projektu.md](docs/karta-projektu.md)
- Lab (topologia, uruchomienie, Wireshark): [lab/README.md](lab/README.md)
- Zadania według etapów: [docs/backlog.md](docs/backlog.md)
- Sprawozdania cząstkowe: [docs/sprawozdania/](docs/sprawozdania/)

## Status projektu

> Po każdym etapie oddajemy prowadzącemu sprawozdanie cząstkowe. Sprawozdania cząstkowe są w [docs/sprawozdania/](docs/sprawozdania/), a na końcu składamy je w jedno sprawozdanie końcowe.

| Etap | Zakres | Stan | Sprawozdanie cząstkowe |
|---|---|---|---|
| Przygotowanie | szkielet repozytorium, lab `v0` (sieć niebezpieczna) | w toku | — |
| Etap 1 | inwentaryzacja aktywów (Asset Inventory), Data Flow Diagram | do zrobienia | — |
| Etap 2 | model Purdue, strefy i kanały (Zones & Conduits), granice zaufania, SL-T | do zrobienia | — |
| Etap 3 | bezpieczeństwo komunikacji: MQTT z TLS, certyfikaty, ACL, Wireshark przed i po | do zrobienia | — |
| Etap 4 | STRIDE, MITRE ATT&CK for ICS, kontrolowany incydent (Tampering G-code), logi | do zrobienia | — |
| Etap 5 | Edge AI: dane prądu wrzeciona, model TinyML, kwantyzacja, alarm lokalny na ESP32 | do zrobienia | — |
| Obrona | sprawozdanie końcowe, ograniczenia rozwiązania, demo | do zrobienia | — |

## Przygotowanie środowiska

Wymagania: Debian z Docker Engine i pluginem compose (użytkownik w grupie `docker`), [mise](https://mise.jdx.dev/getting-started.html) 2026.10.25 lub nowsze, git, GNU make, tcpdump, openssl. Szczegóły: [lab/README.md](lab/README.md#wymagania-debian).

```bash
mise install                  # narzędzia w wersjach z mise.toml
make doctor                   # narzędzia, Docker bez sudo, compose, pamięć
uv sync                       # Python 3.13 i zależności w .venv
uvx pre-commit@4.7.0 install  # hook gitleaks przed commitem, raz po klonie
```

## Szybki start

```bash
make v0-up-atak      # sieć niebezpieczna v0 z przejętym komputerem biurowym
make test-security   # testy potwierdzające podatności v0 (raport w reports/)
make v0-mqtt         # telemetria widoczna w brokerze „w chmurze”
make v0-down
```

## Jak pracujemy

- Każde zadanie to `Txx` z [backlogu](docs/backlog.md). Gałąź `txx-krotki-opis`, PR do `main`.
- Przed PR: `make lint unit gitleaks trivy-config` (te same kontrole co CI). Zmiany w labie: także `make v0-up-atak test-security` (job `e2e` w CI).
- Klucze prywatne i hasła nigdy nie trafiają do repozytorium: blokuje je hook gitleaks i job `secrets`.
- PR kończący etap aktualizuje tabelę „Status projektu” i dodaje sprawozdanie cząstkowe według [szablonu](docs/sprawozdania/README.md).
- Dowody (pliki pcap, logi, zrzuty ekranu) trafiają do `evidence/<etap>/` i są linkowane ze sprawozdania.
- Materiały prowadzącego (PDF, dashboard) traktujemy jako punkt odniesienia; numeracja etapów jest zgodna z PDF.
