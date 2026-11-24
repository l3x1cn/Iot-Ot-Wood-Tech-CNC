# Lab Wood-Tech CNC i kontrole jakości (wzorem secure-k8s-aiops).
# Wymaga Dockera z pluginem compose; narzędzia w wersjach z mise.toml (make doctor sprawdza całość).
MAKEFLAGS += --no-print-directory

# Narzędzia w wersjach z mise.toml mają pierwszeństwo przed systemowymi, także bez aktywacji mise w powłoce.
export PATH := $(shell mise bin-paths 2>/dev/null | tr '\n' ':')$(PATH)

V0 := docker compose -f lab/v0/compose.yaml --profile atak
CZAS ?= 60

.PHONY: help doctor lint unit gitleaks trivy-config test-security \
        v0-up v0-up-atak v0-down v0-status v0-logs v0-mqtt v0-capture

help:
	@echo "Przygotowanie i kontrole (te same co w CI):"
	@echo "  make doctor        narzedzia z mise.toml, Docker bez sudo, compose, pamiec"
	@echo "  make lint          ruff check + ruff format --check"
	@echo "  make unit          testy jednostkowe symulatorow (bez Dockera)"
	@echo "  make gitleaks      sekrety w calej historii HEAD"
	@echo "  make trivy-config  bramka Trivy dla Dockerfile i konfiguracji w lab/ (wyniki w reports/trivy/)"
	@echo "  make test-security testy bezpieczenstwa na dzialajacym labie (najpierw make v0-up-atak)"
	@echo "Lab v0 (siec niebezpieczna):"
	@echo "  make v0-up         router, chmura MQTT, CNC x2, PLC odpylania, serwer, stacja CAD"
	@echo "  make v0-up-atak    jak v0-up, plus przejety komputer biurowy (biuro-pc)"
	@echo "  make v0-status     kontenery i zuzycie pamieci"
	@echo "  make v0-logs       logi JSON symulatorow (Ctrl+C konczy)"
	@echo "  make v0-mqtt       podglad wszystkich wiadomosci MQTT w chmurze (Ctrl+C konczy)"
	@echo "  make v0-capture    zapis ruchu sieci zakladu do evidence/v0-<data>.pcap (CZAS=$(CZAS) s, wymaga sudo)"
	@echo "  make v0-down       zatrzymuje i usuwa kontenery i sieci labu v0"

doctor:
	@bash scripts/doctor.sh

# Lint i formatowanie Pythona (job lint): ruff, reguły w pyproject.toml.
lint:
	ruff check
	ruff format --check

# Testy jednostkowe bez Dockera (job unit): testpaths w pyproject.toml. --locked: błąd, gdy uv.lock nie pasuje do pyproject.toml.
unit:
	uv run --locked pytest

# Sekrety w całej historii HEAD (job secrets). Ważne od Etapu 3: klucze prywatne CA i certyfikatów nie mogą trafić do repo.
gitleaks:
	gitleaks git --no-banner --redact --verbose --log-opts="--diff-merges=first-parent HEAD" .

# Bramka Trivy (job config): Dockerfile i konfiguracje w lab/; kod 1 przy HIGH albo CRITICAL spoza .trivyignore.
# Pełny raport (wszystkie poziomy) w reports/trivy/config.json.
trivy-config:
	@mkdir -p reports/trivy
	trivy config --quiet --format json --output reports/trivy/config.json lab/
	trivy config --quiet --exit-code 1 --severity HIGH,CRITICAL lab/

# Testy na działającym labie (job e2e): tests/security, marker security; raport JUnit w reports/.
test-security:
	@mkdir -p reports
	uv run --locked pytest tests/security -m security -v --junitxml=reports/junit-security.xml

v0-up:
	$(V0) up -d --build cnc-1 cnc-2 plc-odpylanie serwer cad-stacja

v0-up-atak:
	$(V0) up -d --build

v0-down:
	$(V0) down

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
