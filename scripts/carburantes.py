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
OUT_CIUDADES = ROOT / "src" / "data" / "carburantes-ciudades.json"
MADRID = ZoneInfo("Europe/Madrid")
API = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
# El servicio anterior rechaza conexiones desde fuera de España (como los servidores de GitHub);
# la descarga en Excel del propio Geoportal sí funciona y trae los mismos datos.
EXCEL = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"
COMBUSTIBLES = {"g95": "Precio Gasolina 95 E5", "diesel": "Precio Gasoleo A"}
BARATAS = 5            # gasolineras más baratas que se guardan por provincia y combustible
DIAS_HISTORICO = 90
MIN_GASOLINERAS_CIUDAD = 10   # municipios con al menos estas gasolineras tienen página propia
# Las capitales de provincia tienen página aunque tengan menos (Bilbao tiene pocas dentro del municipio)
MIN_GASOLINERAS_CAPITAL = 4
CAPITALES = ("bilbao", "vitoria-gasteiz", "donostia", "pamplona", "logrono", "santander", "oviedo", "leon", "palencia",
             "burgos", "soria", "segovia", "avila", "zamora", "salamanca", "valladolid", "lugo", "ourense", "pontevedra",
             "a-coruna", "huesca", "teruel", "zaragoza", "lleida", "girona", "tarragona", "barcelona", "castellon",
             "valencia", "alicante", "murcia", "albacete", "cuenca", "guadalajara", "toledo", "ciudad-real", "caceres",
             "badajoz", "huelva", "sevilla", "cadiz", "malaga", "cordoba", "jaen", "granada", "almeria", "madrid",
             "palma", "las-palmas-de-gran-canaria", "santa-cruz-de-tenerife", "ceuta", "melilla")
BARATAS_CIUDAD = 10
DIAS_HISTORICO_CIUDAD = 9   # para comparar con hace una semana aunque falle algún día
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


MENORES = {"de", "del", "la", "las", "los", "el", "i", "y", "en", "d'", "l'"}


def bonito(t: str) -> str:
    """'MADRID' -> 'Madrid', 'CORUÑA (A)' -> 'A Coruña', 'VITORIA-GASTEIZ' -> 'Vitoria-Gasteiz',
    'CERDANYOLA DEL VALLES' -> 'Cerdanyola del Vallès', "L' HOSPITALET" -> "L'Hospitalet"."""
    t = t.strip()
    m = re.match(r"^(.*)\s+\((.*)\)$", t)
    if m:
        t = f"{m.group(2)} {m.group(1)}"
    t = re.sub(r"([dl]')\s+", r"\1", t.lower())

    def palabra(w: str, primera: bool) -> str:
        if not primera and w in MENORES:
            return w
        if re.match(r"^[dl]'.", w):                       # l'hospitalet -> L'Hospitalet
            return w[:2].upper() + w[2:3].upper() + w[3:] if primera else w[:2] + w[2:3].upper() + w[3:]
        return w[:1].upper() + w[1:]

    partes = re.split(r"(\s+|/|-)", t)
    salida, primera = [], True
    for x in partes:
        if not x or re.fullmatch(r"\s+|/|-", x):
            salida.append(x)
            if x in ("/", "-"):
                primera = True
            continue
        salida.append(palabra(x, primera))
        primera = False
    return "".join(salida)


def _norm(t) -> str:
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def desde_excel() -> tuple[list[dict], str]:
    """Lee el Excel del Geoportal y devuelve las gasolineras con los mismos campos que el servicio REST."""
    import io

    # El Geoportal a veces da 404 unos minutos mientras regenera el archivo: se reintenta
    import time
    for intento in range(4):
        r = requests.get(EXCEL, headers={"User-Agent": UA}, timeout=180)
        if r.status_code == 200 or intento == 3:
            break
        print(f"  · Geoportal respondió {r.status_code}, reintento en {60 * (intento + 1)} s")
        time.sleep(60 * (intento + 1))
    r.raise_for_status()
    contenido = r.content
    if contenido[:4] == b"\xd0\xcf\x11\xe0":                # Excel antiguo (.xls)
        import xlrd
        hoja = xlrd.open_workbook(file_contents=contenido).sheet_by_index(0)
        filas = [hoja.row_values(i) for i in range(hoja.nrows)]
    elif contenido[:2] == b"PK":                              # Excel moderno (.xlsx)
        import openpyxl
        hoja = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True).worksheets[0]
        filas = [list(f) for f in hoja.iter_rows(values_only=True)]
    else:                                                     # tabla HTML con extensión .xls
        import pandas as pd
        tabla = pd.read_html(io.BytesIO(contenido))[0]
        filas = [list(tabla.columns)] + tabla.astype(str).values.tolist()
    # La cabecera es la primera fila que contiene "Provincia"; antes hay líneas informativas (con la fecha)
    i_cab = next(i for i, f in enumerate(filas) if any(_norm(c) == "provincia" for c in f))
    fecha = " ".join(str(c) for f in filas[:i_cab] for c in f if c and re.search(r"\d{2}/\d{2}/\d{4}", str(c)))[:60]
    cab = [_norm(c) for c in filas[i_cab]]

    def col(*claves, evitar=()):
        for j, c in enumerate(cab):
            if all(k in c for k in claves) and not any(e in c for e in evitar):
                return j
        raise KeyError(f"columna {claves} no encontrada en {cab}")

    idx = {
        "Provincia": col("provincia"), "Localidad": col("localidad"), "C.P.": col("codigo postal"),
        "Dirección": col("direccion"), "Rótulo": col("rotulo"),
        "Precio Gasolina 95 E5": col("gasolina 95 e5", evitar=("premium",)),
        "Precio Gasoleo A": col("gasoleo a", evitar=("premium", "renovable")),
    }
    try:
        idx["Municipio"] = col("municipio")
    except KeyError:
        pass
    estaciones = []
    for f in filas[i_cab + 1:]:
        if len(f) <= max(idx.values()) or not str(f[idx["Provincia"]]).strip():
            continue
        e = {k: ("" if f[j] is None else str(f[j])) for k, j in idx.items()}
        e["C.P."] = e["C.P."].split(".")[0].zfill(5) if e["C.P."] else ""
        estaciones.append(e)
    return estaciones, fecha or "Excel del Geoportal"


