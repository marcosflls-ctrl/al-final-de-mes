"""Comprueba qué fuentes de datos responden desde GitHub. Resultado en las anotaciones de la ejecución."""
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
CANDIDATAS = {
    "minetur provincias https": "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Provincias/",
    "minetur provincias http": "http://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Provincias/",
    "minetur Madrid": "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroProvincia/28",
    "geoportal": "https://geoportalgasolineras.es/",
    "datos.gob.es carburantes": "https://datos.gob.es/apidata/catalog/dataset/title/carburantes?_pageSize=5",
    "ipinfo": "https://ipinfo.io/json",
}
fila = []
for nombre, url in CANDIDATAS.items():
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json,*/*"}, timeout=40)
        fila.append(f"{nombre}: {r.status_code} {len(r.content)}B {r.text[:80]!r}")
    except Exception as e:  # noqa: BLE001
        fila.append(f"{nombre}: {type(e).__name__} {str(e)[:80]}")
for f in fila:
    print("::notice title=Prueba::" + f.replace("\n", " "))
