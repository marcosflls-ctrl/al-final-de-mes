/**
 * Cálculo del sueldo neto en 2026 (territorio común: todas las comunidades salvo País Vasco y Navarra).
 *
 * - Retención de IRPF: algoritmo oficial de la Agencia Tributaria para 2026
 *   («Algoritmo de cálculo del tipo de retención… ejercicio 2026, a partir de 10 de septiembre»).
 * - Cotizaciones del trabajador a la Seguridad Social en 2026 (Orden de cotización 2026).
 *
 * Si cambia la normativa, solo hay que tocar las constantes de este archivo.
 */

export const PARAMETROS_2026 = {
  ejercicio: 2026,
  // Seguridad Social: tipos a cargo del trabajador
  ss: {
    contingenciasComunes: 0.047,
    mei: 0.0015,
    desempleoIndefinido: 0.0155,
    desempleoTemporal: 0.016,
    formacion: 0.001,
    baseMaximaMensual: 5101.2,
    // Cotización adicional de solidaridad (parte del trabajador) sobre lo que exceda la base máxima
    solidaridad: [
      { hasta: 5611.32, tipo: 0.0019 },
      { hasta: 7651.8, tipo: 0.0021 },
      { hasta: Infinity, tipo: 0.0024 },
    ],
  },
  // Salario mínimo interprofesional (jornada completa, 14 pagas). Real Decreto del SMI de cada año.
  // Al cambiar: solo esta cifra. El anual y los textos de las calculadoras se calculan solos.
  smiMensual: 1221,
  get smiAnual() { return this.smiMensual * 14; },
};

export type SituacionFamiliar = 1 | 2 | 3;
export type Discapacidad = 'no' | '33a65' | '65omas';
export type Contrato = 'indefinido' | 'temporal' | 'temporal-corto';

export interface Hijo {
  /** año de nacimiento */
  anio: number;
  /** true si se computa por entero (no se reparte con el otro progenitor) */
  entero: boolean;
}

export interface Entrada {
  brutoAnual: number;
  pagas: 12 | 14;
  contrato: Contrato;
  /** año de nacimiento del trabajador */
  anioNacimiento: number;
  /** 1: soltero/a, viudo/a o separado/a con hijos a su cargo exclusivo; 2: casado/a y el cónyuge gana menos de 1.500 € al año; 3: resto */
  situacion: SituacionFamiliar;
  hijos: Hijo[];
  discapacidad: Discapacidad;
}

export interface Resultado {
  bruto: number;
  seguridadSocial: number;
  desgloseSS: { comunes: number; mei: number; desempleo: number; formacion: number; solidaridad: number };
  tipoRetencion: number;
  retencion: number;
  netoAnual: number;
  /** neto de un mes normal */
  netoMensual: number;
  /** neto de cada paga extra (solo con 14 pagas): no lleva cotizaciones, que ya se reparten en los 12 meses */
  netoExtra?: number;
  brutoPorPaga: number;
  exento: boolean;
  /** pasos intermedios del algoritmo, para mostrarlos y para las pruebas */
  pasos: { rendimientoNeto: number; otrosGastos: number; reduccion: number; base: number; minimo: number; cuota1: number; cuota2: number; cuota: number; limite43?: number };
}

const r2 = (x: number) => Math.round((x + Number.EPSILON) * 100) / 100;
const trunc2 = (x: number) => Math.floor(x * 100 + 1e-9) / 100;

/** Escala de retención (art. 101.1 LIRPF). */
export function escala(base: number): number {
  const tramos = [
    [0, 0, 0.19], [12450, 2365.5, 0.24], [20200, 4225.5, 0.30], [35200, 8725.5, 0.37], [60000, 17901.5, 0.45], [300000, 125901.5, 0.47],
  ] as const;
  if (base <= 0) return 0;
  let fila = tramos[0];
  for (const t of tramos) if (base > t[0]) fila = t;
  return r2(fila[1] + (base - fila[0]) * fila[2]);
}

/** Cotizaciones anuales del trabajador a la Seguridad Social. */
export function cotizaciones(brutoAnual: number, contrato: Contrato, p = PARAMETROS_2026) {
  // La base mensual incluye la parte proporcional de las pagas extra: bruto anual / 12
  const mensual = brutoAnual / 12;
  const base = Math.min(mensual, p.ss.baseMaximaMensual);
  const desempleo = contrato === 'indefinido' ? p.ss.desempleoIndefinido : p.ss.desempleoTemporal;
  let solidaridad = 0, desde = p.ss.baseMaximaMensual;
  for (const t of p.ss.solidaridad) {
    if (mensual <= desde) break;
    solidaridad += (Math.min(mensual, t.hasta) - desde) * t.tipo;
    desde = t.hasta;
  }
  const d = {
    comunes: r2(base * p.ss.contingenciasComunes * 12),
    mei: r2(base * p.ss.mei * 12),
    desempleo: r2(base * desempleo * 12),
    formacion: r2(base * p.ss.formacion * 12),
    solidaridad: r2(solidaridad * 12),
  };
  return { total: r2(d.comunes + d.mei + d.desempleo + d.formacion + d.solidaridad), desglose: d };
}

