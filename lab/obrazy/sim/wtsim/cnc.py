"""Symulator obrabiarki CNC.

- przyjmuje program G-code przez HTTP (POST /program), w v0 bez uwierzytelnienia i bez szyfrowania;
- wykonuje program: każdy ruch G0/G1 trwa CZAS_RUCHU sekund;
- co sekundę publikuje telemetrię wrzeciona po MQTT (prąd, obroty, posuw, głębokość, temperatura);
- słucha komend START/STOP na temacie MQTT `<prefiks>/<id>/komenda`.

Prąd wrzeciona zależy od obrotów, posuwu i głębokości skrawania. Zmieniony (np. podmieniony w locie)
program daje inny przebieg prądu, co później wykorzystuje detekcja anomalii (Etap 5).
"""

import hashlib
import json
import os
import random
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from wtsim.wspolne import klient_mqtt, log

CNC_ID = os.environ.get("CNC_ID", "cnc-1")
PREFIKS = os.environ.get("MQTT_PREFIKS", "wood-tech/hala1")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))
CZAS_RUCHU = float(os.environ.get("CZAS_RUCHU", "1.5"))
PRAD_MAX = 30.0          # zabezpieczenie nadprądowe falownika [A]
PRAD_PRZECIAZENIE = 20.0  # próg ostrzeżenia [A]

SLOWO = re.compile(r"([GMSFXYZ])(-?\d+(?:\.\d+)?)", re.IGNORECASE)


class Maszyna:
    def __init__(self) -> None:
        self.blokada = threading.Lock()
        self.ruchy: list[dict] = []
        self.nazwa = None
        self.sha256 = None
        self.indeks = 0
        self.pracuje = False
        self.wrzeciono = False
        self.obroty = 0.0
        self.posuw = 0.0
        self.z = 5.0
        self.temperatura = 24.0
        self.prad = 0.3

    def wczytaj(self, tekst: str, nazwa: str | None) -> dict:
        ruchy, stan = [], {"S": 0.0, "F": 0.0, "Z": 5.0, "wrzeciono": False}
        for numer, linia in enumerate(tekst.splitlines(), start=1):
            linia = linia.split(";", 1)[0].split("(", 1)[0].strip()
            if not linia:
                continue
            slowa = {k.upper(): float(v) for k, v in SLOWO.findall(linia)}
            if "S" in slowa:
                stan["S"] = slowa["S"]
            if "F" in slowa:
                stan["F"] = slowa["F"]
            if slowa.get("M") == 3:
                stan["wrzeciono"] = True
            if slowa.get("M") == 5:
                stan["wrzeciono"] = False
            if "G" in slowa and slowa["G"] in (0, 1):
                if "Z" in slowa:
                    stan["Z"] = slowa["Z"]
                ruchy.append({"linia": numer, "G": int(slowa["G"]), **stan})
        skrot = hashlib.sha256(tekst.encode()).hexdigest()
        with self.blokada:
            self.ruchy, self.nazwa, self.sha256 = ruchy, nazwa, skrot
            self.indeks, self.pracuje = 0, bool(ruchy)
        return {"nazwa": nazwa, "sha256": skrot, "ruchy": len(ruchy)}

    def krok(self, dt: float) -> None:
        with self.blokada:
            if self.pracuje and self.ruchy:
                ruch = self.ruchy[min(int(self.indeks), len(self.ruchy) - 1)]
                self.wrzeciono, self.obroty = ruch["wrzeciono"], ruch["S"]
                self.posuw, self.z = ruch["F"], ruch["Z"]
                skrawa = ruch["G"] == 1 and ruch["Z"] < 0 and self.wrzeciono
                self.indeks += dt / CZAS_RUCHU
                if self.indeks >= len(self.ruchy):
                    self.pracuje, self.wrzeciono, self.obroty = False, False, 0.0
                    log(CNC_ID, "program_zakonczony", nazwa=self.nazwa, sha256=self.sha256)
            else:
                skrawa = False
                self.wrzeciono, self.obroty, self.posuw = False, 0.0, 0.0
            # Model prądu: elektronika + bieg jałowy wrzeciona + obciążenie skrawaniem.
            prad = 0.3
            if self.wrzeciono:
                prad += 1.2 + 0.00008 * self.obroty
            if skrawa:
                prad += 0.00022 * self.posuw * abs(self.z)
            prad *= random.gauss(1.0, 0.04)
            self.prad = round(min(max(prad, 0.0), PRAD_MAX), 3)
            # Temperatura wrzeciona: powolne nagrzewanie proporcjonalne do prądu.
            self.temperatura += dt * (0.02 * self.prad - 0.01 * (self.temperatura - 24.0))

    def stan(self) -> dict:
        with self.blokada:
            return {
                "cnc": CNC_ID,
                "pracuje": self.pracuje,
                "program": self.nazwa,
                "sha256": self.sha256,
                "linia": self.ruchy[min(int(self.indeks), len(self.ruchy) - 1)]["linia"] if self.pracuje else None,
                "wrzeciono": self.wrzeciono,
                "obroty_rpm": self.obroty,
                "posuw_mm_min": self.posuw,
                "z_mm": self.z,
                "prad_A": self.prad,
                "temperatura_C": round(self.temperatura, 2),
            }


