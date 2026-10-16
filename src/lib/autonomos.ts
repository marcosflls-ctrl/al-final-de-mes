/**
 * Cotización de los autónomos en 2026 (sistema por ingresos reales).
 * Tablas de 2025 prorrogadas para 2026 por el Real Decreto-ley 3/2026 (convalidado el 26/02/2026),
 * con la base máxima de los dos últimos tramos actualizada a 5.101,20 €. Tipo total: 31,5 % (incluye MEI 0,9 %).
 */
export const TIPO_AUTONOMOS_2026 = 0.315;

export interface Tramo { tabla: 'reducida' | 'general'; n: number; hasta: number; baseMin: number; baseMax: number }

export const TRAMOS_2026: Tramo[] = [
  { tabla: 'reducida', n: 1, hasta: 670, baseMin: 653.59, baseMax: 718.94 },
  { tabla: 'reducida', n: 2, hasta: 900, baseMin: 718.95, baseMax: 900 },
  { tabla: 'reducida', n: 3, hasta: 1166.69, baseMin: 849.67, baseMax: 1166.7 },
  { tabla: 'general', n: 1, hasta: 1300, baseMin: 950.98, baseMax: 1300 },
  { tabla: 'general', n: 2, hasta: 1500, baseMin: 960.78, baseMax: 1500 },
  { tabla: 'general', n: 3, hasta: 1700, baseMin: 960.78, baseMax: 1700 },
  { tabla: 'general', n: 4, hasta: 1850, baseMin: 1143.79, baseMax: 1850 },
  { tabla: 'general', n: 5, hasta: 2030, baseMin: 1209.15, baseMax: 2030 },
  { tabla: 'general', n: 6, hasta: 2330, baseMin: 1274.51, baseMax: 2330 },
  { tabla: 'general', n: 7, hasta: 2760, baseMin: 1356.21, baseMax: 2760 },
  { tabla: 'general', n: 8, hasta: 3190, baseMin: 1437.91, baseMax: 3190 },
  { tabla: 'general', n: 9, hasta: 3620, baseMin: 1519.61, baseMax: 3620 },
  { tabla: 'general', n: 10, hasta: 4050, baseMin: 1601.31, baseMax: 4050 },
  { tabla: 'general', n: 11, hasta: 6000, baseMin: 1732.03, baseMax: 5101.2 },
  { tabla: 'general', n: 12, hasta: Infinity, baseMin: 1928.1, baseMax: 5101.2 },
];

export const cuotaDe = (base: number) => Math.round(base * TIPO_AUTONOMOS_2026 * 100) / 100;

export interface EntradaAutonomo { ingresos: number; gastos: number; societario: boolean }

/** Rendimiento neto mensual computable: (ingresos − gastos, sin la propia cuota) menos el 7 % (3 % societarios), entre 12. */
export function rendimientoMensual(e: EntradaAutonomo): number {
  const neto = Math.max(0, e.ingresos - e.gastos);
  return (neto * (1 - (e.societario ? 0.03 : 0.07))) / 12;
}

export function tramoDe(rendMensual: number): Tramo {
  return TRAMOS_2026.find((t) => rendMensual <= t.hasta) ?? TRAMOS_2026[TRAMOS_2026.length - 1];
}
