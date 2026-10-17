/**
 * Estimación de la pensión de jubilación contributiva (Régimen General) con las reglas de 2026 y 2027 en adelante.
 *
 * Fuentes:
 * - Edad ordinaria y porcentaje por años cotizados: LGSS arts. 205 y 210 y disposiciones transitorias 7.ª y 9.ª.
 * - Coeficientes de la jubilación anticipada voluntaria: LGSS art. 208.2 (Ley 21/2021).
 * - Jubilación demorada: 4 % por cada año completo (LGSS art. 210.2).
 * - Pensión máxima y mínimas de 2026: real decreto de revalorización de las pensiones para 2026 (BOE del 24/12/2025).
 * - Complemento de brecha de género 2026: 36,90 € al mes por hijo, hasta cuatro.
 *
 * Simplificación principal: la base reguladora se calcula como si el sueldo, en euros de hoy, fuera el mismo
 * durante los años que se tienen en cuenta (25 años, o 25 años y 2 meses con el sistema nuevo, que da casi lo mismo).
 * Con un sueldo constante, la base reguladora es el sueldo bruto anual (limitado a la base máxima) entre 14.
 */
import { calcular as calcularSueldo, PARAMETROS_2026 } from './sueldo';

export const PENSION_2026 = {
  maxima: 3359.6, // al mes, en 14 pagas
  baseMaximaMensual: 5101.2,
  brechaPorHijo: 36.9,
  // Pensiones mínimas de jubilación (al mes, 14 pagas)
  minimas: {
    '65+': { conyugeACargo: 1256.6, sinConyuge: 936.2, conyugeNoACargo: 888.7 },
    '<65': { conyugeACargo: 1256.6, sinConyuge: 875.9, conyugeNoACargo: 827.9 },
  },
};

export type Familia = 'conyugeACargo' | 'sinConyuge' | 'conyugeNoACargo';

/** Coeficientes reductores de la jubilación anticipada voluntaria (art. 208.2 LGSS), en %, de 24 a 1 mes de adelanto. */
const COEF_VOLUNTARIA: number[][] = [
  // [<38a6m, <41a6m, <44a6m, ≥44a6m]
  [21, 19, 17, 13], [17.6, 16.5, 15, 12], [14.67, 14, 13.33, 11], [12.57, 12, 11.43, 10], [11, 10.5, 10, 9.2],
  [9.78, 9.33, 8.89, 8.4], [8.8, 8.4, 8, 7.6], [8, 7.64, 7.27, 6.91], [7.33, 7, 6.67, 6.33], [6.77, 6.46, 6.15, 5.85],
  [6.29, 6, 5.71, 5.43], [5.87, 5.6, 5.33, 5.07], [5.5, 5.25, 5, 4.75], [5.18, 4.94, 4.71, 4.47], [4.89, 4.67, 4.44, 4.22],
  [4.63, 4.42, 4.21, 4], [4.4, 4.2, 4, 3.8], [4.19, 4, 3.81, 3.62], [4, 3.82, 3.64, 3.45], [3.83, 3.65, 3.48, 3.3],
  [3.67, 3.5, 3.33, 3.17], [3.52, 3.36, 3.2, 3.04], [3.38, 3.23, 3.08, 2.92], [3.26, 3.11, 2.96, 2.81],
];

/** % de reducción por jubilarse `meses` antes (1 a 24) con `cotizados` meses cotizados. */
export function coeficienteVoluntaria(meses: number, cotizados: number): number {
  const fila = COEF_VOLUNTARIA[24 - meses];
  const col = cotizados < 462 ? 0 : cotizados < 498 ? 1 : cotizados < 534 ? 2 : 3;
  return fila[col];
}

