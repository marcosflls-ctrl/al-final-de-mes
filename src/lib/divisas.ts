import fs from 'node:fs';

export interface Divisa {
  codigo: string; nombre: string; valor: number;
  anterior: number | null; hace_un_anio: number | null;
}
export interface DatosDivisas {
  fuente: string; actualizado: string; fecha: string;
  fecha_anterior: string; fecha_hace_un_anio: string;
  divisas: Divisa[];
  series: Record<string, Record<string, number>>;
}

/** Datos guardados por scripts/divisas.py (null si aún no se han descargado). */
export function datosDivisas(): DatosDivisas | null {
  try { return JSON.parse(fs.readFileSync('src/data/divisas.json', 'utf8')); } catch { return null; }
}

/** Decimales razonables según el tamaño del número (1,1225 · 177,63 · 20,92). */
export const decimales = (v: number) => (v >= 10 ? 2 : 4);
export const num = (v: number | null | undefined, d?: number) =>
  v == null ? '—' : v.toLocaleString('es-ES', { minimumFractionDigits: d ?? decimales(v), maximumFractionDigits: d ?? decimales(v) });

/** Variación en % entre dos cambios (positivo = el euro vale más). */
export const variacion = (ahora: number, antes: number | null) => (antes ? ((ahora - antes) / antes) * 100 : null);
