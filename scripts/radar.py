"""
Radar de noticias de Al Final de Mes.

1. Lee el sumario del BOE de hoy y los feeds de scripts/feeds.json
2. Se queda con lo que afecta a la economía de casa y aún no ha procesado
3. Descarga el texto y le pide a Claude un artículo ORIGINAL siguiendo la política editorial
4. Lo guarda como borrador .md en src/content/posts/ (con su imagen de portada)
   → GitHub te abre una propuesta para revisarlo antes de publicar

Uso:
  python scripts/radar.py              # normal (en GitHub usa la federación de identidades, sin clave;
                                       # en tu PC puedes usar ANTHROPIC_API_KEY=...)
  python scripts/radar.py --dry-run    # solo lista lo que encontraría
  python scripts/radar.py --url URL    # redacta solo esa noticia
Variables opcionales: MAX_PER_RUN (2), MODEL (claude-sonnet-5-5)
"""
from __future__ import annotations

import argparse
import calendar
import difflib
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portada import crear as crear_portada  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT / "scripts" / "feeds.json"
STATE_FILE = ROOT / "scripts" / "state" / "seen.json"
POSTS_DIR = ROOT / "src" / "content" / "posts"
IMG_DIR = ROOT / "public" / "img" / "articulos"
MADRID = ZoneInfo("Europe/Madrid")

MAX_AGE_HOURS = 36            # lo más antiguo ya no es noticia
MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "2"))
MODEL = os.environ.get("MODEL", "claude-sonnet-5-5")
MIN_SOURCE_CHARS = 500        # si no hay texto suficiente, no se escribe (evita inventar)
SIMILARITY_SKIP = 0.6         # títulos muy parecidos = misma noticia ya cubierta
UA = "Mozilla/5.0 (compatible; AlFinalDeMesRadar/1.0; +https://alfinaldemes.com)"
CATEGORIES = ["luz", "pensiones", "paro", "vivienda", "hacienda"]
BOE_API = "https://www.boe.es/datosabiertos/api/boe/sumario/{fecha}"
BOE_SECCIONES = {"1", "3"}    # I. Disposiciones generales · III. Otras disposiciones


# ---------- utilidades ----------
def slugify(text: str, max_len: int = 75) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    if len(text) > max_len:
        corte = text[:max_len + 1]
        # Cortar siempre en un guion para no dejar palabras a medias ("euribo", "sobrepreci")
        text = corte[:corte.rfind("-")] if "-" in corte else text[:max_len]
        # Y no terminar en palabras vacías ("...para-reclamar-el")
        vacias = {"a", "al", "con", "de", "del", "el", "en", "la", "las", "lo", "los",
                  "o", "para", "por", "que", "se", "su", "un", "una", "y"}
        partes = text.split("-")
        while len(partes) > 1 and partes[-1] in vacias:
            partes.pop()
        text = "-".join(partes)
    return text.rstrip("-") or "articulo"


def norm_title(t: str) -> str:
    return re.sub(r"\W+", " ", unicodedata.normalize("NFKD", t.lower())).strip()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"urls": [], "titles": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["urls"] = state["urls"][-4000:]
    state["titles"] = state["titles"][-2000:]
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def existing_posts() -> list[dict]:
    """Títulos y direcciones de lo ya escrito, para evitar duplicados y sugerir enlaces internos."""
    out = []
    for f in POSTS_DIR.glob("*.md"):
        txt = f.read_text(encoding="utf-8")
        if re.search(r"^draft:\s*true", txt, re.M):
            continue
        t = re.search(r'^title:\s*"?(.*?)"?\s*$', txt, re.M)
        c = re.search(r"^category:\s*(\w+)", txt, re.M)
        g = re.search(r"^guia:\s*true", txt, re.M)
        d = re.search(r"^date:\s*(\S+)", txt, re.M)
        if t and c:
            out.append({"title": t.group(1), "url": f"/{c.group(1)}/{f.stem}/", "guia": bool(g), "_fecha": d.group(1) if d else ""})
    # lo más reciente primero: es lo que más se puede repetir (en GitHub todos los archivos tienen la misma fecha de
    # modificación, así que se ordena por la fecha del artículo)
    out.sort(key=lambda x: x["_fecha"], reverse=True)
    return [{k: v for k, v in x.items() if k != "_fecha"} for x in out]