/** Límites excluyentes de retención (art. 81 RIRPF, tabla 1 del algoritmo). */
function limiteExcluyente(situacion: SituacionFamiliar, numHijos: number): number | null {
  const n = Math.min(numHijos, 2);
  const tabla: Record<SituacionFamiliar, (number | null)[]> = {
    1: [null, 17644, 18694],
    2: [17197, 18130, 19262],
    3: [15876, 16342, 16867],
  };
  return tabla[situacion][n];
}

export function calcular(e: Entrada, p = PARAMETROS_2026): Resultado {
  const retrib = r2(Math.max(0, e.brutoAnual));
  const ss = cotizaciones(retrib, e.contrato, p);
  const cot = ss.total;
  const edad = p.ejercicio - e.anioNacimiento;
  // Descendientes que dan derecho a mínimo: menores de 25 años (o con discapacidad, no contemplado aquí)
  const hijos = e.hijos.filter((h) => p.ejercicio - h.anio < 25).sort((a, b) => a.anio - b.anio);
  const numHijos = hijos.length;
  // Situación 1 exige al menos un hijo
  const situacion: SituacionFamiliar = e.situacion === 1 && numHijos === 0 ? 3 : e.situacion;

  // Gastos deducibles
  let otrosGastos = 2000;
  if (e.discapacidad === '65omas') otrosGastos += 7750;
  else if (e.discapacidad === '33a65') otrosGastos += 3500;
  if (retrib - cot < 0) otrosGastos = 0;
  if (otrosGastos > retrib - cot) otrosGastos = Math.max(0, retrib - cot);

  // Rendimiento neto y reducción por obtención de rendimientos del trabajo (art. 20 LIRPF)
  const rnt = Math.max(0, retrib - cot);
  let red20 = 0;
  if (rnt <= 14852) red20 = 7302;
  else if (rnt <= 17673.52) red20 = 7302 - 1.75 * (rnt - 14852);
  else if (rnt < 19747.5) red20 = 2364.34 - 1.14 * (rnt - 17673.52);
  red20 = r2(red20);
  const rntRedu = Math.max(0, rnt - otrosGastos - red20);

  // Reducciones y base
  const redHijos = numHijos > 2 ? 600 : 0;
  const base = r2(Math.max(0, rntRedu - redHijos));

  // Mínimo personal y familiar
  let minimo = 5550 + (edad > 64 ? 1150 : 0) + (edad > 74 ? 1400 : 0);
  const porHijo = [2400, 2700, 4000, 4500];
  hijos.forEach((h, i) => {
    const f = h.entero ? 1 : 0.5;
    minimo += porHijo[Math.min(i, 3)] * f;
    if (h.anio > p.ejercicio - 3) minimo += 2800 * f;
  });
  if (e.discapacidad === '65omas') minimo += 9000 + 3000;
  else if (e.discapacidad === '33a65') minimo += 3000;
  minimo = r2(minimo);

  const limite = limiteExcluyente(situacion, numHijos);
  const exento = limite != null && retrib <= limite;

  let cuota1 = 0, cuota2 = 0, cuota = 0, limite43: number | undefined;
  if (!exento) {
    cuota1 = escala(base);
    cuota2 = escala(minimo);
    cuota = Math.max(0, cuota1 - cuota2);
    if (retrib <= 35200 && limite != null) {
      limite43 = r2((retrib - limite) * 0.43);
      if (cuota > limite43) cuota = limite43;
    }
  }

  let tipo = exento || retrib === 0 ? 0 : trunc2((cuota / retrib) * 100);
  if (!exento && e.contrato === 'temporal-corto' && tipo < 2) tipo = 2;
  const retencion = r2((retrib * tipo) / 100);
  const neto = r2(retrib - cot - retencion);

  return {
    bruto: retrib,
    seguridadSocial: cot,
    desgloseSS: ss.desglose,
    tipoRetencion: tipo,
    retencion,
    netoAnual: neto,
    // Con 14 pagas, las cotizaciones se descuentan en los 12 meses normales (incluyen la parte de las extras)
    netoMensual: r2(retrib / e.pagas - cot / 12 - (retrib / e.pagas) * tipo / 100),
    netoExtra: e.pagas === 14 ? r2((retrib / 14) * (1 - tipo / 100)) : undefined,
    brutoPorPaga: r2(retrib / e.pagas),
    exento,
    pasos: { rendimientoNeto: r2(rnt), otrosGastos: r2(otrosGastos), reduccion: red20, base, minimo, cuota1, cuota2, cuota: r2(cuota), limite43 },
  };
}
