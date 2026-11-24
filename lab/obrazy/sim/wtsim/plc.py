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

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext, ModbusSlaveContext
from pymodbus.server import StartAsyncTcpServer

from wtsim.wspolne import klient_mqtt, log

PLC_ID = os.environ.get("PLC_ID", "plc-odpylanie")
PREFIKS = os.environ.get("MQTT_PREFIKS", "wood-tech/hala1")
CEWKI, REJESTRY = 1, 3  # kody funkcji Modbus dla getValues/setValues


async def proces(kontekst: ModbusServerContext) -> None:
    klient = klient_mqtt(PLC_ID)
    urzadzenie = kontekst[0]
    obroty, pyl = 0.0, 5.0
    poprzednie = None
    while True:
        wentylator, przepustnica = urzadzenie.getValues(CEWKI, 0, 2)
        if (wentylator, przepustnica) != poprzednie:
            log(PLC_ID, "zmiana_cewek", wentylator=bool(wentylator), przepustnica=bool(przepustnica))
            poprzednie = (wentylator, przepustnica)
        cel = 2900.0 if wentylator else 0.0
        obroty += (cel - obroty) * 0.3
        podcisnienie = 0.00018 * obroty**2 * (1.0 if przepustnica else 0.15)
        wyciag = (obroty / 2900.0) * (1.0 if przepustnica else 0.1)
        # Obróbka wytwarza pył; wyciąg go usuwa. Bez wyciągu stężenie szybko rośnie (zagrożenie wybuchem).
        pyl = max(0.5, pyl + 0.8 - 1.0 * wyciag * pyl / 5.0 + random.gauss(0, 0.05))
        urzadzenie.setValues(REJESTRY, 0, [int(obroty), int(podcisnienie), int(pyl * 10)])
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
    urzadzenie = ModbusSlaveContext(
        co=ModbusSequentialDataBlock(0, [1, 1] + [0] * 14),
        hr=ModbusSequentialDataBlock(0, [0] * 16),
        zero_mode=True,
    )
    kontekst = ModbusServerContext(slaves=urzadzenie, single=True)
    log(PLC_ID, "start", modbus_port=502)
    await asyncio.gather(
        StartAsyncTcpServer(context=kontekst, address=("0.0.0.0", 502)),
        proces(kontekst),
    )


if __name__ == "__main__":
    asyncio.run(main())