MASZYNA = Maszyna()


class Http(BaseHTTPRequestHandler):
    def _odpowiedz(self, kod: int, dane: dict) -> None:
        tresc = json.dumps(dane, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(tresc)))
        self.end_headers()
        self.wfile.write(tresc)

    def do_GET(self):
        if self.path == "/status":
            self._odpowiedz(200, MASZYNA.stan())
        else:
            self._odpowiedz(404, {"blad": "nie ma"})

    def do_POST(self):
        if self.path != "/program":
            self._odpowiedz(404, {"blad": "nie ma"})
            return
        dlugosc = int(self.headers.get("Content-Length", "0"))
        tekst = self.rfile.read(dlugosc).decode(errors="replace")
        wynik = MASZYNA.wczytaj(tekst, self.headers.get("X-Program"))
        log(CNC_ID, "program_wczytany", nadawca=self.client_address[0], **wynik)
        self._odpowiedz(200, wynik)

    def log_message(self, *_args):  # logi HTTP idą przez log() w do_POST
        pass


def na_komende(_klient, _userdata, wiadomosc) -> None:
    komenda = wiadomosc.payload.decode(errors="replace").strip().upper()
    log(CNC_ID, "komenda_mqtt", temat=wiadomosc.topic, komenda=komenda)
    with MASZYNA.blokada:
        if komenda == "STOP":
            MASZYNA.pracuje = False
        elif komenda == "START" and MASZYNA.ruchy:
            MASZYNA.indeks, MASZYNA.pracuje = 0, True


def main() -> None:
    klient = klient_mqtt(CNC_ID, on_message=na_komende, subskrypcje=(f"{PREFIKS}/{CNC_ID}/komenda",))
    serwer = ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), Http)
    threading.Thread(target=serwer.serve_forever, daemon=True).start()
    log(CNC_ID, "start", http_port=HTTP_PORT)
    dt, licznik, przeciazenie = 0.1, 0, False
    while True:
        MASZYNA.krok(dt)
        licznik += 1
        if licznik % 10 == 0:
            stan = MASZYNA.stan()
            klient.publish(f"{PREFIKS}/{CNC_ID}/telemetria", json.dumps(stan), qos=0)
            if stan["prad_A"] > PRAD_PRZECIAZENIE and not przeciazenie:
                log(CNC_ID, "przeciazenie_wrzeciona", prad_A=stan["prad_A"], program=stan["program"])
            przeciazenie = stan["prad_A"] > PRAD_PRZECIAZENIE
        time.sleep(dt)


if __name__ == "__main__":
    main()
