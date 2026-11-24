# Etap 3: analiza ruchu

## T08 · Ruch `v0` przed zabezpieczeniem

Dowód, że w sieci niebezpiecznej dane i komendy idą jawnym tekstem: da się je podsłuchać, a komendy wstrzyknąć z przejętego komputera biurowego. Wszystko z tego katalogu powstaje jednym poleceniem na wyłączonym labie:

```bash
make v0-down
make v0-analiza   # ok. 2 min: nagranie, scenariusz z biura, zrzuty, zatrzymanie labu
```

Skrypt [scripts/analiza_v0.sh](../../scripts/analiza_v0.sh) startuje lab `v0` razem z `biuro-pc` i od pierwszego pakietu nagrywa oba mosty Dockera przez 110 s. Most `wt0-zaklad` to sieć zakładu, czyli to, co widzi Wireshark na porcie lustrzanym przełącznika. Most `wt0-internet` to łącze do chmury za NAT routera, czyli to, co widzi każdy na drodze do brokera. W tym czasie stacja CAD wysyła G-code na obie obrabiarki, a z biura idzie scenariusz:

| Sekunda od startu | Z biura (`biuro-pc`, 10.10.0.66) | Słabość `v0` |
|---|---|---|
| 40 | anonimowa subskrypcja wszystkich tematów brokera (`#`) | 2, 3 |
| 45 | odczyt rejestrów i cewek PLC odpylania, wyłączenie wentylatora, po 5 s ponowne włączenie | 1, 5 |
| 68 | komenda `STOP` dla `cnc-1` w trakcie programu | 2, 3 |
| 78 | komenda `START` dla `cnc-1` | 2, 3 |

Numery słabości są z [lab/README.md](../../lab/README.md) („Celowe słabości v0”). Zrzuty robi tshark z obrazu `biuro-pc`, czyli Wireshark w wierszu poleceń z tymi samymi dekoderami protokołów. Każdy zrzut ma na początku nagranie i filtr, którym ten sam widok otwiera się w Wiresharku. Pod listą ramek są szczegóły jednej ramki i jej bajty, jak w dolnych panelach Wiresharka.

### Pliki

Kolumna „Fragment w pliku” to teksty, które test [test_dowody_etap_3.py](../../tests/dokumentacja/test_dowody_etap_3.py) znajduje w pliku po każdym nagraniu.

| Plik | Co widać | Fragment w pliku |
|---|---|---|
| `v0-zaklad.pcap` | cały ruch sieci zakładu w czasie scenariusza: telemetria, G-code, Modbus i komendy z biura | — |
| `v0-internet.pcap` | ruch zakładu do brokera w chmurze; wszystkie urządzenia, także biuro, mają ten sam adres NAT 203.0.113.2 | — |
| `zrzut-1-telemetria-mqtt.txt` | telemetria wrzeciona `cnc-1` w internecie jako jawny JSON: stan pracy, nazwa i SHA-256 programu, obroty, prąd i temperatura | `Topic: wood-tech/hala1/cnc-1/telemetria`, `"pracuje": true`, `"sha256"` |
| `zrzut-2-gcode-http.txt` | pełny program G-code wysłany ze stacji CAD na `cnc-1` w żądaniu HTTP bez uwierzytelnienia, z nazwą pliku w nagłówku i odpowiedzią obrabiarki | `POST /program HTTP/1.1`, `X-Program: blat-stolu.nc`, `M3 S18000`, `"sha256"` |
| `zrzut-3-modbus.txt` | biuro czyta rejestry i cewki PLC odpylania i zapisuje cewkę 0 (wentylator); PLC przyjmuje zapis od każdego, kto zna adres | `Read Holding Registers`, `Write Single Coil`, `Src: 10.10.0.66, Dst: 10.10.0.21` |
| `zrzut-4-wstrzykniecie-mqtt.txt` | `cnc-1` subskrybuje swój temat komend, biuro publikuje w nim `STOP` i `START`, a broker przekazuje obie komendy obrabiarce | `Src: 10.10.0.66, Dst: 203.0.113.10`, `Topic: wood-tech/hala1/cnc-1/komenda`, `Message: STOP` |
| `zrzut-5-podsluch-mqtt.txt` | biuro łączy się z brokerem bez nazwy użytkownika i hasła i subskrybuje wszystkie tematy | `User Name Flag: Not set`, `Password Flag: Not set`, `Subscribe Request`, `Topic: #` |
| `konsola-biuro-pc.txt` | polecenia atakującego i ich wyniki: odebrana telemetria maszyn i odpylania, wartości rejestrów PLC przed wyłączeniem wentylatora i po nim, wysłane komendy | `mosquitto_sub`, `wood-tech/hala1/odpylanie/stan`, `zapis cewki 0 = 0: wentylator wylaczony` |
| `logi-labu.txt` | skutki po stronie urządzeń: obrabiarka wykonuje `STOP` i `START` z biura, PLC loguje wyłączenie wentylatora, broker przyjmuje anonimowych klientów z tego samego adresu co maszyny | `"zdarzenie": "komenda_mqtt"`, `"komenda": "STOP"`, `"wentylator": false`, `"nadawca": "10.10.0.41"` |

### Co z tego wynika

- **Poufność.** Telemetria, G-code i stan odpylania są czytelne bez żadnych kluczy, zarówno w sieci zakładu, jak i w internecie. G-code to projekt mebla, czyli własność intelektualna eksportera. Telemetria zdradza, który program i kiedy pracuje.
- **Uwierzytelnienie.** Broker przyjmuje klienta bez nazwy i hasła, a PLC przyjmuje zapis Modbus od każdego. Broker nie odróżni biura od maszyn nawet po adresie, bo za NAT wszystkie mają 203.0.113.2.
- **Integralność.** Nic nie chroni treści w drodze. Obrabiarka podaje SHA-256 odebranego programu, ale tylko w odpowiedzi i telemetrii, które też idą jawnie, więc podmieniony program z przeliczonym skrótem jest nie do odróżnienia. Podmianę w locie pokaże T16.
- **Komendy.** Jedna wiadomość MQTT z biura zatrzymuje obrabiarkę w trakcie programu i ją uruchamia, a jeden zapis Modbus wyłącza odpylanie. W `v1` blokują to strefy i zapory (T09), TLS (T10) i ACL brokera (T11). Komendy z chmury nie mają w `v1` drogi do maszyn (F02, F07 w [modelu stref](../../docs/architektura/strefy-i-conduity.md)), a `START` i `STOP` wydaje tylko operator z panelu (N01).
- **Punkt obserwacji.** Nagranie z mostu Dockera odpowiada portowi lustrzanemu. Atakujący w płaskiej sieci może zdobyć ten sam widok przez ARP spoofing (`arpspoof` w `biuro-pc`), co wykorzystuje T16. Analiza ruchu po zabezpieczeniu (T13) powtórzy ten scenariusz na labie `v1`.

### W Wiresharku

Pliki pcap otwierają się wprost w Wiresharku (Plik → Otwórz), a filtr z nagłówka zrzutu wpisuje się w pole filtra wyświetlania. Dla G-code: prawy przycisk na ramce `POST /program` → Śledź → Strumień TCP. Zrzuty ekranu do sprawozdania robimy z tych widoków.
