# Karta projektu

## Scenariusz

Nr 4 — Średnie: zautomatyzowana fabryka mebli „Wood-Tech CNC”.

- **Profil firmy:** fabryka eksportująca meble. IT jest outsourcowane, za maszyny odpowiadają lokalni automatycy; między IT i OT narasta konflikt kompetencyjny.
- **Infrastruktura:** obrabiarki CNC podłączone do sieci zakładowej, centralny system odpylania sterowany przez PLC, współdzielona serwerownia, urządzenia wysyłające dane MQTT bezpośrednio do chmury bez lokalnej bramki.
- **Dane:** projekty CAD (i wynikowy G-code), harmonogramy produkcji, parametry pracy wrzecion CNC.
- **Zadania ze scenariusza:**
  1. uporządkowanie architektury według modelu Purdue;
  2. Node-RED jako warstwa integracyjna (gateway) między maszynami a chmurą;
  3. modelowanie zagrożeń dla ataku typu Tampering (modyfikacja projektów CAD w locie);
  4. model TinyML przy maszynach do detekcji anomalii prądowych.

## Zakres

Wszystko działa w symulacji, w Docker Compose na jednej maszynie wirtualnej (Debian, 8 GB RAM, 4 CPU).

| Element | `v0` — sieć niebezpieczna (as-is) | `v1` — sieć zabezpieczona (to-be) |
|---|---|---|
| Sieć | jedna płaska sieć dla biura, serwerowni i hali | osobne sieci według poziomów Purdue (0–1, 2, 3, 3.5 IDMZ, 4–5) |
| Router | kontener z nftables: NAT do „internetu”, bez filtrowania | ten sam router jako zapora między strefami; drugi firewall wydziela IDMZ |
| CNC i PLC | symulatory CNC (telemetria wrzeciona, odbiór G-code) i PLC odpylania (Modbus TCP) | bez zmian w logice, za to w strefie komórki |
| MQTT | maszyny piszą wprost do brokera „w chmurze”, port 1883, bez hasła i TLS | lokalny broker z TLS i ACL; do chmury dane wychodzą tylko przez Node-RED w IDMZ |
| G-code | przesyłany jawnym protokołem ze stacji CAD | kanał szyfrowany i weryfikacja integralności pliku |
| ESP32 | — | emulowany w QEMU, model anomalii prądu, lokalny alarm bez chmury |

## Kryteria oceny → dowód

| Kryterium (waga) | Dowód w repozytorium |
|---|---|
| Architektura OT i model bezpieczeństwa (25%) | tabela inwentaryzacji, DFD, schemat Purdue, Zones & Conduits, uzasadnienie SL-T (Etapy 1–2) |
| Bezpieczeństwo komunikacji (25%) | `mosquitto.conf`, plik ACL, certyfikaty z własnego CA, pcap i zrzuty z Wiresharka przed i po (Etap 3) |
| Modelowanie zagrożeń i incydent (20%) | macierz STRIDE z mapowaniem na ATT&CK for ICS, przebieg eksperymentu, logi ze śladami incydentu (Etap 4) |
| Edge AI (20%) | opis danych i podziału na zbiory, model, metryki DR, FPR i opóźnienia detekcji, alarm na emulowanym ESP32 (Etap 5) |
| Obrona (10%) | sprawozdanie końcowe z ograniczeniami rozwiązania, scenariusz demo |

## Ryzyka

| # | Ryzyko | Ograniczenie |
|---|---|---|
| 1 | Lab nie mieści się w 8 GB RAM | lekkie obrazy (Alpine, Python slim), limity pamięci w Compose; cel: `v1` poniżej ok. 4 GB |
| 2 | Atak w labie wycieka poza sieci Dockera | sieci wewnętrzne bez dostępu do sieci hosta; atakujący tylko wewnątrz labu |
| 3 | Emulacja ESP32 w QEMU nie obsłuży modelu | mały model (int8), w razie problemów firmware na emulatorze z ograniczonym zestawem peryferiów |
