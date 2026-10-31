import fs from 'node:fs';

export interface Resumen { media: number; min: number; max: number; n: number }
export interface Gasolinera { p: number; rotulo: string; direccion: string; localidad: string; cp: string }
export interface Provincia {
  nombre: string; slug: string;
  g95?: Resumen; diesel?: Resumen;
  baratas_g95?: Gasolinera[]; baratas_diesel?: Gasolinera[];
}
export interface DatosCarburantes {
  fecha: string; fecha_fuente: string; actualizado: string; fuente: string; gasolineras: number;
  nacional: { g95?: Resumen; diesel?: Resumen };
  provincias: Provincia[];
  historico: Record<string, { g95?: number; diesel?: number }>;
}

/** Datos guardados por scripts/carburantes.py (null si aún no se han descargado). */
export function datosCarburantes(): DatosCarburantes | null {
  try { return JSON.parse(fs.readFileSync('src/data/carburantes.json', 'utf8')); } catch { return null; }
}

export const litro = (p?: number) => (p == null ? '—' : p.toLocaleString('es-ES', { minimumFractionDigits: 3, maximumFractionDigits: 3 }));

/** Precio medio de hace `dias` días en el histórico (o el más cercano anterior), para comparar. */
export function hace(d: DatosCarburantes, dias: number, k: 'g95' | 'diesel'): number | undefined {
  const objetivo = new Date(`${d.fecha}T12:00:00Z`).getTime() - dias * 864e5;
  const fechas = Object.keys(d.historico).filter((f) => new Date(`${f}T12:00:00Z`).getTime() <= objetivo).sort();
  return fechas.length ? d.historico[fechas[fechas.length - 1]][k] : undefined;
}

export interface Ciudad extends Provincia { provincia: string; provincia_slug: string }

// Las páginas de municipio solo se ofrecen a Google si tienen datos de sobra: capitales de provincia y municipios con
// al menos 20 gasolineras. El resto siguen en la web (enlazadas desde su provincia) pero con noindex, para que Google y
// AdSense no juzguen el sitio por cientos de páginas casi iguales. Mantener igual que en astro.config.mjs.
export const MIN_GASOLINERAS_INDEXAR = 20;
export const CAPITALES = ['bilbao', 'vitoria-gasteiz', 'donostia', 'pamplona', 'logrono', 'santander', 'oviedo', 'leon', 'palencia',
  'burgos', 'soria', 'segovia', 'avila', 'zamora', 'salamanca', 'valladolid', 'lugo', 'ourense', 'pontevedra',
  'a-coruna', 'huesca', 'teruel', 'zaragoza', 'lleida', 'girona', 'tarragona', 'barcelona', 'castellon',
  'valencia', 'alicante', 'murcia', 'albacete', 'cuenca', 'guadalajara', 'toledo', 'ciudad-real', 'caceres',
  'badajoz', 'huelva', 'sevilla', 'cadiz', 'malaga', 'cordoba', 'jaen', 'granada', 'almeria', 'madrid',
  'palma', 'las-palmas-de-gran-canaria', 'santa-cruz-de-tenerife', 'ceuta', 'melilla'];
export const esCapital = (slug: string) => CAPITALES.includes(slug) || /^(donostia|castellon|palma-de-mallorca)/.test(slug);
export const ciudadIndexable = (c: { slug: string; g95?: { n?: number } | null }) => esCapital(c.slug) || (c.g95?.n ?? 0) >= MIN_GASOLINERAS_INDEXAR;

/** Municipios con página propia (scripts/carburantes.py → carburantes-ciudades.json). */
export function datosCiudades(): Ciudad[] {
  try { return JSON.parse(fs.readFileSync('src/data/carburantes-ciudades.json', 'utf8')).ciudades ?? []; } catch { return []; }
}

/** Media de un municipio hace unos 7 días (la más antigua entre 6 y 9 días atrás), o null si aún no hay datos. */
export function ciudadHaceUnaSemana(clave: string, k: 'g95' | 'diesel'): number | null {
  let hist: Record<string, Record<string, (number | null)[]>> = {};
  try { hist = JSON.parse(fs.readFileSync('src/data/carburantes-ciudades.json', 'utf8')).historico ?? {}; } catch { return null; }
  const fechas = Object.keys(hist).sort();
  const hoy = fechas[fechas.length - 1];
  if (!hoy) return null;
  const dias = (f: string) => (Date.parse(hoy) - Date.parse(f)) / 86400000;
  const f = fechas.find((x) => dias(x) >= 6 && dias(x) <= 9);
  const v = f ? hist[f][clave]?.[k === 'g95' ? 0 : 1] : null;
  return v ?? null;
}
