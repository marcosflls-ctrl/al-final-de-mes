"""
Cambio oficial del euro (tipos de referencia del Banco Central Europeo), descargado de la API
gratuita Frankfurter (https://frankfurter.dev), que sirve los datos del BCE sin clave.

Guarda en src/data/divisas.json el cambio del último día publicado, el del día anterior, el de
hace un año y la serie diaria del último año de cada divisa. El BCE publica un dato por día hábil,
hacia las 16:00 de España.

Uso: python scripts/divisas.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "divisas.json"
API = "https://api.frankfurter.dev/v1"
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"

# Divisas que mostramos, en este orden (todas las publica el BCE).
DIVISAS = {
    "USD": "Dólar estadounidense",
    "GBP": "Libra esterlina",
    "CHF": "Franco suizo",
    "JPY": "Yen japonés",
    "MXN": "Peso mexicano",
    "BRL": "Real brasileño",
    "CAD": "Dólar canadiense",
    "AUD": "Dólar australiano",
    "CNY": "Yuan chino",
    "SEK": "Corona sueca",
    "NOK": "Corona noruega",
    "DKK": "Corona danesa",
    "PLN": "Esloti polaco",
    "CZK": "Corona checa",
    "HUF": "Florín húngaro",
    "RON": "Leu rumano",
    "TRY": "Lira turca",
    "INR": "Rupia india",
    "ZAR": "Rand sudafricano",
}


def aviso(tipo: str, texto: str) -> None:
    print(texto)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{tipo} title=Divisas::{texto}")


def main() -> int:
    hoy = date.today()
    desde = hoy - timedelta(days=400)
    url = f"{API}/{desde.isoformat()}..?base=EUR&symbols={','.join(DIVISAS)}"
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        datos = r.json()
    except Exception as e:  # noqa: BLE001
        aviso("error", f"{type(e).__name__}: {str(e)[:300]}")
        return 1

    dias: dict[str, dict[str, float]] = dict(sorted((datos.get("rates") or {}).items()))
    if len(dias) < 200:
        aviso("error", f"Solo {len(dias)} días de cambios: no se cambia nada")
        return 1

    fechas = list(dias)
    ultimo, anterior = fechas[-1], fechas[-2]
    # El día hábil más cercano a hace un año (sin pasarse)
    objetivo = (date.fromisoformat(ultimo) - timedelta(days=365)).isoformat()
    hace_un_anio = max((f for f in fechas if f <= objetivo), default=fechas[0])

    divisas = []
    for cod, nombre in DIVISAS.items():
        v = dias[ultimo].get(cod)
        if v is None:
            continue
        divisas.append({
            "codigo": cod,
            "nombre": nombre,
            "valor": v,
            "anterior": dias[anterior].get(cod),
            "hace_un_anio": dias[hace_un_anio].get(cod),
        })
    if len(divisas) < 10:
        aviso("error", f"Solo {len(divisas)} divisas en el último día: no se cambia nada")
        return 1

    ultimos_365 = [f for f in fechas if f > (date.fromisoformat(ultimo) - timedelta(days=366)).isoformat()]
    salida = {
        "fuente": "Banco Central Europeo (tipos de cambio de referencia del euro), vía Frankfurter",
        "actualizado": datetime.now(ZoneInfo("Europe/Madrid")).replace(microsecond=0).isoformat(),
        "fecha": ultimo,
        "fecha_anterior": anterior,
        "fecha_hace_un_anio": hace_un_anio,
        "divisas": divisas,
        # Serie diaria del último año solo de las divisas con gráfico, para no inflar la web
        "series": {c: {f: dias[f][c] for f in ultimos_365 if c in dias[f]} for c in ("USD", "GBP", "CHF", "MXN")},
    }
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    usd = next(d for d in divisas if d["codigo"] == "USD")
    aviso("notice", f"{ultimo}: 1 € = {usd['valor']} $ ({len(divisas)} divisas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
