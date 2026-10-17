/**
 * Prestación contributiva por desempleo («el paro») en 2026, jornada completa.
 *
 * - Duración: artículo 269.1 de la Ley General de la Seguridad Social (LGSS).
 * - Cuantía: artículo 270 LGSS. 70 % de la base reguladora los primeros 180 días y 60 % desde el día 181
 *   (redacción de la Ley 31/2022, en vigor desde 2023). Topes en función del IPREM incrementado en 1/6.
 * - IPREM 2026: 600 € al mes (sin cambios desde 2023, al no haber nuevos Presupuestos).
 * - Descuento del trabajador: 4,70 % de contingencias comunes + 0,15 % de MEI en 2026, sobre la base reguladora.
 *
 * Si cambia la normativa, solo hay que tocar las constantes de este archivo.
 */

export const PARO_2026 = {
  ejercicio: 2026,
  ipremMensual: 600,
  baseMaximaMensual: 5101.2, // base máxima de cotización 2026
  porcentajes: { primeros180: 0.7, despues: 0.6 },
  // topes sobre el IPREM con pagas extra (IPREM × 7/6)
  topeMaximo: { 0: 1.75, 1: 2.0, 2: 2.25 } as Record<0 | 1 | 2, number>,
  topeMinimo: { 0: 0.8, 1: 1.07, 2: 1.07 } as Record<0 | 1 | 2, number>,
  descuentoTrabajador: 0.047 + 0.0015,
  // [días cotizados en los últimos 6 años desde, días de prestación]
  duracion: [
    [360, 120], [540, 180], [720, 240], [900, 300], [1080, 360], [1260, 420],
    [1440, 480], [1620, 540], [1800, 600], [1980, 660], [2160, 720],
  ] as [number, number][],
};

export type Hijos = 0 | 1 | 2; // 2 = dos o más

export interface Entrada {
  /** sueldo bruto anual, con las pagas extra */
  brutoAnual: number;
  /** días cotizados en los últimos 6 años */
  diasCotizados: number;
  hijos: Hijos;
}

export interface Resultado {
  derecho: boolean;
  diasPrestacion: number;
  meses: number;
  baseMensual: number;
  topeMax: number;
  topeMin: number;
  brutoInicio: number; // al mes, primeros 6 meses
  brutoDespues: number; // al mes, desde el 7.º mes (0 si dura 4 meses)
  descuento: number; // al mes
  netoInicio: number;
  netoDespues: number;
  totalBruto: number;
  topado: 'max' | 'min' | null;
}

const r2 = (n: number) => Math.round(n * 100) / 100;

export function diasDePrestacion(diasCotizados: number, p = PARO_2026) {
  let dias = 0;
  for (const [desde, d] of p.duracion) if (diasCotizados >= desde) dias = d;
  return dias;
}

export function calcularParo(e: Entrada, p = PARO_2026): Resultado {
  const dias = diasDePrestacion(e.diasCotizados, p);
  const iprem = (p.ipremMensual * 7) / 6;
  const topeMax = r2(iprem * p.topeMaximo[e.hijos]);
  const topeMin = r2(iprem * p.topeMinimo[e.hijos]);
  const baseMensual = r2(Math.min(Math.max(0, e.brutoAnual) / 12, p.baseMaximaMensual));
  const acotar = (x: number) => Math.min(Math.max(x, topeMin), topeMax);
  const brutoInicio = r2(acotar(baseMensual * p.porcentajes.primeros180));
  const brutoDespues = dias > 180 ? r2(acotar(baseMensual * p.porcentajes.despues)) : 0;
  const descuento = r2(baseMensual * p.descuentoTrabajador);
  const meses = dias / 30;
  const mesesInicio = Math.min(meses, 6);
  const totalBruto = r2(brutoInicio * mesesInicio + brutoDespues * Math.max(0, meses - 6));
  const sinTope = baseMensual * p.porcentajes.primeros180;
  return {
    derecho: dias > 0,
    diasPrestacion: dias,
    meses,
    baseMensual,
    topeMax,
    topeMin,
    brutoInicio,
    brutoDespues,
    descuento,
    netoInicio: r2(Math.max(0, brutoInicio - descuento)),
    netoDespues: dias > 180 ? r2(Math.max(0, brutoDespues - descuento)) : 0,
    totalBruto,
    topado: sinTope > topeMax ? 'max' : sinTope < topeMin ? 'min' : null,
  };
}