def is_similar(title: str, known: list[str]) -> bool:
    n = norm_title(title)
    return any(difflib.SequenceMatcher(None, n, k).ratio() >= SIMILARITY_SKIP for k in known)


def matches(text: str, kws: list[str]) -> bool:
    t = f" {text.lower()} "
    return any(re.search(rf"(?<!\w){re.escape(k)}(?!\w)", t) for k in kws)


RESUMEN: list[str] = []  # qué ha respondido cada fuente (se muestra en GitHub)


# ---------- 1. BOE ----------
def boe_items(cfg: dict, kws: list[str]) -> list[dict]:
    """Disposiciones del BOE de hoy de los departamentos elegidos que hablan de los temas de la web."""
    import requests

    fecha = datetime.now(MADRID).strftime("%Y%m%d")
    r = requests.get(BOE_API.format(fecha=fecha), headers={"Accept": "application/json", "User-Agent": UA}, timeout=30)
    if r.status_code == 404:
        RESUMEN.append("BOE de hoy aún no publicado")
        return []  # todavía no ha salido (se publica de madrugada) o es domingo
    r.raise_for_status()
    deps = [d.lower() for d in cfg.get("boe", {}).get("departamentos", [])]
    out: list[dict] = []

    def walk(o, seccion="", depto=""):
        if isinstance(o, list):
            for x in o:
                walk(x, seccion, depto)
            return
        if not isinstance(o, dict):
            return
        if "identificador" in o and "titulo" in o:
            if seccion in BOE_SECCIONES and any(d in depto.lower() for d in deps) and matches(o["titulo"], kws):
                url = o.get("url_html") or f"https://www.boe.es/diario_boe/txt.php?id={o['identificador']}"
                out.append({"source": "BOE", "title": o["titulo"], "url": url, "oficial": True})
            return
        if "codigo" in o and "departamento" in o:         # sección
            seccion = str(o.get("codigo", ""))
        elif "codigo" in o and "nombre" in o:              # departamento (los epígrafes no llevan código)
            depto = o.get("nombre", depto)
        for v in o.values():
            walk(v, seccion, depto)

    walk(r.json().get("data", {}))
    return out


# ---------- 1. feeds ----------
def collect_candidates(cfg: dict, state: dict, posts: list[dict]) -> list[dict]:
    import feedparser

    kws = [k.lower() for k in cfg["keywords"]]
    known_titles = state["titles"] + [norm_title(p["title"]) for p in posts]
    found = []

    def add(item: dict) -> None:
        if item["url"] in state["urls"]:
            return
        if is_similar(item["title"], known_titles):
            state["urls"].append(item["url"])
            return
        found.append(item)
        known_titles.append(norm_title(item["title"]))

    try:
        boe = boe_items(cfg, kws)
        print(f"  · BOE: {len(boe)} disposiciones de interés")
        RESUMEN.append(f"BOE {len(boe)}")
        for it in boe:
            add(it)
    except Exception as e:  # noqa: BLE001
        print(f"  ! BOE: {e}")
        RESUMEN.append(f"BOE error {type(e).__name__}")

    for feed in cfg["feeds"]:
        try:
            entries = feedparser.parse(feed["url"], agent=UA).entries
        except Exception as e:  # noqa: BLE001
            print(f"  ! {feed['name']}: {e}")
            RESUMEN.append(f"{feed['name']} error")
            continue
        print(f"  · {feed['name']}: {len(entries)} entradas")
        RESUMEN.append(f"{feed['name']} {len(entries)}")
        for e in entries[:40]:
            link, title = e.get("link", ""), e.get("title", "")
            pub = e.get("published_parsed") or e.get("updated_parsed")
            if pub and (time.time() - calendar.timegm(pub)) > MAX_AGE_HOURS * 3600:
                continue
            if not link or not matches(f"{title} {e.get('summary', '')}", kws):
                continue
            add({"source": feed["name"], "title": title, "url": link, "oficial": bool(feed.get("oficial"))})
    # lo oficial primero
    found.sort(key=lambda x: not x.get("oficial"))
    return found