def resumen(precios: list[float]) -> dict:
    return {"media": round(statistics.fmean(precios), 3), "min": min(precios), "max": max(precios), "n": len(precios)}


def main() -> int:
    try:
        estaciones, fecha_fuente = desde_excel()
    except Exception as e:  # noqa: BLE001
        aviso = f"{type(e).__name__}: {str(e)[:400]}"
        print(f"! {aviso}")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error title=Carburantes::{aviso}")
        return 1
    if len(estaciones) < 5000:  # en España hay más de 11.000: si salen pocas, algo ha fallado
        print(f"! Solo {len(estaciones)} gasolineras: no se cambia nada")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error title=Carburantes::Solo {len(estaciones)} gasolineras leídas")
        return 1
    print(f"{len(estaciones)} gasolineras · {fecha_fuente}")

    nacional = {k: [] for k in COMBUSTIBLES}
    provincias: dict[str, dict] = {}
    municipios: dict[tuple[str, str], dict] = {}
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
            g = {
                "p": precio,
                "rotulo": (e.get("Rótulo") or "").strip().title(),
                "direccion": (e.get("Dirección") or "").strip().title(),
                "localidad": bonito(e.get("Localidad") or e.get("Municipio") or ""),
                "cp": (e.get("C.P.") or "").strip(),
            }
            p["precios"][k].append(g)
            muni = (e.get("Municipio") or "").strip()
            if muni:
                m = municipios.setdefault((clave, muni), {"nombre": bonito(muni), "provincia": nombre, "provincia_slug": clave,
                                                          "precios": {kk: [] for kk in COMBUSTIBLES}})
                m["precios"][k].append(g)

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
        "fecha_fuente": fecha_fuente,
        "actualizado": ahora.replace(microsecond=0).isoformat(),
        "fuente": "Ministerio para la Transición Ecológica y el Reto Demográfico (Geoportal de Hidrocarburos)",
        "gasolineras": len(estaciones),
        "nacional": {k: resumen(v) for k, v in nacional.items() if v},
        "provincias": salida_prov,
        "historico": historico,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Ciudades: municipios con suficientes gasolineras para que la media signifique algo
    ciudades = []
    for (prov_slug, _), m in municipios.items():
        nombre_url = m["nombre"].split("/")[0].strip()
        capital = slug(nombre_url) in CAPITALES or slug(nombre_url).startswith(("donostia", "castellon", "palma-de-mallorca"))
        if len(m["precios"]["g95"]) < (MIN_GASOLINERAS_CAPITAL if capital else MIN_GASOLINERAS_CIUDAD):
            continue
        fila = {"nombre": m["nombre"], "slug": slug(nombre_url), "provincia": m["provincia"], "provincia_slug": prov_slug}
        for k in COMBUSTIBLES:
            lista = m["precios"][k]
            if lista:
                fila[k] = resumen([x["p"] for x in lista])
                fila[f"baratas_{k}"] = sorted(lista, key=lambda x: x["p"])[:BARATAS_CIUDAD]
        ciudades.append(fila)
    ciudades.sort(key=lambda c: (c["provincia_slug"], c["slug"]))
    # Histórico corto de medias por municipio, para mostrar cuánto ha cambiado en una semana
    try:
        hist_c = json.loads(OUT_CIUDADES.read_text(encoding="utf-8")).get("historico", {})
    except (FileNotFoundError, json.JSONDecodeError):
        hist_c = {}
    hist_c[hoy] = {f"{c['provincia_slug']}/{c['slug']}": [c.get(k, {}).get("media") for k in COMBUSTIBLES] for c in ciudades}
    hist_c = dict(sorted(hist_c.items())[-DIAS_HISTORICO_CIUDAD:])
    if ciudades:
        OUT_CIUDADES.write_text(json.dumps({"fecha": hoy, "actualizado": salida["actualizado"], "ciudades": ciudades,
                                            "historico": hist_c}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  {len(ciudades)} ciudades con página")
    n = salida["nacional"]
    print(f"✓ Gasolina 95: {n['g95']['media']} €/l · Gasóleo A: {n['diesel']['media']} €/l · {len(salida_prov)} provincias")
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::notice title=Carburantes::G95 {n['g95']['media']} · Diésel {n['diesel']['media']} · {len(estaciones)} gasolineras · {len(salida_prov)} provincias · {fecha_fuente}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
