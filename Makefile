# Kontrole jakości repozytorium (wzorem secure-k8s-aiops). Te same cele uruchamia CI.
# Narzędzia w wersjach z mise.toml (make doctor sprawdza całość).
MAKEFLAGS += --no-print-directory

# Narzędzia w wersjach z mise.toml mają pierwszeństwo przed systemowymi, także bez aktywacji mise w powłoce.
export PATH := $(shell mise bin-paths 2>/dev/null | tr '\n' ':')$(PATH)

.PHONY: help doctor lint unit gitleaks trivy-config

help:
	@echo "make doctor        narzedzia z mise.toml, Docker bez sudo, compose, pamiec"
	@echo "make lint          ruff check + ruff format --check"
	@echo "make unit          testy jednostkowe"
	@echo "make gitleaks      sekrety w calej historii HEAD"
	@echo "make trivy-config  bramka Trivy dla Dockerfile i konfiguracji (wyniki w reports/trivy/)"

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
