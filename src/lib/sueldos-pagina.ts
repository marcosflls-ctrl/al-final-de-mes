// Páginas «X euros brutos en neto»: qué sueldos tienen página y los casos que se muestran en cada una.
import { calcular, type Entrada } from './sueldo';

export const BRUTOS_PAGINA: number[] = [];
for (let b = 15000; b <= 100000; b += 1000) BRUTOS_PAGINA.push(b);

export const slugSueldo = (b: number) => `${b}-euros-brutos`;
export const urlSueldo = (b: number) => `/hacienda/sueldo-neto/${slugSueldo(b)}/`;

/** Caso base de todas las páginas: soltero/a, sin hijos, nacido en 1990, contrato indefinido. */
export const base = (brutoAnual: number, pagas: 12 | 14 = 14, extra: Partial<Entrada> = {}) =>
  calcular({ brutoAnual, pagas, contrato: 'indefinido', anioNacimiento: 1990, situacion: 3, hijos: [], discapacidad: 'no', ...extra });

/** Situaciones familiares que se comparan en cada página. */
export const CASOS: { nombre: string; detalle: string; e: Partial<Entrada> }[] = [
  { nombre: 'Sin hijos', detalle: 'Soltero/a, o casado/a con la pareja trabajando', e: {} },
  { nombre: 'Con 1 hijo', detalle: 'Hijo de 8 años, compartido con el otro progenitor', e: { hijos: [{ anio: 2018, entero: false }] } },
  { nombre: 'Con 2 hijos', detalle: 'Hijos de 6 y 10 años, compartidos con el otro progenitor', e: { hijos: [{ anio: 2016, entero: false }, { anio: 2020, entero: false }] } },
  { nombre: 'Familia monoparental, 1 hijo', detalle: 'Hijo de 8 años que vive solo contigo', e: { situacion: 1, hijos: [{ anio: 2018, entero: true }] } },
  { nombre: 'Pareja a cargo y 2 hijos', detalle: 'La pareja gana menos de 1.500 € al año', e: { situacion: 2, hijos: [{ anio: 2016, entero: true }, { anio: 2020, entero: true }] } },
  { nombre: 'Contrato temporal', detalle: 'Sin hijos, contrato de menos de un año', e: { contrato: 'temporal-corto' } },
];