# ---------- 2. leer la fuente ----------
def fetch_page(url: str) -> tuple[str, str]:
    """Devuelve (html, texto limpio)."""
    import requests
    import trafilatura

    try:
        html = requests.get(url, headers={"User-Agent": UA}, timeout=25).text
    except Exception:  # noqa: BLE001
        return "", ""
    return html, trafilatura.extract(html, include_comments=False, include_tables=True) or ""


def _domain(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).netloc.lower().removeprefix("www.")


def official_links(html: str) -> list[str]:
    """Enlaces a organismos oficiales que cita la fuente (para que la IA los use como fuente principal)."""
    dominios = ("boe.es", "seg-social.es", "sepe.es", "agenciatributaria.", "ine.es", "ree.es", "cnmc.es", "lamoncloa.gob.es", "gob.es")
    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html or "")
    out = []
    for l in links:
        if any(d in _domain(l) for d in dominios) and l not in out:
            out.append(l)
    return out[:8]


# ---------- 3. redactar con IA ----------
SYSTEM = """Eres redactor de Al Final de Mes, una web española que explica las noticias que afectan a la economía \
de casa: pensiones, paro y ayudas, Hacienda e impuestos, y la factura de la luz. Escribes en español de España, \
tuteando al lector, con tono cercano, claro y riguroso. Frases cortas. Nada de muletillas ("cabe destacar", \
"en este sentido", "sin lugar a dudas").

PRINCIPIOS (obligatorios):
- RESPUESTA ARRIBA: la entradilla y el primer párrafo responden ya a lo que promete el titular (quién, cuánto, \
cuándo, desde cuándo). Nunca escondas el dato.
- SOLO HECHOS DE LA FUENTE: usa únicamente los datos que aparecen en el texto fuente. Si algo no está, no lo \
afirmes. Nada de inventar cifras, fechas, requisitos ni citas. Si un cálculo es sencillo y se deduce de los datos \
(por ejemplo, aplicar una subida porcentual a una pensión de ejemplo), puedes hacerlo indicando que es un ejemplo.
- REDACCIÓN 100 % PROPIA: no copies frases ni la estructura del original. Explícalo como se lo explicarías a un \
familiar, con contexto útil.
- FUENTE OFICIAL: si la fuente es un medio y menciona un organismo o una norma (BOE, Seguridad Social, SEPE, \
Agencia Tributaria, INE…), atribúyelo a ese organismo y enlázalo si tienes su enlace. Si no hay respaldo oficial, \
atribúyelo al medio ("según publica X").
- ANUNCIADO ≠ APROBADO: si es una propuesta, un anteproyecto, un acuerdo pendiente o una promesa electoral, dilo \
claramente ("el Gobierno propone", "si se aprueba") y pon "pendiente": true. Solo es oficial lo publicado en el BOE.
- NEUTRALIDAD: no opines sobre partidos ni sobre si una medida es buena o mala. Si hay críticas relevantes, \
recógelas de forma equilibrada y atribuidas.
- SIN CONSEJO PERSONALIZADO: explica a quién afecta y qué hay que hacer (plazos, trámites), pero no recomiendes \
decisiones financieras personales.
- TITULAR HONESTO: con gancho y con la cifra o la fecha si la hay, pero que se cumpla en el texto. Prohibidos los \
titulares tipo "malas noticias para…", "lo que nadie te cuenta", "regala", "confirmado" sin dato, o los que ocultan \
de qué se habla.
- A QUIÉN AFECTA, EN EL TITULAR: si la medida es para un grupo concreto, nómbralo ("pensionistas", "inquilinos", \
"autónomos", "quien cobra el paro") para que el lector sepa al ver el titular si le toca. Es lo que más funciona en \
Google Discover sin exagerar.

QUÉ SE DESCARTA ({"skip": true, "reason": "..."}):
- Lo que no afecta directamente al bolsillo de una familia o un trabajador en España (macroeconomía, empresas, \
bolsa, política sin medida concreta, otros países).
- Nombramientos, convocatorias de empleo público, subvenciones a entidades concretas, correcciones de errores \
menores y trámites internos de la Administración.
- Lo que trata básicamente de lo mismo que alguno de los "artículos ya publicados", salvo que aporte un dato nuevo \
relevante (en ese caso, céntrate en lo nuevo). \
  Cuenta como repetición aunque el título sea distinto: el mismo informe, entrevista o reportaje contado por \
otro medio (por ejemplo, el mismo reportaje de Bloomberg o las mismas declaraciones de un directivo), o un \
detalle secundario de una noticia ya publicada. Revisa sobre todo los primeros de la lista, que son los más recientes.
- Refritos sin novedad, opiniones o textos sin datos.

LONGITUD: la marca lo que hay que contar. Un dato: 250-400 palabras. Una medida con requisitos y plazos: \
500-900 palabras. Nunca rellenes. Antes de responder, repasa la fuente y comprueba que no falta ningún dato \
relevante (cuantías, fechas, requisitos, a quién afecta, cómo se pide).

ESTRUCTURA: subtítulos ## que respondan a preguntas reales que la gente busca ("¿A quién afecta?", "¿Cuándo se \
cobra?", "¿Cómo se pide?"). Una tabla si hay cifras que comparar (tramos, cuantías, fechas). Listas para \
requisitos o pasos. Termina con lo que queda pendiente o el siguiente paso, sin frases hechas de cierre.

SECCIÓN (category), elige la que mejor encaje:
- luz: factura eléctrica, gas, butano, gasolina y diésel, bono social, energía en casa.
- pensiones: pensiones, jubilación, Seguridad Social de los jubilados.
- paro: salario mínimo, nóminas, huelgas, prestación y subsidios del SEPE, ingreso mínimo vital, ayudas a familias, cuotas de autónomos.
- vivienda: alquiler, prórrogas, desahucios, ayudas a la vivienda, compraventa, hipotecas y euríbor.
- hacienda: IRPF, declaración de la renta, IVA y otros impuestos, deducciones, avisos de la Agencia Tributaria.
Si un tema toca dos secciones (por ejemplo, una deducción fiscal por alquiler), elige la que busca el lector: quien busca su alquiler va a vivienda.

FUENTE OFICIAL: en "official_source" pon solo un enlace a la página concreta del documento o dato oficial (el BOE, la nota de prensa, la tabla del INE), nunca la portada de un organismo. Si no tienes ese enlace concreto, pon null.

ENLACES INTERNOS: incluye 1-3 enlaces a artículos de la lista "ya publicados" si encajan de forma natural, \
sobre todo a las guías.

FORMATO DE RESPUESTA: solo un objeto JSON válido, sin texto alrededor:
{
  "skip": false,
  "category": "luz" | "pensiones" | "paro" | "vivienda" | "hacienda",
  "pendiente": true | false,
  "title": "titular de 55-90 caracteres, concreto, con la cifra o fecha si existe",
  "card_title": "versión corta del titular para la imagen de portada, máximo 70 caracteres",
  "foto": "tema de la foto de portada que mejor encaja, de esta lista: {temas_foto}; o \"\" si ninguno encaja de verdad",
  "description": "entradilla de 130-160 caracteres que ya responde a la pregunta",
  "tags": ["3-5 etiquetas en minúsculas"],
  "official_source": {"name": "nombre del documento u organismo oficial", "url": "enlace oficial"} | null,
  "body": "artículo en Markdown, sin el título como # al principio"
}"""
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from banco import TEMAS as _TEMAS_FOTO, elegir as elegir_foto
except Exception:  # noqa: BLE001
    _TEMAS_FOTO, elegir_foto = [], None
