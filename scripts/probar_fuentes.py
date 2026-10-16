"""Prueba fuentes de datos desde los servidores de GitHub. Resultado en las anotaciones de la ejecución."""
import requests
UA = "Mozilla/5.0 (compatible; AlFinalDeMes/1.0; +https://alfinaldemes.com)"
r = requests.get("https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/IPC", headers={"User-Agent": UA}, timeout=60)
print(f"::notice title=estado::{r.status_code} {len(r.content)}B")
tablas = r.json()
lineas = [f"{t.get('Id')}: {t.get('Nombre')}" for t in tablas]
for i in range(0, len(lineas), 25):
    print("::notice title=tablas " + str(i) + "::" + " || ".join(lineas[i:i + 25])[:3800])
