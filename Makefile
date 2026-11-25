# Lab Wood-Tech CNC i kontrole jakości (wzorem secure-k8s-aiops). Te same cele uruchamia CI.
# Narzędzia w wersjach z mise.toml (make doctor sprawdza całość).
MAKEFLAGS += --no-print-directory

# Narzędzia w wersjach z mise.toml mają pierwszeństwo przed systemowymi, także bez aktywacji mise w powłoce.
export PATH := $(shell mise bin-paths 2>/dev/null | tr '\n' ':')$(PATH)

V0 := docker compose -f lab/v0/compose.yaml --profile atak
V1 := docker compose -f lab/v1/compose.yaml --profile atak
# Usługi labu v1 bez przejętego komputera biurowego (biuro-pc ma profil `atak`).
V1_USLUGI := fw-ot fw-it broker-lokalny cnc-1 cnc-2 plc-odpylanie serwer cad-stacja chmura-mqtt
CZAS ?= 60

.PHONY: help doctor lint unit gitleaks trivy-config test-security test-segmentacja \
        v0-up v0-up-atak v0-down v0-status v0-logs v0-mqtt v0-capture v0-nagranie v0-przeplywy v0-analiza \
        v1-up v1-up-atak v1-down v1-status v1-logs

help:
	@echo "make doctor        narzedzia z mise.toml, Docker bez sudo, compose, pamiec"
	@echo "make lint          ruff check + ruff format --check"
	@echo "make unit          testy jednostkowe"
	@echo "make gitleaks      sekrety w calej historii HEAD"
	@echo "make trivy-config  bramka Trivy dla Dockerfile i konfiguracji (wyniki w reports/trivy/)"
	@echo "make test-security testy bezpieczenstwa na dzialajacym labie v0 (najpierw make v0-up-atak)"
	@echo "make test-segmentacja testy segmentacji na dzialajacym labie v1 (najpierw make v1-up-atak)"
	@echo "make v0-up         lab v0 (siec niebezpieczna): router, chmura MQTT, CNC x2, PLC, serwer, stacja CAD"
	@echo "make v0-up-atak    jak v0-up, plus przejety komputer biurowy (biuro-pc)"
	@echo "make v0-status     kontenery i zuzycie pamieci"
	@echo "make v0-logs       logi JSON symulatorow (Ctrl+C konczy)"
	@echo "make v0-mqtt       podglad wszystkich wiadomosci MQTT w chmurze (Ctrl+C konczy)"
	@echo "make v0-capture    zapis ruchu sieci zakladu do evidence/v0-<data>.pcap (CZAS=$(CZAS) s, wymaga sudo)"
	@echo "make v0-nagranie   start labu z nagrywaniem obu sieci od pierwszego pakietu (CZAS=$(CZAS) s, bez sudo)"
	@echo "make v0-przeplywy  polaczenia widoczne w pliku pcap (PCAP=plik.pcap), do porownania z tabela przeplywow"
	@echo "make v0-analiza    nagranie v0 ze scenariuszem ataku z biura i zrzuty tshark do evidence/etap-3/ (ok. 2 min)"
	@echo "make v0-down       zatrzymuje i usuwa kontenery i sieci labu v0"
	@echo "make v1-up         lab v1 (siec zabezpieczona): strefy, dwie zapory nftables, lokalny broker"
	@echo "make v1-up-atak    jak v1-up, plus przejety komputer biurowy w strefie biura (biuro-pc)"
	@echo "make v1-status     kontenery i zuzycie pamieci labu v1"
	@echo "make v1-logs       logi JSON symulatorow labu v1 (Ctrl+C konczy)"
	@echo "make v1-down       zatrzymuje i usuwa kontenery i sieci labu v1"

doctor:
	@bash scripts/doctor.sh

# Lint i formatowanie Pythona (job lint): ruff, reguły w pyproject.toml.
lint:
	ruff check
	ruff format --check

# Testy jednostkowe (job unit). --locked: błąd, gdy uv.lock nie pasuje do pyproject.toml.
# Kod 5 pytesta (nie znaleziono testów) nie jest błędem, dopóki repozytorium nie ma jeszcze kodu.
unit:
	uv run --locked pytest; kod=$$?; [ $$kod -eq 0 ] || [ $$kod -eq 5 ]

# Sekrety w całej historii HEAD (job secrets). Ważne od Etapu 3: klucze prywatne CA i certyfikatów nie mogą trafić do repo.
gitleaks:
	gitleaks git --no-banner --redact --verbose --log-opts="--diff-merges=first-parent HEAD" .