SYSTEM = SYSTEM.replace("{temas_foto}", ", ".join(_TEMAS_FOTO) or "(ninguno)")

_CLIENT = None


def refresh_github_identity() -> None:
    """En GitHub Actions, pide un pase de identidad nuevo (caduca en minutos y es de un solo uso)."""
    import requests

    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    req_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    path = os.environ.get("ANTHROPIC_IDENTITY_TOKEN_FILE")
    if not (url and req_token and path):
        return
    r = requests.get(url, params={"audience": "https://api.anthropic.com"},
                     headers={"Authorization": f"Bearer {req_token}"}, timeout=15)
    r.raise_for_status()
    Path(path).write_text(r.json()["value"], encoding="utf-8")


def get_client():
    global _CLIENT
    if _CLIENT is None:
        import anthropic
        refresh_github_identity()
        _CLIENT = anthropic.Anthropic()
    return _CLIENT


def write_article(item: dict, source_text: str, oficiales: list[str], posts: list[dict]) -> dict | None:
    client = get_client()
    refresh_github_identity()
    related = "\n".join(f"- {'[GUÍA] ' if p['guia'] else ''}{p['title']} → {p['url']}" for p in posts[:150]) or "(ninguno aún)"
    hoy = datetime.now(MADRID).date().isoformat()
    user = (
        f"HOY ES: {hoy}\n"
        f"FUENTE: {item['source']}{' (oficial)' if item.get('oficial') else ''}\nTÍTULO ORIGINAL: {item['title']}\nURL: {item['url']}\n"
        + (f"ENLACES OFICIALES QUE CITA LA FUENTE:\n" + "\n".join(oficiales) + "\n" if oficiales else "")
        + f"\nTEXTO FUENTE:\n\"\"\"\n{source_text[:30000]}\n\"\"\"\n\n"
        f"ARTÍCULOS YA PUBLICADOS EN LA WEB:\n{related}"
    )
    msg = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM,
                                 messages=[{"role": "user", "content": user}])
    raw = "".join(b.text for b in msg.content if b.type == "text").strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("  ! respuesta no válida de la IA, se omite")
        return None
    if data.get("skip"):
        print(f"  – descartada: {data.get('reason', '')}")
        return None
    if data.get("category") not in CATEGORIES or not data.get("title") or not data.get("body"):
        print("  ! faltan campos, se omite")
        return None
    return data


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').strip() + '"'


