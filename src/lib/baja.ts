/**
 * Cuánto se cobra de baja (incapacidad temporal) en 2026, trabajadores por cuenta ajena del Régimen General.
 *
 * Ley General de la Seguridad Social, artículos 169 a 173, con los cambios del Real Decreto-ley 31/2026
 * (BOE-A-2026-21872, en vigor desde el 21 de octubre de 2026):
 * - Enfermedad común o accidente no laboral: nada los días 1 a 3, el 60 % de la base reguladora del día 4 al 20
 *   y el 75 % desde el día 21. Del día 4 al 15 lo paga la empresa; desde el 16, la Seguridad Social o la mutua.
 * - Accidente de trabajo o enfermedad profesional: la empresa paga el sueldo del día de la baja y desde el día
 *   siguiente se cobra el 75 %.
 * - Situaciones especiales (menstruación incapacitante, embarazo desde la semana 39, trastorno menopáusico,
 *   lesiones por violencia de género): la empresa paga el sueldo del día de la baja y desde el día siguiente se
 *   cobra como en enfermedad común (60 % hasta el día 20 y 75 % después), a cargo de la Seguridad Social o la mutua.
 * - Base reguladora: base de cotización por contingencias comunes de un mes (desde el 1 de diciembre de 2026, la de
 *   dos meses antes de la baja) dividida entre 30. Aquí se estima con el sueldo bruto anual entre 12.
 */
import { PARAMETROS_2026 } from './sueldo';

export type TipoBaja = 'comun' | 'profesional' | 'especial';
export type Complemento = 'no' | 'desde1' | 'desde4';

export const BAJA_2026 = {
  baseMinimaMensual: Math.round((PARAMETROS_2026.smiMensual * 14 / 12) * 100) / 100,
  baseMaximaMensual: PARAMETROS_2026.ss.baseMaximaMensual,
};

export interface Tramo { desde: number; hasta: number; pct: number; euDia: number; total: number; paga: string; nota?: string }

export interface ResultadoBaja {
  baseMensual: number; baseDiaria: number; sueldoDiario: number;
  tramos: Tramo[]; totalBaja: number; totalSueldo: number; pierdes: number;
}

/** Base de cotización mensual estimada a partir del sueldo bruto anual (con pagas extra), entre la mínima y la máxima. */
export function baseDesdeBruto(brutoAnual: number) {
  return Math.min(Math.max(brutoAnual / 12, BAJA_2026.baseMinimaMensual), BAJA_2026.baseMaximaMensual);
}

export function calcularBaja(o: { brutoAnual: number; baseMensual?: number; tipo: TipoBaja; dias: number; complemento: Complemento }): ResultadoBaja {
  const baseMensual = o.baseMensual && o.baseMensual > 0 ? Math.min(o.baseMensual, BAJA_2026.baseMaximaMensual) : baseDesdeBruto(o.brutoAnual);
  const baseDiaria = baseMensual / 30;
  const sueldoDiario = o.brutoAnual / 365;
  const dias = Math.max(0, Math.min(545, Math.round(o.dias)));

  // Qué se cobra cada día por ley: [porcentaje de la base (o 'sueldo' si la empresa paga el día entero), quién paga]
  const dia = (d: number): { pct: number | 'sueldo'; paga: string } => {
    if (o.tipo === 'profesional') return d === 1 ? { pct: 'sueldo', paga: 'Empresa' } : { pct: 75, paga: 'Mutua (a través de la empresa)' };
    if (o.tipo === 'especial') {
      if (d === 1) return { pct: 'sueldo', paga: 'Empresa' };
      return { pct: d <= 20 ? 60 : 75, paga: 'Seguridad Social o mutua' };
    }
    if (d <= 3) return { pct: 0, paga: 'Nadie (salvo convenio)' };
    if (d <= 15) return { pct: 60, paga: 'Empresa' };
    return { pct: d <= 20 ? 60 : 75, paga: 'Seguridad Social o mutua (a través de la empresa)' };
  };

  const tramos: Tramo[] = [];
  let totalBaja = 0;
  for (let d = 1; d <= dias; d++) {
    const { pct, paga } = dia(d);
    let euDia = pct === 'sueldo' ? sueldoDiario : baseDiaria * pct / 100;
    let nota: string | undefined;
    const desdeCompl = o.complemento === 'desde1' ? 1 : o.complemento === 'desde4' ? 4 : Infinity;
    if (d >= desdeCompl && euDia < sueldoDiario) { euDia = sueldoDiario; nota = 'con el complemento del convenio'; }
    const pctMostrado = pct === 'sueldo' ? 100 : pct;
    const ult = tramos[tramos.length - 1];
    const pagaTxt = nota && pct !== 'sueldo' && paga !== 'Empresa' ? `${paga} + complemento de la empresa` : paga;
    if (ult && ult.pct === pctMostrado && ult.paga === pagaTxt && Math.abs(ult.euDia - euDia) < 0.005) {
      ult.hasta = d; ult.total += euDia;
    } else {
      tramos.push({ desde: d, hasta: d, pct: pctMostrado, euDia, total: euDia, paga: pagaTxt, nota });
    }
    totalBaja += euDia;
  }
  const totalSueldo = sueldoDiario * dias;
  return { baseMensual, baseDiaria, sueldoDiario, tramos, totalBaja, totalSueldo, pierdes: Math.max(0, totalSueldo - totalBaja) };
}
