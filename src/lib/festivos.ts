import type { Festivo } from '../data/festivos-2027';

const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
const d = (f: string) => new Date(`${f}T12:00:00Z`);
export const diaSemana = (f: string) => DIAS[d(f).getUTCDay()];
export const fechaCorta = (f: string) => `${d(f).getUTCDate()} de ${MESES[d(f).getUTCMonth()]}`;
export const mes = (f: string) => MESES[d(f).getUTCMonth()];

const masDias = (f: string, n: number) => new Date(d(f).getTime() + n * 864e5).toISOString().slice(0, 10);

/** Qué supone cada festivo según el día de la semana y los festivos de al lado (`todas`: fechas festivas de esa comunidad). */
export function efecto(f: string, todas: string[] = []): { tipo: 'puente' | 'largo' | 'finde' | 'normal'; texto: string } {
  const w = d(f).getUTCDay();
  const es = (n: number) => todas.includes(masDias(f, n));
  if (w === 0 || w === 6) return { tipo: 'finde', texto: 'Cae en fin de semana' };
  if (w === 4 && es(1)) return { tipo: 'largo', texto: 'Cuatro días seguidos, con el viernes' };
  if (w === 5 && es(-1)) return { tipo: 'largo', texto: 'Cuatro días seguidos, con el jueves' };
  if (w === 2 && es(-1)) return { tipo: 'largo', texto: 'Cuatro días seguidos, con el lunes' };
  if (w === 1 && es(1)) return { tipo: 'largo', texto: 'Cuatro días seguidos, con el martes' };
  if (w === 1 || w === 5) return { tipo: 'largo', texto: 'Fin de semana largo' };
  if (w === 3 && es(-2)) return { tipo: 'puente', texto: 'Puente si libras el martes: cinco días' };
  if (w === 3 && es(2)) return { tipo: 'puente', texto: 'Puente si libras el jueves: cinco días' };
  if (w === 2) return { tipo: 'puente', texto: 'Puente si libras el lunes' };
  if (w === 4) return { tipo: 'puente', texto: 'Puente si libras el viernes' };
  return { tipo: 'normal', texto: 'Entre semana' };
}

/** Cuenta fines de semana largos (bloques de días festivos pegados a un fin de semana) y puentes posibles. */
export function resumen(lista: Festivo[]) {
  const fechas = lista.map((f) => f.fecha);
  const efectos = lista.map((f) => ({ f: f.fecha, e: efecto(f.fecha, fechas) }));
  // Un bloque de festivos seguidos que toca un fin de semana cuenta como un solo fin de semana largo
  const largos = new Set(efectos.filter((x) => x.e.tipo === 'largo').map((x) => {
    const w = d(x.f).getUTCDay();
    return w >= 4 ? masDias(x.f, 6 - w) : masDias(x.f, -w - 1); // sábado del fin de semana que toca
  }));
  return {
    total: lista.length,
    laborables: efectos.filter((x) => x.e.tipo !== 'finde').length,
    largos: largos.size,
    puentes: efectos.filter((x) => x.e.tipo === 'puente').length,
    finde: efectos.filter((x) => x.e.tipo === 'finde').length,
  };
}
