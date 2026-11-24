"""Wspólne funkcje symulatorów: logi JSON i klient MQTT."""

import json
import os
import sys
import time

import paho.mqtt.client as mqtt


def log(zrodlo: str, zdarzenie: str, **pola) -> None:
    """Jedna linia JSON na stdout; `docker compose logs` zbiera je jako ślady do analizy."""
    rekord = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "zrodlo": zrodlo, "zdarzenie": zdarzenie, **pola}
    print(json.dumps(rekord, ensure_ascii=False), file=sys.stdout, flush=True)


def klient_mqtt(identyfikator: str, on_message=None, subskrypcje: tuple[str, ...] = ()) -> mqtt.Client:
    """Klient MQTT z ustawień środowiska. W v0: bez TLS, bez hasła, połączenie wprost do chmury."""
    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    klient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=identyfikator)
    uzytkownik = os.environ.get("MQTT_USER")
    if uzytkownik:
        klient.username_pw_set(uzytkownik, os.environ.get("MQTT_PASSWORD"))
    ca = os.environ.get("MQTT_CA")
    if ca:
        klient.tls_set(ca_certs=ca, certfile=os.environ.get("MQTT_CERT"), keyfile=os.environ.get("MQTT_KEY"))
    if on_message:
        klient.on_message = on_message

    def po_polaczeniu(c, _userdata, _flags, kod, _props):
        log(identyfikator, "mqtt_polaczono", broker=f"{host}:{port}", kod=str(kod))
        for temat in subskrypcje:
            c.subscribe(temat, qos=1)

    klient.on_connect = po_polaczeniu
    klient.reconnect_delay_set(min_delay=1, max_delay=10)
    while True:
        try:
            klient.connect(host, port, keepalive=30)
            break
        except OSError as blad:
            log(identyfikator, "mqtt_brak_polaczenia", broker=f"{host}:{port}", blad=str(blad))
            time.sleep(3)
    klient.loop_start()
    return klient
