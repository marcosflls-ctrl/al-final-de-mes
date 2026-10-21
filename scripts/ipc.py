"""
IPC del INE: índice general, grupos y subclases (productos) con las variaciones anual y mensual.
Guarda en src/data/ipc.json los últimos 25 meses. Base 2025 = 100 (ECOICOP ver. 2).
Además, para las calculadoras del alquiler y del valor del dinero:
  · «irav»: el Índice de Referencia para la Actualización de Arrendamientos de Vivienda (INE, tabla 72975).
  · «historico»: el índice general de todos los meses que publique el INE (serie enlazada), para comparar años.
Si alguno de estos dos falla, se conserva el dato anterior y no se da error.

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
TABLA_IRAV = 72975
API_TODO = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{}?nult={}"
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


def extra(anterior: dict) -> dict:
    """IRAV y serie larga del índice general. Nunca hace fallar el script."""
    out = {"irav": anterior.get("irav", {}), "historico": anterior.get("historico", {})}
    try:
        datos = requests.get(API_TODO.format(TABLA_IRAV, 36), headers={"User-Agent": UA}, timeout=120).json()
        irav = {}
        for s in datos:
            for x in s.get("Data", []):
                if x.get("Valor") is not None and 1 <= int(x.get("FK_Periodo", 0)) <= 12:
                    irav[f"{x['Anyo']}-{int(x['FK_Periodo']):02d}"] = x["Valor"]
            if irav:
                break
        if irav:
            out["irav"] = dict(sorted(irav.items()))
    except Exception as e:  # noqa: BLE001
        aviso("warning", f"IRAV: {type(e).__name__}: {str(e)[:200]}")
    try:
        datos = requests.get(API_TODO.format(TABLAS["grupos"], 600), headers={"User-Agent": UA}, timeout=180).json()
        for s in datos:
            partes = [p.strip() for p in s.get("Nombre", "").split(".") if p.strip()]
            if len(partes) >= 3 and partes[0] in ("Nacional", "Total Nacional") and re.match(r"(?i)índice general", partes[1]) and partes[-1] == "Índice":
                hist = {f"{x['Anyo']}-{int(x['FK_Periodo']):02d}": x["Valor"] for x in s.get("Data", [])
                        if x.get("Valor") is not None and 1 <= int(x["FK_Periodo"]) <= 12}
                if len(hist) > len(out["historico"]):
                    out["historico"] = dict(sorted(hist.items()))
                break
    except Exception as e:  # noqa: BLE001
        aviso("warning", f"Serie larga del IPC: {type(e).__name__}: {str(e)[:200]}")
    return out


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
    anterior = {}
    if OUT.exists():
        try:
            anterior = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            anterior = {}
    mas = extra(anterior)
    salida = {
        "fuente": "INE, Índice de Precios de Consumo (base 2025, ECOICOP ver. 2)",
        "actualizado": datetime.now(ZoneInfo("Europe/Madrid")).replace(microsecond=0).isoformat(),
        "mes": ultimo,
        "general": general,
        "grupos": {k: v for k, v in grupos.items() if v is not general},
        "subclases": subclases,
        "irav": mas["irav"],
        "historico": mas["historico"],
    }
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    hist = mas["historico"]
    aviso("notice", f"{ultimo}: IPC general {general['va'][ultimo]} % anual · {len(grupos)} grupos · {len(subclases)} subclases · "
                    f"IRAV {len(mas['irav'])} meses (último {max(mas['irav']) if mas['irav'] else '—'}) · "
                    f"histórico {min(hist) if hist else '—'} a {max(hist) if hist else '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
