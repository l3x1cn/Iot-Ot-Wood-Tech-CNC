"""Symulator PLC centralnego odpylania (Modbus TCP, port 502).

Mapa rejestrów (adresy od 0):
- cewka 0: wentylator wyciągowy (1 = pracuje),
- cewka 1: przepustnica hali 1 (1 = otwarta),
- rejestr 0: obroty wentylatora [rpm],
- rejestr 1: podciśnienie w kolektorze [Pa],
- rejestr 2: stężenie pyłu drzewnego na hali [mg/m3 * 10].

W v0 Modbus nie ma żadnego uwierzytelnienia: każdy w sieci może zapisać cewki.
Stan publikowany jest co sekundę po MQTT.
"""

import asyncio
import json
import os
import random

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

from wtsim.wspolne import klient_mqtt, log

PLC_ID = os.environ.get("PLC_ID", "plc-odpylanie")
PREFIKS = os.environ.get("MQTT_PREFIKS", "wood-tech/hala1")
CEWKI, REJESTRY = 1, 3  # kody funkcji Modbus wskazujące blok pamięci (cewki, rejestry holding)


def urzadzenie() -> SimDevice:
    """Pamięć PLC: osobne bloki cewek, wejść, rejestrów holding i wejściowych, po 16 adresów od 0."""
    return SimDevice(
        id=0,  # odpowiada na każdy identyfikator urządzenia (unit id)
        simdata=(
            [SimData(0, values=[True, True] + [False] * 14, datatype=DataType.BITS)],
            [SimData(0, values=[False] * 16, datatype=DataType.BITS)],
            [SimData(0, count=16, values=0, datatype=DataType.REGISTERS)],
            [SimData(0, count=16, values=0, datatype=DataType.REGISTERS)],
        ),
    )


async def proces(pamiec) -> None:
    """Pętla procesu; `pamiec` to datastore serwera (ModbusTcpServer.context)."""
    klient = klient_mqtt(PLC_ID)
    obroty, pyl = 0.0, 5.0
    poprzednie = None
    while True:
        wentylator, przepustnica = await pamiec.async_getValues(0, CEWKI, 0, 2)
        if (wentylator, przepustnica) != poprzednie:
            log(PLC_ID, "zmiana_cewek", wentylator=bool(wentylator), przepustnica=bool(przepustnica))
            poprzednie = (wentylator, przepustnica)
        cel = 2900.0 if wentylator else 0.0
        obroty += (cel - obroty) * 0.3
        podcisnienie = 0.00018 * obroty**2 * (1.0 if przepustnica else 0.15)
        wyciag = (obroty / 2900.0) * (1.0 if przepustnica else 0.1)
        # Obróbka wytwarza pył; wyciąg go usuwa. Bez wyciągu stężenie szybko rośnie (zagrożenie wybuchem).
        pyl = max(0.5, pyl + 0.8 - 1.0 * wyciag * pyl / 5.0 + random.gauss(0, 0.05))
        await pamiec.async_setValues(0, REJESTRY, 0, [int(obroty), int(podcisnienie), int(pyl * 10)])
        stan = {
            "plc": PLC_ID,
            "wentylator": bool(wentylator),
            "przepustnica": bool(przepustnica),
            "obroty_rpm": int(obroty),
            "podcisnienie_Pa": int(podcisnienie),
            "pyl_mg_m3": round(pyl, 1),
        }
        klient.publish(f"{PREFIKS}/odpylanie/stan", json.dumps(stan), qos=0)
        if pyl > 50:
            log(PLC_ID, "alarm_stezenie_pylu", pyl_mg_m3=round(pyl, 1))
        await asyncio.sleep(1.0)


async def main() -> None:
    serwer = ModbusTcpServer(urzadzenie(), address=("0.0.0.0", 502))
    log(PLC_ID, "start", modbus_port=502)
    await asyncio.gather(serwer.serve_forever(), proces(serwer.context))


if __name__ == "__main__":
    asyncio.run(main())
