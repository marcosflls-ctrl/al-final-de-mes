"""Prueba fuentes de datos desde los servidores de GitHub. Resultado en las anotaciones de la ejecución."""
import re
import requests
UA = "Mozilla/5.0 (compatible; DineroEnClaro/1.0; +https://dineroenclaro.com)"
def nota(t, m): print(f"::notice title={t}::{m[:3900]}")
# BCE: tipo de la facilidad de depósito y de las operaciones principales
for k in ("FM/D.U2.EUR.4F.KR.DFR.LEV", "FM/D.U2.EUR.4F.KR.MRR_FR.LEV"):
    try:
        r = requests.get(f"https://data-api.ecb.europa.eu/service/data/{k}?lastNObservations=3&format=csvdata", headers={"User-Agent": UA}, timeout=60)
        nota(k, f"{r.status_code} " + " | ".join(r.text.strip().splitlines()[-3:])[:1500])
    except Exception as e: nota(k, repr(e))
# Tesoro: últimas subastas de Letras
for u in ("https://www.tesoro.es/deuda-publica/subastas/resultado-ultimas-subastas/letras-del-tesoro",
          "https://www.tesoro.es/deuda-publica/subastas/resultado-ultimas-subastas"):
    try:
        r = requests.get(u, headers={"User-Agent": UA}, timeout=60)
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", r.text)))
        i = txt.find("Letras")
        nota(u[-40:], f"{r.status_code} len={len(r.text)} :: {txt[max(0,i-200):i+3000]}")
        links = sorted(set(re.findall(r'href="([^"]+\.(?:xlsx?|csv|pdf))"', r.text)))[:30]
        nota("enlaces " + u[-25:], " ".join(links)[:3800])
    except Exception as e: nota(u[-40:], repr(e))
# Banco de España: tablas de tipos (buscar columnas de Letras)
for t in ("ti_1_6", "ti_1_5", "ti_1_4", "ti_1_3", "ti_1_2", "be_22_2"):
    try:
        r = requests.get(f"https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/{t}.csv", headers={"User-Agent": UA}, timeout=60)
        r.encoding = "latin-1"
        filas = r.text.splitlines()
        nota(t, f"{r.status_code} " + " || ".join(f[:600] for f in filas[:6]) + " || ULTIMA: " + (filas[-1][:400] if filas else ""))
    except Exception as e: nota(t, repr(e))
