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

/** Municipios con página propia (scripts/carburantes.py → carburantes-ciudades.json). */
export function datosCiudades(): Ciudad[] {
  try { return JSON.parse(fs.readFileSync('src/data/carburantes-ciudades.json', 'utf8')).ciudades ?? []; } catch { return []; }
}
