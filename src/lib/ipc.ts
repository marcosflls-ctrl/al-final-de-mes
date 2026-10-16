import fs from 'node:fs';

export interface Serie { i?: Record<string, number>; va?: Record<string, number>; vm?: Record<string, number> }
export interface DatosIPC { fuente: string; actualizado: string; mes: string; general: Serie; grupos: Record<string, Serie>; subclases: Record<string, Serie> }

export function datosIPC(): DatosIPC | null {
  try { return JSON.parse(fs.readFileSync('src/data/ipc.json', 'utf8')); } catch { return null; }
}

/** Productos de la cesta: nombre del INE → nombre que mostramos */
export const CESTA: [string, string][] = [
  ['Pan y productos de panadería', 'Pan y bollería'],
  ['Cereales', 'Arroz y otros cereales'],
  ['Macarrones, tallarines, cuscús y pastas alimenticias similares', 'Pasta'],
  ['Cereales de desayuno', 'Cereales de desayuno'],
  ['Carne, fresca, refrigerada o congelada', 'Carne fresca o congelada'],
  ['Preparados de carne y despojos', 'Embutidos y preparados de carne'],
  ['Pescado,  fresco, refrigerado o congelado', 'Pescado fresco o congelado'],
  ['Marisco, vivo, fresco, refrigerado o congelado', 'Marisco'],
  ['Preparados de pescado', 'Conservas y preparados de pescado'],
  ['Leche entera', 'Leche entera'],
  ['Leche desnatada y semidesnatada', 'Leche desnatada y semidesnatada'],
  ['Queso', 'Queso'],
  ['Yogur y productos similares', 'Yogures'],
  ['Huevos', 'Huevos'],
  ['Aceites vegetales', 'Aceite (de oliva, girasol y otros)'],
  ['Mantequilla y otros aceites y grasas derivados de la leche', 'Mantequilla'],
  ['Cítricos frescos', 'Naranjas, mandarinas y limones'],
  ['Frutas de hueso y frutas de pepita, frescas', 'Manzanas, peras, melocotones y similares'],
  ['Frutas tropicales, dátiles e higos', 'Plátanos y fruta tropical'],
  ['Bayas frescas', 'Fresas, uvas y otras bayas'],
  ['Hortalizas de hoja o de tallo, frescas o refrigeradas', 'Lechuga, espinacas y verduras de hoja'],
  ['Hortalizas cultivadas por su fruto, frescas o refrigeradas', 'Tomates, pimientos, calabacines y similares'],
  ['Patatas y otros tubérculos', 'Patatas'],
  ['Legumbres secas', 'Legumbres secas'],
  ['Azúcar de caña y azúcar de remolacha', 'Azúcar'],
  ['Chocolate, cacao y productos alimenticios a base de cacao', 'Chocolate y cacao'],
  ['Alimentos preparados', 'Platos preparados'],
  ['Café y sucedáneos de café', 'Café'],
  ['Agua', 'Agua embotellada'],
  ['Refrescos', 'Refrescos'],
  ['Zumos de frutas y hortalizas', 'Zumos'],
  ['Cerveza', 'Cerveza'],
  ['Vino de uva', 'Vino'],
];

const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
export const nombreMes = (m: string, anio = true) => `${MESES[parseInt(m.slice(5, 7), 10) - 1]}${anio ? ` de ${m.slice(0, 4)}` : ''}`;
export const pct = (v?: number | null, d = 1) => (v == null ? '—' : `${v > 0 ? '+' : ''}${v.toLocaleString('es-ES', { minimumFractionDigits: d, maximumFractionDigits: d })} %`);