# Bramka Trivy (job config): Dockerfile i konfiguracje w repozytorium; kod 1 przy HIGH albo CRITICAL spoza .trivyignore.
# Pełny raport (wszystkie poziomy) w reports/trivy/config.json.
trivy-config:
	@mkdir -p reports/trivy
	trivy config --quiet --skip-dirs .venv --format json --output reports/trivy/config.json .
	trivy config --quiet --skip-dirs .venv --exit-code 1 --severity HIGH,CRITICAL .

# Testy na działającym labie (job e2e): tests/security, marker security; raport JUnit w reports/.
test-security:
	@mkdir -p reports
	uv run --locked pytest tests/security -m security -v --junitxml=reports/junit-security.xml

# Testy segmentacji labu v1 (job e2e-v1): tests/security, marker segmentacja; najpierw make v1-up-atak.
test-segmentacja:
	@mkdir -p reports
	uv run --locked pytest tests/security -m segmentacja -v --junitxml=reports/junit-segmentacja.xml

v0-up:
	$(V0) up -d --build cnc-1 cnc-2 plc-odpylanie serwer cad-stacja

v0-up-atak:
	$(V0) up -d --build

v0-down:
	$(V0) down

v1-up:
	$(V1) up -d --build $(V1_USLUGI)

v1-up-atak:
	$(V1) up -d --build

v1-down:
	$(V1) down

v1-status:
	$(V1) ps
	@docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}' $$($(V1) ps -q)

v1-logs:
	$(V1) logs -f cnc-1 cnc-2 plc-odpylanie cad-stacja

v0-status:
	$(V0) ps
	@docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}' $$($(V0) ps -q)

v0-logs:
	$(V0) logs -f cnc-1 cnc-2 plc-odpylanie cad-stacja

v0-mqtt:
	$(V0) exec chmura-mqtt mosquitto_sub -h localhost -t '#' -v

v0-capture:
	@mkdir -p evidence
	sudo timeout $(CZAS) tcpdump -i wt0-zaklad -w evidence/v0-$$(date +%Y%m%d-%H%M%S).pcap || true

# Start labu z nagrywaniem od pierwszego pakietu, na obu sieciach (wt0-zaklad i wt0-internet), bez sudo
# i bez tcpdump na hoście: tcpdump z obrazu routera w sieci hosta. Lab musi być wyłączony (make v0-down).
# Wynik: evidence/v0-<data>-zaklad.pcap i evidence/v0-<data>-internet.pcap.
NAGRYWARKA = docker run -d --rm --net host --cap-add NET_RAW --cap-add NET_ADMIN -v "$(CURDIR)/evidence:/cap" \
	--entrypoint timeout
v0-nagranie:
	@mkdir -p evidence
	$(V0) up --no-start cnc-1 cnc-2 plc-odpylanie serwer cad-stacja
	@t=$$(date +%Y%m%d-%H%M%S); \
	for siec in zaklad internet; do \
	  $(NAGRYWARKA) --name wt-nagranie-$$siec wood-tech/router:dev $(CZAS) \
	    tcpdump -i wt0-$$siec -nn -U -w /cap/v0-$$t-$$siec.pcap >/dev/null; \
	done; \
	sleep 2; $(V0) up -d cnc-1 cnc-2 plc-odpylanie serwer cad-stacja; \
	echo "nagrywanie $(CZAS) s do evidence/v0-$$t-zaklad.pcap i evidence/v0-$$t-internet.pcap"; \
	docker wait wt-nagranie-zaklad wt-nagranie-internet >/dev/null

# Połączenia widoczne w nagraniu: początki połączeń TCP i datagramy UDP, każde raz.
# Porównujemy je z tabelą przepływów w docs/architektura/przeplywy-danych.md. tcpdump z obrazu routera.
v0-przeplywy:
	@test -n "$(PCAP)" || { echo "podaj plik: make v0-przeplywy PCAP=evidence/v0-<data>-zaklad.pcap"; exit 1; }
	@docker run --rm -v "$(CURDIR):/repo:ro" -w /repo --entrypoint tcpdump wood-tech/router:dev \
	  -nn -q -r $(PCAP) 'tcp[tcpflags] == tcp-syn or udp' 2>/dev/null | python3 scripts/przeplywy.py

# Analiza ruchu v0 (T08): start labu z biurem i nagrywaniem obu sieci, scenariusz z przejętego komputera
# biurowego (podsłuch MQTT, zapis cewki PLC, wstrzyknięcie STOP/START dla cnc-1), zrzuty tshark w obrazie
# atakującego. Wynik w evidence/etap-3/. Lab musi być wyłączony (make v0-down); skrypt zatrzymuje go na końcu.
v0-analiza:
	@bash scripts/analiza_v0.sh
