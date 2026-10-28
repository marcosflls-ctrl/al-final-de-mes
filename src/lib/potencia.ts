/**
 * Coste de la potencia contratada de la luz en 2026 (peaje 2.0TD, hogares hasta 15 kW).
 *
 * - Peajes de transporte y distribución: Resolución de la CNMC de 18 de diciembre de 2025 (BOE-A-2025-26348).
 * - Cargos del sistema: Orden TED/1524/2025, de 23 de diciembre.
 * - Margen de comercialización del PVPC: 3,113 €/kW y año.
 * - Impuesto especial sobre la electricidad (5,11269632 %) e IVA (21 %): los generales. Si se activa la rebaja
 *   automática (IVA al 10 % e impuesto al 0,5 %), cambiar IMPUESTOS.
 * Si cambian los precios en enero, solo hay que tocar estas constantes.
 */
export const POTENCIA_2026 = {
  peajesP1: 23.324952, peajesP2: 0.44377,      // €/kW y año
  cargosP1: 4.379461, cargosP2: 0.281653,      // €/kW y año
  margenPVPC: 3.113,                           // €/kW y año
};
export const IMPUESTOS = { electricidad: 0.0511269632, iva: 0.21 };
// Potencias habituales (monofásica a 230 V)
export const POTENCIAS_NORMALIZADAS = [2.3, 3.45, 4.6, 5.75, 6.9, 8.05, 9.2];
export const ENGANCHE = 9.04; // derechos de enganche al cambiar la potencia, sin IVA

/** Coste de 1 kW contratado (en punta y en valle) durante un año en el PVPC, con impuestos. */
export function costeKwAnio(conImpuestos = true) {
  const p = POTENCIA_2026;
  const base = p.peajesP1 + p.cargosP1 + p.margenPVPC + p.peajesP2 + p.cargosP2;
  return conImpuestos ? base * (1 + IMPUESTOS.electricidad) * (1 + IMPUESTOS.iva) : base;
}

/** Potencia recomendada: la suma de lo que se enciende a la vez, redondeada a la potencia normalizada siguiente. */
export function potenciaRecomendada(watios: number) {
  const kw = watios / 1000;
  return POTENCIAS_NORMALIZADAS.find((p) => p >= kw) ?? Math.ceil(kw * 10) / 10;
}

export const APARATOS: { id: string; nombre: string; w: number; siempre?: boolean }[] = [
  { id: 'base', nombre: 'Nevera, luces, router y enchufes pequeños', w: 500, siempre: true },
  { id: 'horno', nombre: 'Horno', w: 2200 },
  { id: 'vitro', nombre: 'Vitrocerámica o inducción (dos fuegos)', w: 2500 },
  { id: 'lavadora', nombre: 'Lavadora calentando agua', w: 2000 },
  { id: 'lavavajillas', nombre: 'Lavavajillas', w: 1800 },
  { id: 'secadora', nombre: 'Secadora', w: 2500 },
  { id: 'microondas', nombre: 'Microondas', w: 1000 },
  { id: 'termo', nombre: 'Termo eléctrico', w: 1500 },
  { id: 'aire', nombre: 'Aire acondicionado o bomba de calor', w: 1500 },
  { id: 'calefactor', nombre: 'Radiador o calefactor eléctrico', w: 2000 },
  { id: 'secador', nombre: 'Secador de pelo', w: 1800 },
  { id: 'plancha', nombre: 'Plancha', w: 2000 },
];
