"""
Imagen de portada (1600x900, WebP) con el titular, para artículos sin foto propia.
Discover necesita imágenes grandes: esta es la que se ve en la tarjeta.

Uso desde otro script:  from portada import crear; crear("Titular", "pensiones", Path("public/img/articulos/x.webp"))
Uso directo:            python scripts/portada.py "Titular" pensiones salida.webp
También genera las imágenes fijas de la web:  python scripts/portada.py --fijas
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FUENTES = Path(__file__).resolve().parent / "fuentes"
VERDE, VERDE_2, AMBAR, CREMA = (13, 92, 69), (18, 122, 92), (242, 169, 59), (250, 248, 244)
ETIQUETAS = {"inicio": "AL FINAL DE MES", "luz": "LUZ", "pensiones": "PENSIONES", "paro": "PARO Y AYUDAS", "hacienda": "HACIENDA"}
# Un color de acento por sección, para que las portadas no parezcan todas iguales
ACENTO = {"luz": (242, 169, 59), "pensiones": (125, 196, 160), "paro": (143, 182, 222), "hacienda": (232, 140, 120)}


def fuente(nombre: str, tam: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FUENTES / f"{nombre}.woff"), tam)


def partir(draw: ImageDraw.ImageDraw, texto: str, f: ImageFont.FreeTypeFont, ancho: int) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if draw.textlength(prueba, font=f) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def marca(draw: ImageDraw.ImageDraw, x: int, y: int, s: float) -> None:
    """El icono de la web (hoja de calendario con el último día marcado), en blanco sobre verde."""
    draw.rounded_rectangle([x, y, x + 32 * s, y + 32 * s], radius=8 * s, fill=VERDE_2)
    draw.rounded_rectangle([x + 7 * s, y + 9 * s, x + 25 * s, y + 25 * s], radius=2.5 * s, outline="white", width=round(2 * s))
    draw.line([x + 7 * s, y + 13.5 * s, x + 25 * s, y + 13.5 * s], fill="white", width=round(2 * s))
    for cx in (11.5, 20.5):
        draw.line([x + cx * s, y + 6.5 * s, x + cx * s, y + 10.5 * s], fill="white", width=round(2 * s))
    r = 2.6 * s
    draw.ellipse([x + 20.5 * s - r, y + 20 * s - r, x + 20.5 * s + r, y + 20 * s + r], fill=AMBAR)


def crear(titulo: str, categoria: str, salida: Path, ancho: int = 1600, alto: int = 900, subtitulo: str = "") -> Path:
    escala = ancho / 1600
    img = Image.new("RGB", (ancho, alto), VERDE)
    d = ImageDraw.Draw(img)
    acento = ACENTO.get(categoria, AMBAR)
    # banda lateral de color y círculo decorativo, discretos
    d.ellipse([ancho - 520 * escala, -260 * escala, ancho + 260 * escala, 520 * escala], fill=VERDE_2)
    d.rectangle([0, 0, 18 * escala, alto], fill=acento)
    m = round(96 * escala)
    # etiqueta de la sección
    fe = fuente("inter-600", round(30 * escala))
    etiqueta = ETIQUETAS.get(categoria, categoria.upper())
    tw = d.textlength(etiqueta, font=fe)
    d.rounded_rectangle([m, m, m + tw + 40 * escala, m + 56 * escala], radius=10 * escala, fill=acento)
    d.text((m + 20 * escala, m + 28 * escala), etiqueta, font=fe, fill=VERDE, anchor="lm")
    # titular: el tamaño baja si es largo, para que siempre quepa en 4 líneas
    zona_y0, zona_y1 = m + 100 * escala, alto - 170 * escala
    for tam in (104, 94, 84, 76, 68, 60):
        ft = fuente("serif-700", round(tam * escala))
        lineas = partir(d, titulo, ft, ancho - 2 * m - 60 * escala)
        alto_linea = round(tam * 1.18 * escala)
        if len(lineas) <= 4 and len(lineas) * alto_linea <= zona_y1 - zona_y0:
            break
    y = zona_y0 + ((zona_y1 - zona_y0) - len(lineas) * alto_linea) / 2
    for linea in lineas[:4]:
        d.text((m, y), linea, font=ft, fill="white")
        y += alto_linea
    if subtitulo:
        fs = fuente("inter-400", round(34 * escala))
        d.text((m, y + 10 * escala), subtitulo, font=fs, fill=(214, 233, 224))
    # pie: marca y dominio
    marca(d, m, round(alto - m - 52 * escala), 1.65 * escala)
    fm = fuente("inter-600", round(32 * escala))
    d.text((m + 72 * escala, alto - m - 26 * escala), "alfinaldemes.com", font=fm, fill=CREMA, anchor="lm")
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.suffix == ".png":
        img.save(salida, "PNG", optimize=True)
    else:
        img.save(salida, "WEBP", quality=84, method=6)
    return salida


def icono(tam: int, salida: Path) -> None:
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = tam / 32
    d.rounded_rectangle([0, 0, tam - 1, tam - 1], radius=8 * s, fill=VERDE)
    d.rounded_rectangle([7 * s, 9 * s, 25 * s, 25 * s], radius=2.5 * s, outline="white", width=max(1, round(2 * s)))
    d.line([7 * s, 13.5 * s, 25 * s, 13.5 * s], fill="white", width=max(1, round(2 * s)))
    for cx in (11.5, 20.5):
        d.line([cx * s, 6.5 * s, cx * s, 10.5 * s], fill="white", width=max(1, round(2 * s)))
    r = 2.6 * s
    d.ellipse([20.5 * s - r, 20 * s - r, 20.5 * s + r, 20 * s + r], fill=AMBAR)
    img.save(salida, "PNG", optimize=True)


def fijas() -> None:
    """Portadas de cada sección, imagen por defecto para redes e iconos."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from miniaturas import make_variants

    textos = {
        "luz": ("Precio de la luz hoy y mañana por horas", "Las horas más baratas, cada día"),
        "pensiones": ("Pensiones: subidas, pagas y fechas de cobro", "Con los datos de la Seguridad Social"),
        "paro": ("Paro, subsidios y ayudas: requisitos y cuantías", "Con los datos del SEPE"),
        "hacienda": ("Renta, IRPF y avisos de Hacienda", "Con los datos de la Agencia Tributaria"),
    }
    for cat, (t, sub) in textos.items():
        p = crear(t, cat, ROOT / "public" / "img" / "portadas" / f"{cat}.webp", subtitulo=sub)
        make_variants(p)
    crear("Lo que afecta a tu bolsillo, explicado claro", "inicio", ROOT / "public" / "og-default.png", 1200, 630,
          subtitulo="Pensiones, paro, Hacienda y luz")
    for tam, nombre in ((48, "favicon-48.png"), (180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")):
        icono(tam, ROOT / "public" / nombre)
    print("Imágenes fijas creadas")


if __name__ == "__main__":
    if sys.argv[1:] == ["--fijas"]:
        fijas()
    elif len(sys.argv) == 4:
        print(crear(sys.argv[1], sys.argv[2], Path(sys.argv[3])))
    else:
        print(__doc__)
