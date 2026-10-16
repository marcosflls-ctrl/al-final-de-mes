"""
IPC del INE: índice general, grupos y subclases (productos) con las variaciones anual y mensual.
Guarda en src/data/ipc.json los últimos 25 meses. Base 2025 = 100 (ECOICOP ver. 2).

Uso: python scripts/ipc.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "ipc.json"
API = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{}?nult=25"
TABLAS = {"grupos": 76125, "subclases": 76128}
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"
TIPOS = {"Índice": "i", "Variación anual": "va", "Variación mensual": "vm"}


def aviso(tipo: str, texto: str) -> None:
    print(texto)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{tipo} title=IPC::{texto}")


def leer(tabla: int) -> dict[str, dict]:
    datos = requests.get(API.format(tabla), headers={"User-Agent": UA}, timeout=120).json()
    res: dict[str, dict] = {}
    for s in datos:
        partes = [p.strip() for p in s.get("Nombre", "").split(".") if p.strip()]
        if len(partes) < 3 or partes[0] not in ("Nacional", "Total Nacional"):
            continue
        nombre, tipo = ". ".join(partes[1:-1]), partes[-1]
        clave = TIPOS.get(tipo)
        if not clave:
            continue
        serie = {f"{x['Anyo']}-{int(x['FK_Periodo']):02d}": x["Valor"] for x in s.get("Data", []) if x.get("Valor") is not None and 1 <= int(x["FK_Periodo"]) <= 12}
        res.setdefault(nombre, {})[clave] = dict(sorted(serie.items()))
    return res


def main() -> int:
    try:
        grupos, subclases = leer(TABLAS["grupos"]), leer(TABLAS["subclases"])
    except Exception as e:  # noqa: BLE001
        aviso("error", f"{type(e).__name__}: {str(e)[:300]}")
        return 1
    if len(subclases) < 100 or not grupos:
        aviso("error", f"Pocos datos: {len(grupos)} grupos, {len(subclases)} subclases")
        return 1
    general = next((v for k, v in grupos.items() if re.match(r"(?i)índice general", k)), None)
    if not general or not general.get("va"):
        aviso("error", f"No encuentro el índice general entre: {list(grupos)[:5]}")
        return 1
    ultimo = max(general["va"])
    salida = {
        "fuente": "INE, Índice de Precios de Consumo (base 2025, ECOICOP ver. 2)",
        "actualizado": datetime.now(ZoneInfo("Europe/Madrid")).replace(microsecond=0).isoformat(),
        "mes": ultimo,
        "general": general,
        "grupos": {k: v for k, v in grupos.items() if v is not general},
        "subclases": subclases,
    }
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    aviso("notice", f"{ultimo}: IPC general {general['va'][ultimo]} % anual · {len(grupos)} grupos · {len(subclases)} subclases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
