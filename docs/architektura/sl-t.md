# Docelowe poziomy bezpieczeństwa (SL-T)

Etap 2, zadanie T06. Dla każdej strefy z [modelu stref i conduitów](strefy-i-conduity.md) (T05) ustalamy docelowy poziom bezpieczeństwa SL-T według IEC 62443-3-2 i uzasadniamy go skutkiem ataku i typem atakującego, przed którym strefa ma się obronić. SL-T podajemy jako wektor siedmiu wymagań podstawowych (FR) z IEC 62443-3-3, bo strefy potrzebują różnej ochrony w różnych obszarach: PLC odpylania nie ma tajemnic, ale musi działać, a projekty CAD odwrotnie.

## Poziomy i wymagania podstawowe

| SL | Przed kim chroni (IEC 62443-3-3) |
|---|---|
| 0 | brak szczególnych wymagań; u nas strefy niezaufane |
| 1 | przypadkowe albo niezamierzone naruszenie |
| 2 | celowe naruszenie prostymi środkami: małe zasoby, ogólna wiedza, niska motywacja |
| 3 | celowe naruszenie zaawansowanymi środkami: średnie zasoby, wiedza o systemach sterowania, umiarkowana motywacja |
| 4 | jak 3, ale z dużymi zasobami i wysoką motywacją |

| FR | Wymaganie podstawowe | Czego dotyczy u nas |
|---|---|---|
| FR1 | identyfikacja i uwierzytelnianie (IAC) | kto łączy się z brokerem, PLC i obrabiarką |
| FR2 | kontrola użycia (UC) | kto może wydać START/STOP, zapisać cewkę PLC, wysłać program |
| FR3 | integralność systemu (SI) | czy program G-code i komendy dochodzą niezmienione |
| FR4 | poufność danych (DC) | projekty CAD, G-code, telemetria |
| FR5 | ograniczony przepływ danych (RDF) | segmentacja, zapory, conduity z T05 |
| FR6 | reakcja na zdarzenia (TRE) | logi zapór i brokera, wykrywanie incydentu |
| FR7 | dostępność zasobów (RA) | praca odpylania i maszyn mimo awarii albo ataku |

## Metoda

**Atakujący.** Profile wynikają ze scenariusza: eksporter mebli z outsourcowanym IT, biurem z pocztą i projektami wartymi dla konkurencji.

| Profil | Kto | Typowy atak | SL, który go zatrzymuje |
|---|---|---|---|
| P1 | pracownik, który się pomylił; nieukierunkowane złośliwe oprogramowanie | zła konfiguracja, zainfekowany pendrive | 1 |
| P2 | cyberprzestępca z gotowymi narzędziami | phishing w biurze, ransomware, skanowanie i znane podatności | 2 |
| P3 | atakujący ukierunkowany z wiedzą o systemach sterowania: szpieg przemysłowy konkurencji, sabotażysta, były automatyk | kradzież projektów, podmiana G-code w locie, fałszywe komendy Modbus i MQTT | 3 |
| P4 | grupa państwowa | długotrwała kampania z własnymi narzędziami | 4: poza zakresem, fabryka mebli nie jest infrastrukturą krytyczną |

**Skutek.** Bierzemy najgorszy realny skutek dla aktywów strefy, w skali krytyczności z [inwentaryzacji](inwentaryzacja-aktywow.md) (T03).

**Reguła.**

1. Strefy systemu sterowania (Z1–Z5) mają SL-T co najmniej 2: bronią się przed P2, bo przejęcie biura phishingiem to najbardziej prawdopodobny początek ataku. Pojedynczy FR może być niżej, gdy strefa nie ma w nim czego chronić, np. poufności stanu odpylania.
2. FR podnosimy do 3, gdy P3 ma w strefie cel wart wysiłku albo skutkiem jest zagrożenie dla ludzi. Strefa z aktywem o krytyczności „Krytyczna” ma co najmniej jeden FR na poziomie 3.
3. Strefy IT (Z6, Z7) nie należą do systemu sterowania. Zakładamy, że mogą zostać przejęte, więc OT nie może polegać na ich ochronie.
4. Strefa internetu (Z8) jest niezaufana i ma SL-T 0.

## SL-T stref

