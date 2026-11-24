# Iot-Ot-Wood-Tech-CNC

Cyber-Ochrona IoT/OT — projekt laboratoryjny, Scenariusz 4: zautomatyzowana fabryka mebli „Wood-Tech CNC”.

Całe środowisko jest symulowane w Dockerze na jednej maszynie wirtualnej z Debianem (8 GB RAM, 4 CPU): obrabiarki CNC, PLC odpylania, węzeł ESP32 z czujnikiem prądu, router, broker MQTT, bramka Node-RED i „chmura”. Pracujemy w dwóch krokach: najpierw stawiamy sieć celowo niebezpieczną (`v0`, stan as-is z opisu scenariusza), szukamy w niej podatności i atakujemy ją, a potem budujemy wersję zabezpieczoną (`v1`) i powtarzamy te same testy.

- Karta projektu (zespół, scenariusz, zakres, kryteria oceny): [docs/karta-projektu.md](docs/karta-projektu.md)
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

## Jak pracujemy

- Każde zadanie to `Txx` z [backlogu](docs/backlog.md). Gałąź `txx-krotki-opis`, PR do `main`.
- PR kończący etap aktualizuje tabelę „Status projektu” i dodaje sprawozdanie cząstkowe według [szablonu](docs/sprawozdania/README.md).
- Dowody (pliki pcap, logi, zrzuty ekranu) trafiają do `evidence/<etap>/` i są linkowane ze sprawozdania.
- Materiały prowadzącego (PDF, dashboard) traktujemy jako punkt odniesienia; numeracja etapów jest zgodna z PDF.