def save_post(data: dict, item: dict) -> Path:
    slug = slugify(data["title"])
    path = POSTS_DIR / f"{slug}.md"
    i = 2
    while path.exists():
        path = POSTS_DIR / f"{slug}-{i}.md"
        i += 1
    slug = path.stem

    # Portada: una foto real del banco si encaja con la noticia (Discover las prefiere);
    # si no, la portada con el titular
    img_lines = ""
    foto = None
    try:
        foto = elegir_foto(data["title"], data["category"], data.get("foto") or "") if elegir_foto else None
    except Exception as e:  # noqa: BLE001
        print(f"  ! no se pudo elegir foto: {e}")
    if foto:
        img_lines = (f"image: /img/banco/{foto['slug']}.webp\nimageAlt: {yaml_str(foto['alt'])}\n"
                     f"imageCredit: {yaml_str(foto['credito'])}\nimageCreditUrl: {yaml_str(foto['pagina'])}\n")
    else:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from miniaturas import make_variants, make_crops
            img = crear_portada(data.get("card_title") or data["title"], data["category"], IMG_DIR / f"{slug}.webp")
            make_variants(img)
            make_crops(img)
            img_lines = f"image: /img/articulos/{slug}.webp\nimageAlt: {yaml_str('Portada: ' + data['title'][:140])}\n"
        except Exception as e:  # noqa: BLE001
            print(f"  ! no se pudo crear la portada: {e}")

    fuentes = []
    of = data.get("official_source") or {}
    from urllib.parse import urlparse
    concreta = len(urlparse(of.get("url", "")).path.strip("/")) > 0  # nada de portadas tipo "https://www.ine.es"
    if of.get("url", "").startswith("http") and of.get("name") and concreta:
        fuentes.append((of["name"], of["url"]))
    if not any(u == item["url"] for _, u in fuentes):
        fuentes.append((f"{item['source']}: {item['title'][:100]}", item["url"]))
    src_yaml = "".join(f"  - name: {yaml_str(n)}\n    url: {yaml_str(u)}\n" for n, u in fuentes)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    tags = ", ".join(yaml_str(slugify(t, 30)) for t in data.get("tags", [])[:5])  # entre comillas: "2027" es texto
    fm = (
        "---\n"
        f"title: {yaml_str(data['title'][:110])}\n"
        f"description: {yaml_str(data['description'][:170])}\n"
        f"date: {now}\n"
        f"category: {data['category']}\n"
        f"tags: [{tags}]\n"
        f"pendiente: {'true' if data.get('pendiente') else 'false'}\n"
        f"{img_lines}"
        f"sources:\n{src_yaml}"
        "---\n\n"
    )
    path.write_text(fm + data["body"].strip() + "\n", encoding="utf-8")
    return path