| Strefa | FR1 | FR2 | FR3 | FR4 | FR5 | FR6 | FR7 | SL-T | Atakujący | Uzasadnienie |
|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | P3 | podmieniony G-code daje wadliwe wyroby i może przeciążyć wrzeciono, a niespodziewany START zagraża operatorowi; Tampering G-code to główne zagrożenie scenariusza, więc integralność (FR3) i kontrola komend (FR2) na poziomie 3 |
| Z2 | 3 | 3 | 3 | 1 | 3 | 2 | 3 | 3 | P3 | wyłączenie odpylania grozi wybuchem pyłu, to jedyne zagrożenie dla ludzi; poziom 3 dla wszystkiego, co pozwala sterować wentylatorem albo go zatrzymać (FR1, FR2, FR3, FR5, FR7); stan odpylania nie jest tajemnicą (FR4 = 1) |
| Z3 | 2 | 3 | 2 | 1 | 2 | 2 | 2 | 3 | P3 | panele są jedynym miejscem, z którego wolno sterować odpylaniem i wydać START/STOP, więc kontrola użycia (FR2) jak w strefach, którymi sterują; same panele nie przechowują tajemnic |
| Z4 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | P3 | stąd programy trafiają na maszyny (integralność G-code krytyczna, FR3), a projekty CAD to własność intelektualna eksportera i cel szpiegostwa (FR4); przestój stacji ma obejście ręczne |
| Z5 | 3 | 2 | 2 | 2 | 3 | 2 | 1 | 3 | P2, P3 | jedyny styk z internetem i biurem, więc pierwszy cel po przejęciu biura; poziom 3 dla uwierzytelniania bramki (FR1) i ograniczania przepływów (FR5); awaria IDMZ odcina tylko chmurę, a produkcja trwa (FR7 = 1) |
| Z6 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | P2 | biuro jest poza systemem sterowania; zakładamy, że phishing je przejmie, dlatego OT chroni granica (fw-it, IDMZ), a nie biuro; konta i pocztę zabezpiecza IT poza IEC 62443 |
| Z7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | prywatne telefony poza kontrolą zakładu; traktujemy je jak internet |
| Z8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | internet i chmura poza kontrolą zakładu; dlatego żaden kanał z Z8 nie otwiera połączenia do zakładu (T05) |

Kolumna SL-T to najwyższa wartość wektora, czyli najsilniejszy atakujący, przed którym strefa musi się obronić w którymś obszarze.

## SL-T conduitów

Conduit musi chronić przepływ co najmniej tak jak lepiej chroniona ze stref, które łączy, więc dostaje wyższy z ich SL-T.

| Conduit | Strefy | SL-T |
|---|---|---|
| K1 | Z4, Z1 | 3 |
| K2 | Z4, Z2 | 3 |
| K3 | Z3, Z2 | 3 |
| K4 | Z3, Z4 | 3 |
| K5 | Z5, Z4 | 3 |
| K6 | Z5, Z8 | 3 |
| K7 | Z6, Z5 | 3 |
| K8 | Z6, Z8 | 1 |
| K9 | Z7, Z8 | 0 |

## Luka: stan `v0` i co ją zamyka

W `v0` cały zakład to jedna strefa bez kontroli, więc osiągnięty poziom (SL-A) jest prawie wszędzie zerowy. Tabela pokazuje, które zadania podnoszą każdy FR i co zostaje poniżej SL-T.

| FR | SL-A w `v0` | Co podnosi poziom w `v1` | Co zostaje poniżej SL-T |
|---|---|---|---|
| FR1 | 0: broker anonimowy, Modbus i HTTP bez uwierzytelnienia | certyfikaty i TLS (T10), konta urządzeń (T11), mTLS (T25) | Modbus z natury nie uwierzytelnia; PLC chroni tylko conduit K3 z jednym klientem (środek kompensacyjny) |
| FR2 | 0: każdy publikuje komendy i zapisuje cewki | ACL brokera (T11), komendy tylko z panelu (N01), kanał C05 jako jedyny dostęp do PLC | panel HMI jest poza symulacją, więc FR2 strefy Z3 opisujemy, ale nie testujemy |
| FR3 | 0: brak kontroli integralności | TLS na MQTT (T10) | G-code idzie jawnym HTTP (C01); sprawdzanie integralności programu przez obrabiarkę rozważy T15 i T16 |
| FR4 | 0: wszystko jawnym tekstem | TLS na MQTT (T10), serwer projektów dostępny tylko w Z4 (T09) | G-code w C01 jawny wewnątrz OT |
| FR5 | 0: jedna płaska sieć | strefy i zapory z polityką drop (T09), bramka w IDMZ (T12) | ruch wewnątrz strefy nie jest filtrowany |
| FR6 | 0: brak logów bezpieczeństwa | logi odrzuconych pakietów na zaporach (T09), logi incydentu (T17), dashboard (T27) | brak stałego monitoringu i reagowania w labie |
| FR7 | 1: limity pamięci i restart kontenerów | lokalny broker i alarm na ESP32 działają bez chmury (T10, T21) | odporność na DoS z wnętrza strefy nie jest celem labu |

## Co z tego wynika

- Każda strefa systemu sterowania ma co najmniej jeden FR na poziomie 3, ale żadna nie ma 3 we wszystkich. To uzasadnia podejście punktowe: TLS i ACL wszędzie (poziom 2), a dodatkowe środki tylko dla integralności G-code, kontroli komend i odpylania.
- Najsłabsze miejsca względem SL-T to integralność G-code (FR3 w Z1 i Z4) i uwierzytelnianie Modbus (FR1 w Z2). Pierwsze rozwija Etap 4 (Tampering), drugie zamykamy conduitem, bo protokołu nie zmienimy.
- Biuro ma SL-T 1 świadomie: bezpieczeństwo produkcji nie może zależeć od tego, czy pracownik kliknie w link.
