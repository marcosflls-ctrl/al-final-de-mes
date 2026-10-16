"""
Precio de la gasolina 95 y el gasóleo A hoy, en España y por provincia, con los datos abiertos
del Ministerio para la Transición Ecológica (Geoportal de Hidrocarburos).

Descarga el listado de todas las gasolineras (varios MB) y guarda un resumen ligero en
src/data/carburantes.json: medias nacionales y provinciales, las más baratas y la evolución diaria.

Uso:  python scripts/carburantes.py
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import unicodedata
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "carburantes.json"
MADRID = ZoneInfo("Europe/Madrid")
API = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"
COMBUSTIBLES = {"g95": "Precio Gasolina 95 E5", "diesel": "Precio Gasoleo A"}
BARATAS = 5            # gasolineras más baratas que se guardan por provincia y combustible
DIAS_HISTORICO = 90
# Precios fuera de este rango (€/l) se consideran errores de la fuente y se ignoran
MIN_OK, MAX_OK = 0.8, 3.5


def slug(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def num(v) -> float | None:
    try:
        x = float(str(v).replace(",", "."))
    except ValueError:
        return None
    return x if MIN_OK <= x <= MAX_OK else None


def bonito(t: str) -> str:
    """'MADRID' -> 'Madrid', 'CORUÑA (A)' -> 'A Coruña', 'BALEARS (ILLES)' -> 'Illes Balears'."""
    t = t.strip()
    m = re.match(r"^(.*)\s+\((.*)\)$", t)
    if m:
        t = f"{m.group(2)} {m.group(1)}"
    return " ".join(w.capitalize() if len(w) > 2 or i == 0 else w.lower() for i, w in enumerate(t.lower().split()))


def resumen(precios: list[float]) -> dict:
    return {"media": round(statistics.fmean(precios), 3), "min": min(precios), "max": max(precios), "n": len(precios)}


def main() -> int:
    try:
        r = requests.get(API, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=180)
        r.raise_for_status()
        datos = json.loads(r.content.decode("utf-8-sig"))  # la respuesta puede traer BOM
    except Exception as e:  # noqa: BLE001
        aviso = f"{type(e).__name__}: {str(e)[:300]}"
        print(f"! {aviso}")
        if os.environ.get("GITHUB_ACTIONS"):
            extra = f" · estado {r.status_code} · inicio {r.text[:120]!r}" if "r" in locals() else ""
            print(f"::error title=Carburantes::{aviso}{extra}")
        return 1
    if datos.get("ResultadoConsulta") != "OK" or not datos.get("ListaEESSPrecio"):
        print(f"! Respuesta inesperada: {datos.get('ResultadoConsulta')}")
        return 1
    estaciones = datos["ListaEESSPrecio"]
    print(f"{len(estaciones)} gasolineras · fecha de la fuente: {datos.get('Fecha')}")

    nacional = {k: [] for k in COMBUSTIBLES}
    provincias: dict[str, dict] = {}
    for e in estaciones:
        prov = e.get("Provincia", "").strip()
        if not prov:
            continue
        nombre = bonito(prov)
        # "Valencia / València" -> valencia; "Araba/Álava" -> alava (como lo busca la gente)
        clave = slug(nombre.split("/")[0])
        clave = {"araba": "alava"}.get(clave, clave)
        p = provincias.setdefault(prov, {"nombre": nombre, "slug": clave, "precios": {k: [] for k in COMBUSTIBLES}})
        for k, campo in COMBUSTIBLES.items():
            precio = num(e.get(campo, ""))
            if precio is None:
                continue
            nacional[k].append(precio)
            p["precios"][k].append({
                "p": precio,
                "rotulo": (e.get("Rótulo") or "").strip().title(),
                "direccion": (e.get("Dirección") or "").strip().title(),
                "localidad": bonito(e.get("Localidad") or e.get("Municipio") or ""),
                "cp": (e.get("C.P.") or "").strip(),
            })

    salida_prov = []
    for prov, p in sorted(provincias.items(), key=lambda x: x[1]["slug"]):
        fila = {"nombre": p["nombre"], "slug": p["slug"]}
        for k in COMBUSTIBLES:
            lista = p["precios"][k]
            if not lista:
                continue
            fila[k] = resumen([x["p"] for x in lista])
            fila[f"baratas_{k}"] = sorted(lista, key=lambda x: x["p"])[:BARATAS]
        salida_prov.append(fila)

    ahora = datetime.now(MADRID)
    hoy = ahora.date().isoformat()
    try:
        anterior = json.loads(OUT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        anterior = {}
    historico = anterior.get("historico", {})
    historico[hoy] = {k: round(statistics.fmean(v), 3) for k, v in nacional.items() if v}
    historico = dict(sorted(historico.items())[-DIAS_HISTORICO:])

    salida = {
        "fecha": hoy,
        "fecha_fuente": datos.get("Fecha"),
        "actualizado": ahora.replace(microsecond=0).isoformat(),
        "fuente": "Ministerio para la Transición Ecológica y el Reto Demográfico (Geoportal de Hidrocarburos)",
        "gasolineras": len(estaciones),
        "nacional": {k: resumen(v) for k, v in nacional.items() if v},
        "provincias": salida_prov,
        "historico": historico,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = salida["nacional"]
    print(f"✓ Gasolina 95: {n['g95']['media']} €/l · Gasóleo A: {n['diesel']['media']} €/l · {len(salida_prov)} provincias")
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::notice title=Carburantes::G95 {n['g95']['media']} · Diésel {n['diesel']['media']} · {len(estaciones)} gasolineras · {len(salida_prov)} provincias · fuente {datos.get('Fecha')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
