# Backlog

Źródłem prawdy są [Issues](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues) i [Milestones](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/milestones); ten plik to migawka na potrzeby przeglądu i sprawozdań. Jeden issue to jeden PR. Kolumna „Zależy od” to kolejność prac. Etapy nie mają terminów.

## Przygotowanie

Szkielet repozytorium, harness i lab v0 (sieć niebezpieczna).

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T01](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/3) Szkielet repozytorium i harness | Repozytorium ma opis projektu ze statusem etapów, kartę projektu, szablon sprawozdań i backlog w Issues, a każda zmiana przechodzi te same kontrole lokalnie i w CI. | — | w toku |
| [T02](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/4) Lab v0: sieć niebezpieczna | Stan as-is ze scenariusza odtworzony w Docker Compose i uruchamiany jednym poleceniem, z testami potwierdzającymi jego celowe słabości. | [T01](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/3) | do zrobienia |

## Etapy 1–2 · Inwentaryzacja i architektura

Asset Inventory, DFD, model Purdue, Zones & Conduits, SL-T. Oddanie: tabela inwentaryzacji i schemat sieci.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T03](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/5) Asset Inventory | Pełna inwentaryzacja aktywów stanu as-is, z której wynikają strefy i poziomy Purdue. | [T02](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/4) | do zrobienia |
| [T04](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/6) Data Flow Diagram | Przepływy danych v0 z protokołami i granicami zaufania jako podstawa STRIDE i reguł zapór. | [T03](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/5) | do zrobienia |
| [T05](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/7) Model Purdue i Zones & Conduits | Docelowy podział sieci na strefy i kanały zgodnie z IEC 62443, z IDMZ na poziomie 3.5. | [T04](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/6) | do zrobienia |
| [T06](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/8) SL-T | Uzasadniony docelowy poziom bezpieczeństwa dla każdej strefy. | [T05](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/7) | do zrobienia |
| [T07](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/9) Sprawozdanie Etapów 1–2 | Sprawozdanie cząstkowe Etapów 1–2 dla prowadzącego. | [T03](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/5), [T04](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/6), [T05](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/7), [T06](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/8) | do zrobienia |

## Etap 3 · Bezpieczeństwo komunikacji

MQTT z TLS, certyfikaty, ACL, segmentacja, Node-RED gateway. Oddanie: Wireshark przed i po, plik ACL.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T08](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/10) Analiza ruchu v0 | Dowód, że w v0 dane i komendy idą jawnym tekstem i dają się podsłuchać oraz wstrzyknąć. | [T02](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/4) | do zrobienia |
| [T09](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/11) Lab v1: segmentacja i zapory | Sieci stref i dwie zapory nftables realizujące conduity z T05. | [T05](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/7) | do zrobienia |
| [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12) PKI i TLS | Własne CA i certyfikaty; MQTT tylko po TLS. | [T09](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/11) | do zrobienia |
| [T11](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/13) ACL MQTT | Każde urządzenie publikuje i czyta tylko swoje tematy. | [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12) | do zrobienia |
| [T12](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/14) Node-RED gateway | Bramka w IDMZ: lokalny broker → filtrowanie i agregacja → chmura. | [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12) | do zrobienia |
| [T13](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/15) Analiza ruchu v1 | Porównanie ruchu po zabezpieczeniu z T08. | [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12), [T11](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/13), [T12](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/14) | do zrobienia |
| [T14](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/16) Sprawozdanie Etapu 3 | Sprawozdanie cząstkowe Etapu 3 dla prowadzącego. | [T08](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/10), [T09](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/11), [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12), [T11](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/13), [T12](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/14), [T13](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/15) | do zrobienia |

## Etap 4 · Zagrożenia i incydent

STRIDE, MITRE ATT&CK for ICS, kontrolowany eksperyment. Oddanie: macierz zagrożeń i logi incydentu.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T15](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/17) STRIDE i MITRE ATT&CK for ICS | Macierz zagrożeń dla przepływów z DFD z mapowaniem na techniki ATT&CK for ICS i kontrolami w v1. | [T04](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/6) | do zrobienia |
| [T16](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/18) Eksperyment: Tampering G-code | Kontrolowana modyfikacja G-code w locie w v0 i ten sam test w v1. | [T02](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/4), [T09](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/11) | do zrobienia |
| [T17](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/19) Logi incydentu | Obserwowalne ślady incydentu jako baza pod AI. | [T16](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/18) | do zrobienia |
| [T18](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/20) Sprawozdanie Etapu 4 | Sprawozdanie cząstkowe Etapu 4 dla prowadzącego. | [T15](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/17), [T16](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/18), [T17](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/19) | do zrobienia |

## Etap 5 · Edge AI

Dane prądu wrzeciona, model TinyML w Edge Impulse, kwantyzacja, alarm lokalny na ESP32. Oddanie: metryki DR, FPR, opóźnienie.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T19](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/21) Dane prądu wrzeciona | Zbiory treningowy (tylko praca normalna) i testowy (normalna i anomalie) do Edge Impulse. | [T02](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/4) | do zrobienia |
| [T20](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/22) Model TinyML w Edge Impulse | Model detekcji anomalii prądowych, kwantyzacja int8, metryki. | [T19](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/21) | do zrobienia |
| [T21](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/23) ESP32 w QEMU | Firmware z modelem na emulowanym ESP32 z lokalnym alarmem bez chmury. | [T20](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/22) | do zrobienia |
| [T22](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/24) Sprawozdanie Etapu 5 | Sprawozdanie cząstkowe Etapu 5 dla prowadzącego. | [T19](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/21), [T20](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/22), [T21](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/23) | do zrobienia |

## Obrona

Sprawozdanie końcowe, ograniczenia rozwiązania, demo.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T23](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/25) Sprawozdanie końcowe | Jedno sprawozdanie złożone ze sprawozdań cząstkowych. | [T07](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/9), [T14](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/16), [T18](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/20), [T22](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/24) | do zrobienia |
| [T24](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/26) Scenariusz demo | Kolejność pokazu na obronie i polecenia do uruchomienia. | [T23](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/25) | do zrobienia |

## Rozszerzenia

Zadania rozszerzone podwyższające ocenę.

| Zadanie | Cel | Zależy od | Stan |
|---|---|---|---|
| [T25](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/27) mTLS | Wzajemne uwierzytelnianie certyfikatami wszystkich klientów MQTT. | [T10](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/12) | do zrobienia |
| [T26](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/28) Drugi scenariusz ataku: wyłączenie odpylania | Fałszywa komenda wyłączenia odpylania (Unauthorized Command Message). | [T16](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/18) | do zrobienia |
| [T27](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/29) Dashboard bezpieczeństwa | Zdarzenia z brokera, zapór i detektora w jednym widoku. | [T17](https://github.com/l3x1cn/Iot-Ot-Wood-Tech-CNC/issues/19) | do zrobienia |
