"""
Alerta de fechas de cobro: busca en las fuentes del radar noticias sobre qué día pagan los bancos
la pensión o el paro. Si son de un mes que todavía no está en src/data/cobros.json, abre un aviso
(issue) en GitHub con los enlaces, para actualizar el calendario. No escribe nada en la web.

Uso: python scripts/alerta_cobros.py   (en GitHub usa GITHUB_TOKEN y GITHUB_REPOSITORY)
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import feedparser
import requests

ROOT = Path(__file__).resolve().parent.parent
FEEDS = json.loads((ROOT / "scripts" / "feeds.json").read_text(encoding="utf-8"))["feeds"]
COBROS = json.loads((ROOT / "src" / "data" / "cobros.json").read_text(encoding="utf-8"))
ESTADO = ROOT / "scripts" / "state" / "alertas-cobros.json"
UA = "Mozilla/5.0 (compatible; AlFinalDeMesRadar/1.0; +https://alfinaldemes.com)"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
BANCOS = r"banco|bancos|entidad|caixabank|santander|bbva|ing\b|unicaja|sabadell|bankinter|ibercaja|abanca|kutxabank|cajamar"


def norm(t: str) -> str:
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def clasificar(titulo: str) -> str | None:
    """'pensiones', 'paro' o None según de qué hable el titular."""
    t = norm(titulo)
    if not re.search(r"cobr|ingres|pag[ao]|fecha|adelant", t) or not re.search(norm(BANCOS) + r"|que dia|cuando|calendario|pago de", t):
        return None
    if re.search(r"pension|jubilad|paga extra", t):
        return "pensiones"
    if re.search(r"\bparo\b|desempleo|sepe|subsidio", t):
        return "paro"
    return None


def mes_de(titulo: str, ahora: datetime) -> str:
    """Mes del que habla el titular (AAAA-MM); si no nombra ninguno, el actual."""
    t = norm(titulo)
    for i, m in enumerate(MESES, start=1):
        if re.search(rf"\b{m}\b", t):
            anio = ahora.year + (1 if i < ahora.month - 2 else 0)  # «enero» dicho en noviembre es del año siguiente
            return f"{anio}-{i:02d}"
    return f"{ahora.year}-{ahora.month:02d}"


def ya_en_calendario(tipo: str, mes: str) -> bool:
    return any(m["mes"] == mes and not m.get("pendiente") for m in COBROS[tipo]["meses"])


def main() -> int:
    ahora = datetime.now(ZoneInfo("Europe/Madrid"))
    try:
        vistos = set(json.loads(ESTADO.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        vistos = set()

    nuevas: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    for feed in FEEDS:
        try:
            entradas = feedparser.parse(feed["url"], agent=UA).entries
        except Exception:  # noqa: BLE001
            continue
        for e in entradas[:50]:
            titulo, url = e.get("title", ""), e.get("link", "")
            tipo = clasificar(titulo)
            if not tipo or not url or url in vistos:
                continue
            vistos.add(url)
            mes = mes_de(titulo, ahora)
            if mes < f"{ahora.year}-{ahora.month:02d}" or ya_en_calendario(tipo, mes):
                continue
            nuevas.setdefault((tipo, mes), []).append((feed["name"], titulo, url))

    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(sorted(vistos)[-2000:], ensure_ascii=False, indent=0), encoding="utf-8")
    if not nuevas:
        print("Sin noticias nuevas sobre fechas de cobro")
        return 0

    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    for (tipo, mes), lista in nuevas.items():
        nombre = f"{MESES[int(mes[5:]) - 1]} de {mes[:4]}"
        que = "la pensión" if tipo == "pensiones" else "el paro"
        titulo = f"📅 Fechas de cobro de {que} de {nombre}"
        cuerpo = (f"Han salido noticias sobre qué día pagan los bancos {que} de {nombre}, "
                  f"y el calendario de la web todavía no tiene ese mes.\n\n"
                  + "\n".join(f"- [{t}]({u}) — {f}" for f, t, u in lista)
                  + f"\n\nPara actualizarlo, pídele a Claude: «actualiza el calendario de cobro de {que} de {nombre}». "
                  f"Página: https://alfinaldemes.com/{tipo}/cuando-se-cobra/")
        print(f"→ {titulo}: {len(lista)} noticias")
        if not (token and repo):
            continue
        api = f"https://api.github.com/repos/{repo}/issues"
        cab = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        abiertos = requests.get(api, headers=cab, params={"state": "open", "labels": "calendario"}, timeout=20).json()
        previo = next((i for i in abiertos if isinstance(i, dict) and i.get("title") == titulo), None)
        if previo:  # ya hay aviso de ese mes: se añaden los enlaces nuevos como comentario
            requests.post(previo["comments_url"], headers=cab, json={"body": "\n".join(f"- [{t}]({u}) — {f}" for f, t, u in lista)}, timeout=20)
        else:
            requests.post(api, headers=cab, json={"title": titulo, "body": cuerpo, "labels": ["calendario"],
                                                   "assignees": [repo.split("/")[0]]}, timeout=20)
        tg, chat = os.environ.get("TG_TOKEN"), os.environ.get("TG_CHAT")
        if tg and chat and not previo:
            requests.post(f"https://api.telegram.org/bot{tg}/sendMessage",
                          data={"chat_id": chat, "text": f"{titulo}: hay noticias nuevas. Revisa el aviso en GitHub."}, timeout=20)
    return 0


if __name__ == "__main__":
    sys.exit(main())
