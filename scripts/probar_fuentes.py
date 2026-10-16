"""Prueba fuentes de datos desde los servidores de GitHub. Resultado en las anotaciones de la ejecución."""
import csv, io
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
r = requests.get("https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv", headers={"User-Agent": UA}, timeout=60)
filas = list(csv.reader(io.StringIO(r.content.decode("latin-1"))))
cab = [f for f in filas[:8]]
datos = [f for f in filas if f and f[0][:1].isdigit() or (f and f[0][:3].upper() in ("ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"))]
for j in range(1, len(filas[0])):
    meta = " | ".join(f[j] for f in cab if len(f) > j)
    ult = " ; ".join(f"{f[0]}={f[j]}" for f in filas[-4:] if len(f) > j)
    print(f"::notice title=col{j}::{meta[:600]} || {ult}")
print(f"::notice title=filas::{len(filas)} primeras: {[f[0] for f in filas[:10]]} últimas: {[f[0] for f in filas[-3:]]}")
