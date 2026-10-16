"""Busca de dónde carga sus datos el Geoportal de gasolineras. Resultado en las anotaciones de la ejecución."""
import re
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
BASE = "https://geoportalgasolineras.es/"
s = requests.Session()
s.headers["User-Agent"] = UA
html = s.get(BASE, timeout=40).text
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("::notice title=Scripts::" + " | ".join(scripts)[:900])
hallado = set()
for src in scripts:
    url = src if src.startswith("http") else BASE + src.lstrip("/")
    try:
        js = s.get(url, timeout=40).text
    except Exception:  # noqa: BLE001
        continue
    for m in re.findall(r'["\']([^"\']*(?:rest/|/rest|\.xls|\.csv|\.json|descarga|Precios|precios)[^"\']{0,80})["\']', js):
        if len(m) < 140:
            hallado.add(m)
print("::notice title=Rutas::" + " | ".join(sorted(hallado))[:3500])
for prueba in ["resources/files/preciosEESS_es.xls", "geoportal/resources/files/preciosEESS_es.xls"]:
    try:
        r = s.get(BASE + prueba, timeout=60)
        print(f"::notice title=Excel::{prueba}: {r.status_code} {len(r.content)}B {r.headers.get('content-type')}")
    except Exception as e:  # noqa: BLE001
        print(f"::notice title=Excel::{prueba}: {type(e).__name__}")
