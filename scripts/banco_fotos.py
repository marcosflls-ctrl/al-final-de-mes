"""
Banco de fotos con licencia libre (Wikimedia Commons) para las portadas.

Discover muestra mejor las fotos reales que las portadas con texto. Este script:
  buscar   → busca candidatas por tema en Commons y las deja en banco_candidatas/ con sus datos
             (se ejecuta en GitHub, que sí llega a Commons; luego se revisan a mano)
  preparar → convierte las elegidas (lista en scripts/banco_elegidas.json) a portadas 1600x900
             con sus versiones pequeñas y recortes, y escribe scripts/banco.json

Solo se aceptan licencias que permiten el uso comercial: dominio público, CC0, CC BY y CC BY-SA.
Cada foto guarda su autor y licencia, que se muestran bajo la imagen.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "banco_candidatas"
DEST = ROOT / "public" / "img" / "banco"
BANCO = ROOT / "scripts" / "banco.json"
ELEGIDAS = ROOT / "scripts" / "banco_elegidas.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "AlFinalDeMes/1.0 (https://alfinaldemes.com; banco de portadas)"

# tema → (búsquedas en Commons, palabras del titular que lo señalan, secciones)
TEMAS: dict[str, dict] = {
    "contador-luz": {"q": ["electricity meter Spain", "contador eléctrico"], "palabras": ["luz", "factura", "pvpc", "kwh", "eléctric"], "secciones": ["luz"]},
    "bombilla": {"q": ["light bulb lit", "bombilla encendida"], "palabras": ["luz", "factura", "consumo"], "secciones": ["luz"]},
    "torres-electricas": {"q": ["power lines sunset Spain", "high voltage towers Spain"], "palabras": ["luz", "eléctric", "red eléctrica", "apagón", "energía"], "secciones": ["luz"]},
    "placas-solares": {"q": ["solar panels roof Spain", "placas solares tejado"], "palabras": ["solar", "autoconsumo", "placas", "renovable"], "secciones": ["luz", "vivienda"]},
    "radiador": {"q": ["electric radiator heater", "radiador"], "palabras": ["calefacción", "frío", "invierno", "radiador", "gas"], "secciones": ["luz"]},
    "gasolinera": {"q": ["petrol station Spain", "gasolinera España"], "palabras": ["gasolina", "diésel", "carburante", "gasolinera", "combustible"], "secciones": ["luz"]},
    "surtidor": {"q": ["fuel pump nozzle", "surtidor gasolina"], "palabras": ["gasolina", "diésel", "carburante", "repostar", "litro"], "secciones": ["luz"]},
    "bombona-butano": {"q": ["butane gas cylinder Spain", "bombona butano"], "palabras": ["butano", "bombona"], "secciones": ["luz"]},
    "coche-electrico": {"q": ["electric car charging station", "punto de recarga coche eléctrico"], "palabras": ["coche eléctrico", "recarga", "moves"], "secciones": ["luz", "hacienda"]},
    "billetes-euro": {"q": ["euro banknotes", "billetes de euro"], "palabras": ["euros", "ayuda", "pago", "cobro", "dinero", "smi", "salario mínimo", "paga extra"], "secciones": ["hacienda", "pensiones", "paro"]},
    "monedas-euro": {"q": ["euro coins", "monedas de euro"], "palabras": ["ahorro", "precio", "subida", "ipc"], "secciones": ["hacienda", "pensiones"]},
    "calculadora": {"q": ["calculator documents desk", "calculadora facturas"], "palabras": ["renta", "declaración", "irpf", "impuesto", "deducción", "cuota"], "secciones": ["hacienda", "paro"]},
    "agencia-tributaria": {"q": ["Agencia Tributaria building", "Agencia Tributaria sede Madrid"], "palabras": ["hacienda", "agencia tributaria", "aeat", "renta"], "secciones": ["hacienda"]},
    "ministerio-hacienda": {"q": ["Ministerio de Hacienda Madrid Alcalá", "Real Casa de la Aduana Madrid"], "palabras": ["hacienda", "ministerio", "presupuestos"], "secciones": ["hacienda"]},
    "congreso": {"q": ["Congreso de los Diputados fachada", "Palacio de las Cortes Madrid"], "palabras": ["congreso", "convalida", "decreto", "ley", "partido", "elecciones", "votación"], "secciones": ["hacienda", "vivienda", "pensiones", "paro", "luz"]},
    "moncloa": {"q": ["Palacio de la Moncloa"], "palabras": ["gobierno", "consejo de ministros", "moncloa"], "secciones": ["hacienda", "vivienda", "pensiones", "paro", "luz"]},
    "banco-de-espana": {"q": ["Banco de España edificio Madrid"], "palabras": ["banco de españa", "euríbor", "hipoteca", "tipos"], "secciones": ["vivienda", "hacienda"]},
    "seguridad-social": {"q": ["Seguridad Social oficina", "Instituto Nacional de la Seguridad Social"], "palabras": ["seguridad social", "inss", "pensión", "cotiza", "jubila", "empleadas del hogar", "baja por"], "secciones": ["pensiones", "paro"]},
    "pensionistas": {"q": ["elderly people park bench Spain", "jubilados paseo"], "palabras": ["pensión", "pensiones", "jubila", "mayores", "pensionistas"], "secciones": ["pensiones"]},
    "oficina-empleo": {"q": ["oficina de empleo SEPE", "Servicio Público de Empleo Estatal"], "palabras": ["paro", "sepe", "desempleo", "subsidio", "empleo"], "secciones": ["paro"]},
    "trabajo-oficina": {"q": ["office workers desks", "oficina trabajadores"], "palabras": ["trabajador", "jornada", "salario", "nómina", "convenio", "sueldo"], "secciones": ["paro"]},
    "obra-construccion": {"q": ["construction workers building site Spain", "obra construcción edificio"], "palabras": ["obra", "construcción", "autónomo"], "secciones": ["paro", "vivienda"]},
    "edificio-viviendas": {"q": ["apartment buildings Madrid", "bloque de viviendas España"], "palabras": ["vivienda", "pisos", "edificio", "inmobiliari"], "secciones": ["vivienda"]},
    "fachada-balcones": {"q": ["balconies facade Barcelona", "fachada balcones Valencia"], "palabras": ["alquiler", "inquilino", "casero", "piso", "propietario"], "secciones": ["vivienda"]},
    "se-alquila": {"q": ["se alquila cartel", "for rent sign Spain"], "palabras": ["alquiler", "alquila", "arrendamiento", "inquilino"], "secciones": ["vivienda"]},
    "llaves-casa": {"q": ["house keys", "llaves de casa"], "palabras": ["hipoteca", "compra", "vivienda", "comprar"], "secciones": ["vivienda"]},
    "gruas": {"q": ["construction cranes city skyline Spain", "grúas construcción"], "palabras": ["obra nueva", "construcción", "promoción", "suelo"], "secciones": ["vivienda"]},
    "supermercado": {"q": ["supermarket aisle", "supermercado pasillo"], "palabras": ["supermercado", "precios", "ipc", "cesta", "alimentos", "compra"], "secciones": ["hacienda"]},
    "carro-compra": {"q": ["shopping cart supermarket", "carro de la compra"], "palabras": ["compra", "cesta", "iva", "alimentos"], "secciones": ["hacienda"]},
    "mercado-fruta": {"q": ["fruit market stall Spain", "mercado frutería"], "palabras": ["fruta", "verdura", "alimentos", "aceite"], "secciones": ["hacienda"]},
    "aceite-oliva": {"q": ["olive oil bottles", "aceite de oliva"], "palabras": ["aceite"], "secciones": ["hacienda"]},
    "loteria": {"q": ["Lotería de Navidad décimo", "Doña Manolita lotería"], "palabras": ["lotería", "décimo", "sorteo", "gordo"], "secciones": ["hacienda"]},
    "reloj": {"q": ["clock face", "reloj de pared"], "palabras": ["cambio de hora", "horario", "hora"], "secciones": ["luz"]},
    "calendario": {"q": ["calendar planner", "calendario pared"], "palabras": ["calendario", "festivo", "plazo", "fechas"], "secciones": ["paro", "hacienda"]},
    "cajero": {"q": ["ATM cash machine Spain", "cajero automático"], "palabras": ["banco", "cobro", "ingreso", "cajero", "paga"], "secciones": ["pensiones", "paro"]},
}
LICENCIAS_OK = re.compile(r"^(cc0|public domain|pd|cc[ -]by(-sa)?[ -]?[234](\.\d)?( [a-z]+)?)$", re.I)


def limpiar(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def buscar() -> None:
    CAND.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    datos = []
    for tema, cfg in TEMAS.items():
        vistos, n = set(), 0
        for q in cfg["q"]:
            params = {
                "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": 30,
                "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1600,
            }
            try:
                r = s.get(API, params=params, timeout=60)
                pages = (r.json().get("query") or {}).get("pages", {})
            except Exception as e:  # noqa: BLE001
                print(f"! {tema} {q}: {e}")
                continue
            for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
                ii = (p.get("imageinfo") or [{}])[0]
                titulo = p.get("title", "")
                if titulo in vistos or ii.get("mime") != "image/jpeg":
                    continue
                w, h = ii.get("width", 0), ii.get("height", 0)
                if w < 1600 or not (1.25 <= w / max(h, 1) <= 2.1):
                    continue
                meta = ii.get("extmetadata", {})
                lic = limpiar(meta.get("LicenseShortName", {}).get("value", ""))
                if not LICENCIAS_OK.match(lic):
                    continue
                vistos.add(titulo)
                n += 1
                nombre = f"{tema}-{n:02d}.jpg"
                try:
                    img = s.get(ii["thumburl"], timeout=60).content
                    Image.open(io.BytesIO(img)).convert("RGB").save(CAND / nombre, "JPEG", quality=82)
                except Exception as e:  # noqa: BLE001
                    print(f"! descarga {titulo}: {e}")
                    continue
                datos.append({
                    "archivo": nombre, "tema": tema, "titulo": titulo,
                    "pagina": ii.get("descriptionurl", ""),
                    "autor": limpiar(meta.get("Artist", {}).get("value", ""))[:120],
                    "licencia": lic, "licencia_url": meta.get("LicenseUrl", {}).get("value", ""),
                    "descripcion": limpiar(meta.get("ImageDescription", {}).get("value", ""))[:200],
                })
                time.sleep(0.3)
                if n >= 8:
                    break
            if n >= 8:
                break
        print(f"{tema}: {n} candidatas")
    (CAND / "candidatas.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Total: {len(datos)}")


def preparar() -> None:
    """Pasa las elegidas a public/img/banco/ en 1600x900 y escribe scripts/banco.json."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from miniaturas import make_variants, make_crops

    cand = {c["archivo"]: c for c in json.loads((CAND / "candidatas.json").read_text(encoding="utf-8"))}
    elegidas = json.loads(ELEGIDAS.read_text(encoding="utf-8"))
    DEST.mkdir(parents=True, exist_ok=True)
    banco = []
    for e in elegidas:
        c = cand[e["archivo"]]
        slug = Path(e["archivo"]).stem
        with Image.open(CAND / e["archivo"]) as im:
            im = im.convert("RGB")
            escala = max(1600 / im.width, 900 / im.height)
            im = im.resize((round(im.width * escala), round(im.height * escala)), Image.LANCZOS)
            x, y = (im.width - 1600) // 2, round((im.height - 900) * e.get("y", 0.5))
            salida = DEST / f"{slug}.webp"
            im.crop((x, y, x + 1600, y + 900)).save(salida, "WEBP", quality=70, method=6)
        make_variants(salida)
        make_crops(salida)
        tema = TEMAS[c["tema"]]
        banco.append({
            "slug": slug, "tema": c["tema"], "alt": e["alt"],
            "palabras": tema["palabras"], "secciones": tema["secciones"],
            "credito": f"{e.get('autor') or c['autor'] or 'Autor desconocido'} / Wikimedia Commons ({c['licencia']})",
            "pagina": c["pagina"],
        })
    BANCO.write_text(json.dumps({"imagenes": banco}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(banco)} fotos en el banco")


if __name__ == "__main__":
    {"buscar": buscar, "preparar": preparar}[sys.argv[1]]()
