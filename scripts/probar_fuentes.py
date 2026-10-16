"""Prueba fuentes de datos desde los servidores de GitHub. Resultado en las anotaciones de la ejecución."""
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PRUEBAS = {
    "BCE mensual": "https://data-api.ecb.europa.eu/service/data/FM/M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA?format=csvdata&lastNObservations=3",
    "BCE diario": "https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.RT.MM.EURIBOR1YD_.HSTA?format=csvdata&lastNObservations=3",
    "BdE ti_1_7": "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv",
    "EMMI hist 2026": "https://www.emmi-benchmarks.eu/assets/modules/rateisblue/processed_files/hist_EURIBOR_2026.csv",
    "euribor-rates": "https://www.euribor-rates.eu/es/tipos-euribor-actuales/4/euribor-valor-12-meses/",
}
for nombre, url in PRUEBAS.items():
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=40)
        txt = r.text.replace("\n", " ⏎ ")
        trozo = txt[:350] if "html" not in r.headers.get("content-type", "") else txt[txt.find("12 meses"):][:350]
        print(f"::notice title={nombre}::{r.status_code} {len(r.content)}B {r.headers.get('content-type')} | {trozo}")
    except Exception as e:  # noqa: BLE001
        print(f"::notice title={nombre}::{type(e).__name__}: {str(e)[:200]}")
