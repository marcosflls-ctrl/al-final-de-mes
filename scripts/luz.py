"""
Precio de la luz (PVPC) de hoy y de mañana, hora a hora, con los datos públicos de Red Eléctrica.

Guarda src/data/luz.json, que usa la página /luz/. Si nada ha cambiado, no toca el archivo
(así GitHub no publica la web sin necesidad).

Uso:  python scripts/luz.py
Red Eléctrica publica los precios del día siguiente cada tarde, hacia las 20:15.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "luz.json"
MADRID = ZoneInfo("Europe/Madrid")
API = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
PVPC_ID = "1001"           # serie "PVPC" (tarifa regulada 2.0TD), en €/MWh, sin impuestos
DIAS_GUARDADOS = 8
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"


def precios_dia(dia: date) -> list[dict] | None:
    """Precios PVPC de un día, hora a hora, en €/kWh. None si aún no están publicados."""
    params = {"start_date": f"{dia.isoformat()}T00:00", "end_date": f"{dia.isoformat()}T23:59", "time_trunc": "hour"}
    r = requests.get(API, params=params, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=30)
    if r.status_code in (400, 404, 500, 502, 503):
        return None
    r.raise_for_status()
    serie = next((s for s in r.json().get("included", []) if str(s.get("id")) == PVPC_ID), None)
    if not serie:
        return None
    horas, vistas = [], {}
    for v in serie["attributes"]["values"]:
        t = datetime.fromisoformat(v["datetime"]).astimezone(MADRID)
        if t.date() != dia:
            continue
        etiqueta = t.strftime("%H:00")
        vistas[etiqueta] = vistas.get(etiqueta, 0) + 1
        if vistas[etiqueta] == 2:          # día del cambio de hora de octubre: la 02:00 se repite
            etiqueta += " (2.ª)"
        horas.append({"h": etiqueta, "p": round(v["value"] / 1000, 5)})
    # Un día normal tiene 24 horas (23 o 25 en los cambios de hora); si faltan, aún no está completo
    return horas if len(horas) >= 23 else None


def main() -> int:
    ahora = datetime.now(MADRID)
    hoy = ahora.date()
    try:
        datos = json.loads(OUT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        datos = {"dias": {}}
    dias: dict = datos.get("dias", {})

    for dia in (hoy, hoy + timedelta(days=1)):
        if dia.isoformat() in dias and dia != hoy:
            continue  # mañana ya descargado
        try:
            horas = precios_dia(dia)
        except requests.RequestException as e:
            print(f"! {dia}: {e}")
            continue
        if horas:
            dias[dia.isoformat()] = horas
            print(f"✓ {dia}: {len(horas)} horas")
        else:
            print(f"– {dia}: todavía sin publicar")

    if hoy.isoformat() not in dias:
        print("! No hay precios de hoy: no se cambia nada")
        return 1

    # solo los últimos días, para que el archivo no crezca sin fin
    limite = (hoy - timedelta(days=DIAS_GUARDADOS)).isoformat()
    dias = {k: v for k, v in sorted(dias.items()) if k >= limite}
    nuevo = {"hoy": hoy.isoformat(), "fuente": "Red Eléctrica (PVPC, tarifa 2.0TD, sin impuestos)", "dias": dias}
    antes = {k: datos.get(k) for k in ("hoy", "fuente", "dias")}
    if nuevo == antes:
        print("Sin cambios")
        return 0
    nuevo["actualizado"] = ahora.replace(microsecond=0).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Guardado src/data/luz.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
