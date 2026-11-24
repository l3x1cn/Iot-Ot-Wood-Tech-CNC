"""Testy jednostkowe symulatora PLC: mapa rejestrów Modbus na prawdziwym serwerze TCP (localhost)."""

import asyncio
import socket

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.server import ModbusTcpServer

from wtsim.plc import CEWKI, REJESTRY, urzadzenie


def wolny_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def scenariusz() -> dict:
    port = wolny_port()
    serwer = ModbusTcpServer(urzadzenie(), address=("127.0.0.1", port))
    zadanie = asyncio.create_task(serwer.serve_forever())
    klient = AsyncModbusTcpClient("127.0.0.1", port=port, timeout=3)
    try:
        for _ in range(50):
            if await klient.connect():
                break
            await asyncio.sleep(0.05)
        wynik = {"cewki_start": (await klient.read_coils(0, count=2)).bits[:2]}
        # Proces PLC zapisuje pomiary do rejestrów holding; klient sieciowy je odczytuje.
        await serwer.context.async_setValues(0, REJESTRY, 0, [2900, 1514, 52])
        wynik["rejestry"] = (await klient.read_holding_registers(0, count=3)).registers
        # Atakujący z sieci wyłącza wentylator; proces PLC widzi to w swojej pamięci.
        await klient.write_coil(0, False)
        wynik["cewki_proces"] = await serwer.context.async_getValues(0, CEWKI, 0, 2)
        return wynik
    finally:
        klient.close()
        await serwer.shutdown()
        zadanie.cancel()


def test_mapa_rejestrow_i_zapis_cewki_z_sieci():
    wynik = asyncio.run(scenariusz())
    assert wynik["cewki_start"] == [True, True]
    assert wynik["rejestry"] == [2900, 1514, 52]
    assert list(wynik["cewki_proces"]) == [False, True]
