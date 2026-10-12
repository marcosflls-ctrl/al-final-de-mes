"""Comprueba qué fuentes responden (para elegir las de scripts/feeds.json). Resultado en las anotaciones de GitHub."""
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import feedparser
import requests

UA = "Mozilla/5.0 (compatible; AlFinalDeMesRadar/1.0; +https://alfinaldemes.com)"
CANDIDATAS = {
    "SegSocial revista /feed": "https://revista.seg-social.es/feed",
    "SegSocial revista /feed/": "https://revista.seg-social.es/feed/",
    "SegSocial revista rss": "https://revista.seg-social.es/rss",
    "SegSocial revista ?feed=rss2": "https://revista.seg-social.es/?feed=rss2",
    "elEconomista economia": "https://www.eleconomista.es/rss/rss-economia.php",
    "elEconomista ecoaula/actualidad": "https://www.eleconomista.es/rss/rss-category.php?category=economia",
    "elEconomista portada": "https://www.eleconomista.es/rss/rss-portada.php",
    "Cinco Días": "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.elpais.com/portada",
    "El Confidencial economía": "https://rss.elconfidencial.com/economia/",
    "Expansión economía": "https://e00-expansion.uecdn.es/rss/economia.xml",
    "El Mundo economía": "https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml",
    "La Vanguardia economía": "https://www.lavanguardia.com/rss/economia.xml",
    "ABC economía": "https://www.abc.es/rss/2.0/economia/",
    "El Periódico economía": "https://www.elperiodico.com/es/rss/economia/rss.xml",
    "La Información": "https://www.lainformacion.com/rss/",
    "Newtral": "https://www.newtral.es/feed/",
    "Maldita dinero": "https://maldita.es/feed/",
    "Idealista news": "https://www.idealista.com/news/rss/v2/latest-news.xml",
    "OCU": "https://www.ocu.org/rss/actualidad",
    "INE prensa": "https://www.ine.es/dyngs/Prensa/rss.xml",
    "INE novedades": "https://www.ine.es/rss/novedades.xml",
    "Moncloa Consejo de Ministros": "https://www.lamoncloa.gob.es/consejodeministros/Paginas/rss.aspx",
    "Moncloa notas prensa": "https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/Paginas/rss.aspx",
    "AEAT novedades": "https://sede.agenciatributaria.gob.es/Sede/novedades.rss",
    "Banco de España": "https://www.bde.es/wbe/es/noticias-eventos/actualidad-banco-espana/rss/",
    "CNMC": "https://www.cnmc.es/rss.xml",
}

fila = []
for nombre, url in CANDIDATAS.items():
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        n = len(feedparser.parse(r.content).entries) if r.ok else 0
        fila.append(f"{nombre}: {r.status_code}/{n}")
    except Exception as e:  # noqa: BLE001
        fila.append(f"{nombre}: {type(e).__name__}")

# BOE: los últimos días laborables
boe = []
hoy = datetime.now(ZoneInfo("Europe/Madrid")).date()
for i in range(0, 5):
    d = hoy - timedelta(days=i)
    try:
        r = requests.get(f"https://www.boe.es/datosabiertos/api/boe/sumario/{d:%Y%m%d}",
                         headers={"Accept": "application/json", "User-Agent": UA}, timeout=20)
        ok = r.headers.get("content-type", "")
        n = r.text.count('"identificador"') if r.ok else 0
        boe.append(f"{d}: {r.status_code} {ok.split(';')[0]} items={n}")
    except Exception as e:  # noqa: BLE001
        boe.append(f"{d}: {type(e).__name__}")

mitad = len(fila) // 2
print("::notice title=Fuentes 1::" + " · ".join(fila[:mitad]))
print("::notice title=Fuentes 2::" + " · ".join(fila[mitad:]))
print("::notice title=BOE::" + " · ".join(boe))