/** Porcentaje de la base reguladora según los meses cotizados y el año de jubilación. */
export function porcentaje(meses: number, anio: number): number {
  if (meses < 180) return 0;
  const extra = meses - 180;
  let p: number;
  if (anio <= 2026) {
    // 2023-2026: 0,21 % los meses 1 a 49 y 0,19 % los meses 50 a 258 (100 % con 36 años y 6 meses)
    p = 50 + Math.min(extra, 49) * 0.21 + Math.max(0, Math.min(extra, 258) - 49) * 0.19;
  } else {
    // Desde 2027: 0,19 % los meses 1 a 248 y 0,18 % los meses 249 a 264 (100 % con 37 años)
    p = 50 + Math.min(extra, 248) * 0.19 + Math.max(0, Math.min(extra, 264) - 248) * 0.18;
  }
  return Math.min(100, Math.round(p * 100) / 100);
}

/** Índice de mes (año*12 + mes 0-11). */
export const idx = (anio: number, mes: number) => anio * 12 + mes;
export const anioDe = (i: number) => Math.floor(i / 12);
export const mesDe = (i: number) => ((i % 12) + 12) % 12;

export interface Entrada {
  anioNac: number;
  mesNac: number; // 0-11
  cotizadosHoy: number; // meses
  sigueCotizando: boolean;
  sueldoAnual: number; // bruto, en euros de hoy
  ajuste: number; // meses: negativo = anticipada voluntaria (hasta -24), positivo = demorada
  familia: Familia;
  hijos: number; // para el complemento de brecha de género (0-4)
  hoy: number; // índice del mes actual
}

export interface Resultado {
  ok: boolean;
  aviso?: string;
  edadOrdinaria: number; // meses de edad
  fechaOrdinaria: number; // índice de mes
  fecha: number; // índice de mes de la jubilación elegida
  edad: number; // meses de edad al jubilarse
  cotizados: number; // meses cotizados al jubilarse
  baseReguladora: number;
  porcentaje: number;
  teorica: number;
  coeficiente: number; // % de reducción (anticipada) o de aumento (demorada, en positivo)
  limitadaMaxima: boolean;
  complementoMinimos: number;
  brecha: number;
  bruta: number; // al mes, 14 pagas
  tipoIrpf: number;
  neta: number; // al mes
  anual: number;
  reemplazo: number; // pensión neta anual / sueldo neto anual
}

const r2 = (x: number) => Math.round(x * 100) / 100;

/** Edad ordinaria de jubilación (en meses de edad) según la fecha en que se cumple. */
export function edadOrdinaria(e: Pick<Entrada, 'anioNac' | 'mesNac' | 'cotizadosHoy' | 'sigueCotizando' | 'hoy'>): number {
  const nac = idx(e.anioNac, e.mesNac);
  const cotizadoEn = (i: number) => e.cotizadosHoy + (e.sigueCotizando ? Math.max(0, i - e.hoy) : 0);
  const a65 = nac + 65 * 12;
  const umbral = anioDe(a65) <= 2026 ? 38 * 12 + 3 : 38 * 12 + 6;
  if (cotizadoEn(a65) >= umbral) return 65 * 12;
  const a6610 = nac + 66 * 12 + 10;
  if (anioDe(a6610) <= 2026) return 66 * 12 + 10;
  return 67 * 12;
}

function netoMensual(bruta: number, edadMeses: number, familia: Familia) {
  if (bruta <= 0) return { tipo: 0, neta: 0 };
  // Las pensiones no cotizan a la Seguridad Social: se usa el algoritmo de retención de IRPF sin cotizaciones.
  const sinCotizar = {
    ...PARAMETROS_2026,
    ss: { ...PARAMETROS_2026.ss, contingenciasComunes: 0, mei: 0, desempleoIndefinido: 0, desempleoTemporal: 0, formacion: 0, solidaridad: PARAMETROS_2026.ss.solidaridad.map((t) => ({ ...t, tipo: 0 })) },
  };
  const r = calcularSueldo({
    brutoAnual: bruta * 14, pagas: 14, contrato: 'indefinido',
    anioNacimiento: PARAMETROS_2026.ejercicio - Math.floor(edadMeses / 12),
    situacion: familia === 'conyugeACargo' ? 2 : 3, hijos: [], discapacidad: 'no',
  }, sinCotizar);
  return { tipo: r.tipoRetencion, neta: r2(bruta * (1 - r.tipoRetencion / 100)) };
}

