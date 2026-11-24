#!/usr/bin/env bash
# Sprawdza, czy maszyna jest gotowa do pracy z projektem (T01, wzorem secure-k8s-aiops).
# Uruchamiaj przez `make doctor`: Makefile stawia narzędzia z mise.toml na początku PATH.
# Kod wyjścia 0 tylko wtedy, gdy żadne sprawdzenie nie zwróciło FAIL.
set -u

cd "$(dirname "$0")/.." || exit 1

# Cały lab (v0 i v1) ma się zmieścić w ok. 4 GB; z zapasem na system i Wiresharka wymagamy 6 GiB widocznych dla Dockera.
MIN_DOCKER_MEM_BYTES=6442450944

failures=0

ok() { printf '[ OK ] %s\n' "$1"; }
skip() { printf '[SKIP] %s\n' "$1"; }
fail() {
  printf '[FAIL] %s\n' "$1"
  if [ -n "${2:-}" ]; then
    printf '       Napraw: %s\n' "$2"
  fi
  failures=$((failures + 1))
}
physical_dir() { (cd "$1" 2>/dev/null && pwd -P); }

echo "== Narzędzia z mise.toml =="
if ! command -v mise >/dev/null 2>&1; then
  fail "brak mise" "zainstaluj mise: https://mise.jdx.dev/getting-started.html"
else
  ok "mise $(mise --version 2>/dev/null | cut -d ' ' -f 1)"
  # klucz z [tools] w mise.toml i jego plik wykonywalny; nowe narzędzie dopisz w obu miejscach
  while read -r tool bin; do
    if ! dir=$(mise where "$tool" 2>/dev/null </dev/null); then
      fail "$tool: brak wersji z mise.toml" "mise install"
      continue
    fi
    tool_dir=$(physical_dir "$dir")
    path=$(command -v "$bin" 2>/dev/null || true)
    bin_dir=""
    if [ -n "$path" ]; then
      bin_dir=$(physical_dir "$(dirname "$path")")
    fi
    case "$bin_dir/" in
      "$tool_dir"/*) ok "$tool ${dir##*/}" ;;
      *) fail "$tool: $bin z PATH (${path:-brak}) to nie wersja ${dir##*/} z mise.toml" "uruchamiaj przez make (make doctor)" ;;
    esac
  done <<'EOF'
python python3
uv uv
ruff ruff
trivy trivy
gitleaks gitleaks
EOF
fi

echo "== Docker =="
docker_ok=0
if [ "$(id -u)" -eq 0 ]; then
  fail "make doctor uruchomione jako root" "uruchom bez sudo, jako zwykły użytkownik"
elif ! command -v docker >/dev/null 2>&1; then
  fail "brak polecenia docker" "zainstaluj Docker Engine według README (sekcja „Przygotowanie środowiska”)"
elif ! docker_out=$(docker info --format '{{.ServerVersion}} {{.MemTotal}}' 2>&1); then
  case "$docker_out" in
    *"permission denied"*)
      fail "brak dostępu do Dockera bez sudo" 'sudo usermod -aG docker "$USER", potem wyloguj się i zaloguj ponownie' ;;
    *)
      fail "Docker nie odpowiada: $(printf '%s\n' "$docker_out" | head -n 1)" "sudo systemctl start docker" ;;
  esac
else
  docker_ok=1
  ok "Docker ${docker_out% *}, dostęp bez sudo"
fi
if [ "$docker_ok" -eq 1 ]; then
  mem=${docker_out#* }
  mem_gib=$(awk -v b="$mem" 'BEGIN { printf "%.1f", b / 1073741824 }')
  if [ "$mem" -ge "$MIN_DOCKER_MEM_BYTES" ]; then
    ok "pamięć dla Dockera: $mem_gib GiB"
  else
    fail "pamięć dla Dockera: $mem_gib GiB, wymagane co najmniej 6 GiB" "zwiększ RAM maszyny wirtualnej (zalecane 8 GB)"
  fi
  if compose_out=$(docker compose version --short 2>/dev/null); then
    ok "Docker Compose $compose_out"
  else
    fail "brak pluginu docker compose" "sudo apt install docker-compose-plugin (repozytorium Dockera)"
  fi
else
  skip "pamięć dla Dockera (brak dostępu do Dockera)"
  skip "Docker Compose (brak dostępu do Dockera)"
fi

echo "== Inne narzędzia =="
for para in "make:make" "tcpdump:zapis ruchu labu do pcap" "openssl:certyfikaty w Etapie 3"; do
  bin=${para%%:*}
  cel=${para#*:}
  if command -v "$bin" >/dev/null 2>&1; then
    ok "$bin ($cel)"
  else
    fail "brak $bin (potrzebny do: $cel)" "sudo apt install $bin"
  fi
done

echo
if [ "$failures" -eq 0 ]; then
  echo "Wszystkie sprawdzenia przeszły."
else
  echo "Nieudane sprawdzenia: $failures. Napraw je i uruchom ponownie: make doctor"
  exit 1
fi
