"""Prueba fuentes de datos desde los servidores de GitHub. Resultado en las anotaciones de la ejecución."""
import csv, io
import requests
UA = "Mozilla/5.0 (compatible; DineroEnClaro/1.0; +https://dineroenclaro.com)"
def nota(t, m): print(f"::notice title={t}::{m[:3900]}")
for t in ("ti_1_3", "ti_1_4", "ti_1_6"):
    r = requests.get(f"https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/{t}.csv", headers={"User-Agent": UA}, timeout=60)
    r.encoding = "latin-1"
    filas = list(csv.reader(io.StringIO(r.text)))
    cods = filas[0]; desc = next(f for f in filas if f and f[0].startswith("DESCRIPCI") and "SERIE" in f[0])
    nota(t + " columnas", " || ".join(f"{c}: {d[-110:]}" for c, d in zip(cods[1:], desc[1:])))
    datos = [f for f in filas if f and f[0][:2].strip().isdigit()]
    ult = []
    for j in range(1, len(cods)):
        vals = [(f[0], f[j]) for f in datos if j < len(f) and f[j] not in ("", "_")]
        if vals: ult.append(f"{cods[j]} → {vals[-1]} (n={len(vals)}, desde {vals[0][0]})")
    nota(t + " ultimos", " || ".join(ult))