# ---------- main ----------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="solo listar candidatos, sin IA ni escritura")
    ap.add_argument("--url", default="", help="redactar solo esta noticia (enlace)")
    args = ap.parse_args()

    cfg = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    state = load_state()
    posts = existing_posts()
    # también los borradores de ejecuciones anteriores que aún esperan aprobación (no están publicados)
    vistos_urls = {x["url"] for x in posts}
    for e in reversed(state.get("escritos", [])):
        if e["url"] not in vistos_urls:
            posts.insert(0, e)

    print("Buscando novedades…")
    url_forzada = (args.url or os.environ.get("RADAR_URL", "")).strip()
    if url_forzada:
        print(f"Noticia indicada a mano: {url_forzada}")
        html_tmp, _ = fetch_page(url_forzada)
        t = re.search(r"<title[^>]*>(.*?)</title>", html_tmp or "", re.I | re.S)
        oficial = any(d in _domain(url_forzada) for d in ("boe.es", "seg-social.es", "sepe.es", "agenciatributaria.", "gob.es"))
        candidates = [{"source": _domain(url_forzada) or "fuente", "url": url_forzada, "oficial": oficial,
                       "title": re.sub(r"\s+", " ", t.group(1)).strip() if t else url_forzada}]
    else:
        candidates = collect_candidates(cfg, state, posts)
    print(f"{len(candidates)} candidatas nuevas")
    if os.environ.get("GITHUB_ACTIONS"):
        # resumen visible en la página de la ejecución (anotaciones de GitHub)
        print(f"::notice title=Fuentes::{' · '.join(RESUMEN) or 'noticia indicada a mano'}")
        print(f"::notice title=Candidatas ({len(candidates)})::" + " | ".join(f"[{c['source']}] {c['title'][:80]}" for c in candidates[:12]))
    if args.dry_run:
        for c in candidates:
            print(f"  - [{c['source']}] {c['title']}\n    {c['url']}")
        return 0
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_IDENTITY_TOKEN_FILE")):
        print("Faltan credenciales: ANTHROPIC_API_KEY o la federación de identidades (ANTHROPIC_IDENTITY_TOKEN_FILE)")
        return 1

    written, errors, intentos = [], 0, 0
    for item in candidates:
        # cada candidata cuesta una consulta a la IA aunque se descarte: tope para no gastar de más
        if len(written) >= MAX_PER_RUN or intentos >= MAX_PER_RUN * 4:
            break
        print(f"→ [{item['source']}] {item['title']}")
        state["urls"].append(item["url"])
        state["titles"].append(norm_title(item["title"]))
        html, text = fetch_page(item["url"])
        if len(text) < MIN_SOURCE_CHARS:
            print("  – texto insuficiente, se omite")
            continue
        intentos += 1
        try:
            data = write_article(item, text, official_links(html), posts)
        except Exception as e:  # noqa: BLE001
            print(f"  ! error al redactar: {type(e).__name__}: {str(e)[:200]}")
            state["urls"].remove(item["url"])
            state["titles"].pop()
            errors += 1
            if errors >= 2:
                print("  ! dos errores seguidos, se detiene esta ejecución")
                break
            continue
        if data:
            p = save_post(data, item)
            written.append(p)
            nuevo = {"title": data["title"], "url": f"/{data['category']}/{p.stem}/", "guia": False}
            posts.insert(0, nuevo)
            # se recuerda en la memoria del robot, que se guarda en main, para que la próxima ejecución lo vea
            # aunque el borrador aún no se haya aprobado
            state.setdefault("escritos", []).append(nuevo)
            state["escritos"] = state["escritos"][-80:]
            print(f"  ✓ {p.relative_to(ROOT)}")

    save_state(state)
    print(f"\nArtículos nuevos: {len(written)}\n" + "\n".join(f"- {p.stem}" for p in written))
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"count={len(written)}\n")
            fh.write("titulos=" + " | ".join(p.stem for p in written) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
