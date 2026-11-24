# Backlog

Zadania według etapów z instrukcji. Kolumna „Zależy od” to kolejność prac. Etapy nie mają terminów; idziemy tak szybko, jak się da.

## Przygotowanie

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T01 Szkielet repozytorium | README ze statusem projektu, karta projektu, szablon sprawozdań, backlog. | wszyscy | — | w toku |
| T02 Lab `v0`: sieć niebezpieczna | Płaska sieć w Docker Compose odwzorowująca stan as-is, uruchamiana jednym poleceniem. | R1 | T01 | w toku |

## Etapy 1 i 2 — inwentaryzacja i architektura

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T03 Asset Inventory | Tabela aktywów `v0`: funkcja, poziom Purdue, protokoły, dane, właściciel (IT/OT), krytyczność. | R1 | T02 | do zrobienia |
| T04 Data Flow Diagram | Przepływy danych `v0` z protokołami i granicami zaufania. | R1 | T03 | do zrobienia |
| T05 Model Purdue i Zones & Conduits | Docelowy podział na strefy i kanały, z IDMZ na poziomie 3.5. | R1 | T04 | do zrobienia |
| T06 SL-T | Uzasadnienie docelowego poziomu bezpieczeństwa dla każdej strefy. | R1 | T05 | do zrobienia |
| T07 Sprawozdanie Etapów 1–2 | `docs/sprawozdania/etap-1-2.md`. | R1 | T03–T06 | do zrobienia |

## Etap 3 — bezpieczeństwo komunikacji

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T08 Analiza ruchu `v0` | Pcap jawnego MQTT i G-code; dowód podsłuchu i wstrzyknięcia wiadomości. | R2 | T02 | do zrobienia |
| T09 Lab `v1`: segmentacja | Sieci stref, router-zapora z regułami conduitów, IDMZ. | R1 | T05 | do zrobienia |
| T10 PKI i TLS | Własne CA, certyfikaty brokera i klientów, MQTT po TLS. | R2 | T09 | do zrobienia |
| T11 ACL | Uprawnienia do tematów MQTT dla każdego urządzenia. | R2 | T10 | do zrobienia |
| T12 Node-RED gateway | Bramka w IDMZ: lokalny broker → filtrowanie i agregacja → chmura. | R2 | T10 | do zrobienia |
| T13 Analiza ruchu `v1` | Pcap po zabezpieczeniu i porównanie z T08. | R2 | T10–T12 | do zrobienia |
| T14 Sprawozdanie Etapu 3 | `docs/sprawozdania/etap-3.md`. | R2 | T08–T13 | do zrobienia |

## Etap 4 — modelowanie zagrożeń i incydent

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T15 STRIDE i ATT&CK for ICS | Macierz zagrożeń dla przepływów z DFD, mapowanie technik, kontrole w `v1`. | R3 | T04 | do zrobienia |
| T16 Eksperyment: Tampering G-code | Kontrolowana modyfikacja G-code w locie w `v0` i ten sam test w `v1`. | R3 | T02, T09 | do zrobienia |
| T17 Logi incydentu | Obserwowalne ślady incydentu (broker, router, CNC, pcap) jako baza pod AI. | R3 | T16 | do zrobienia |
| T18 Sprawozdanie Etapu 4 | `docs/sprawozdania/etap-4.md`. | R3 | T15–T17 | do zrobienia |

## Etap 5 — Edge AI

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T19 Dane prądu wrzeciona | Generator sygnału, zbiór treningowy (tylko praca normalna) i testowy (normalna i anomalie). | R4 | T02 | do zrobienia |
| T20 Model i kwantyzacja | Model detekcji anomalii, kwantyzacja int8, metryki DR, FPR, opóźnienie detekcji. | R4 | T19 | do zrobienia |
| T21 ESP32 w QEMU | Firmware z modelem, lokalny alarm bez połączenia z chmurą. | R4 | T20 | do zrobienia |
| T22 Sprawozdanie Etapu 5 | `docs/sprawozdania/etap-5.md`. | R4 | T19–T21 | do zrobienia |

## Obrona

| Zadanie | Cel | Rola | Zależy od | Stan |
|---|---|---|---|---|
| T23 Sprawozdanie końcowe | Złożenie sprawozdań cząstkowych w jedno, z ograniczeniami rozwiązania. | wszyscy | T07, T14, T18, T22 | do zrobienia |
| T24 Scenariusz demo | Kolejność pokazu na obronie i polecenia do uruchomienia. | wszyscy | T23 | do zrobienia |

## Rozszerzenia (opcjonalne)

| Zadanie | Cel |
|---|---|
| T25 mTLS | Wzajemne uwierzytelnianie certyfikatami wszystkich klientów MQTT. |
| T26 Drugi scenariusz ataku | Fałszywa komenda wyłączenia odpylania (Unauthorized Command Message). |
| T27 Dashboard bezpieczeństwa | Widok zdarzeń z brokera, routera i detektora w jednym miejscu. |
