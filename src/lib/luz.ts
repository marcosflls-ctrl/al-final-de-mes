import fs from 'node:fs';

export interface Hora { h: string; p: number }
export interface DatosLuz { hoy: string; actualizado?: string; fuente: string; dias: Record<string, Hora[]> }

/** Datos de la luz guardados por scripts/luz.py (null si aún no se han descargado). */
export function datosLuz(): DatosLuz | null {
  try { return JSON.parse(fs.readFileSync('src/data/luz.json', 'utf8')); } catch { return null; }
}

/** Fecha de hoy y de mañana en España (AAAA-MM-DD), según el momento en que se construye la web. */
export function hoyManana(): [string, string] {
  const f = (d: Date) => d.toLocaleDateString('sv-SE', { timeZone: 'Europe/Madrid' });
  const ahora = new Date();
  return [f(ahora), f(new Date(ahora.getTime() + 864e5))];
}

/** "martes 13 de octubre" */
export function fechaLarga(iso: string) {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'Europe/Madrid' });
}