export function calcular(e: Entrada): Resultado {
  const P = PENSION_2026;
  const nac = idx(e.anioNac, e.mesNac);
  const edadOrd = edadOrdinaria(e);
  const fechaOrd = nac + edadOrd;
  const fecha = fechaOrd + e.ajuste;
  const edad = edadOrd + e.ajuste;
  const cotizados = e.cotizadosHoy + (e.sigueCotizando ? Math.max(0, fecha - e.hoy) : 0);
  const base = r2(Math.min(e.sueldoAnual, P.baseMaximaMensual * 12) / 14);
  const vacio: Resultado = {
    ok: false, edadOrdinaria: edadOrd, fechaOrdinaria: fechaOrd, fecha, edad, cotizados, baseReguladora: base, porcentaje: 0, teorica: 0,
    coeficiente: 0, limitadaMaxima: false, complementoMinimos: 0, brecha: 0, bruta: 0, tipoIrpf: 0, neta: 0, anual: 0, reemplazo: 0,
  };
  if (cotizados < 180) return { ...vacio, aviso: 'Con menos de 15 años cotizados no hay derecho a pensión contributiva de jubilación. Podrías pedir la no contributiva si tus ingresos son bajos.' };
  if (e.ajuste < 0 && cotizados < 420) return { ...vacio, aviso: 'Para jubilarte antes de tiempo de forma voluntaria necesitas al menos 35 años cotizados al hacerlo.' };

  const pct = porcentaje(cotizados, anioDe(fecha));
  const teorica = r2((base * pct) / 100);
  const tramo = edad < 65 * 12 ? '<65' : '65+';
  let bruta = teorica, coef = 0, limitada = false;

  if (e.ajuste < 0) {
    coef = coeficienteVoluntaria(-e.ajuste, cotizados);
    bruta = r2(teorica * (1 - coef / 100));
    // Requisito: la pensión resultante tiene que superar la mínima que correspondería a los 65 años
    if (bruta < P.minimas['65+'][e.familia]) {
      return { ...vacio, porcentaje: pct, teorica, coeficiente: coef, bruta, aviso: 'No podrías jubilarte antes de tiempo: la pensión resultante sería menor que la pensión mínima, y la ley lo exige.' };
    }
    if (bruta > P.maxima) { bruta = P.maxima; limitada = true; }
  } else if (e.ajuste > 0) {
    coef = 4 * Math.floor(e.ajuste / 12);
    bruta = r2(Math.min(teorica * (1 + coef / 100), P.maxima * (1 + coef / 100)));
    limitada = teorica > P.maxima;
  } else if (bruta > P.maxima) {
    bruta = P.maxima; limitada = true;
  }

  let complemento = 0;
  const minima = P.minimas[tramo][e.familia];
  if (bruta < minima) { complemento = r2(minima - bruta); bruta = minima; }
  const brecha = r2(Math.min(4, Math.max(0, e.hijos)) * P.brechaPorHijo);
  bruta = r2(bruta + brecha);

  const { tipo, neta } = netoMensual(bruta, edad, e.familia);
  const sueldoNeto = e.sueldoAnual > 0 ? calcularSueldo({ brutoAnual: e.sueldoAnual, pagas: 14, contrato: 'indefinido', anioNacimiento: 1980, situacion: e.familia === 'conyugeACargo' ? 2 : 3, hijos: [], discapacidad: 'no' }).netoAnual : 0;
  return {
    ok: true, edadOrdinaria: edadOrd, fechaOrdinaria: fechaOrd, fecha, edad, cotizados, baseReguladora: base, porcentaje: pct, teorica,
    coeficiente: coef, limitadaMaxima: limitada, complementoMinimos: complemento, brecha, bruta, tipoIrpf: tipo, neta,
    anual: r2(bruta * 14), reemplazo: sueldoNeto > 0 ? r2((neta * 14) / sueldoNeto * 100) : 0,
  };
}
