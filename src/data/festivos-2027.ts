// Fiestas laborales de 2027: Resolución de 8 de octubre de 2026 de la Dirección General de Trabajo
// (BOE núm. 254, de 13 de octubre de 2026, BOE-A-2026-21254). Copiado del anexo, columna a columna.
export const BOE_FESTIVOS_2027 = {
  ref: 'BOE-A-2026-21254',
  url: 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-21254',
  pdf: 'https://www.boe.es/boe/dias/2026/10/13/pdfs/BOE-A-2026-21254.pdf',
  fecha: '13 de octubre de 2026',
};

export interface Comunidad { slug: string; nombre: string; en: string; nota?: string }

export const COMUNIDADES: Comunidad[] = [
  { slug: 'andalucia', nombre: 'Andalucía', en: 'en Andalucía' },
  { slug: 'aragon', nombre: 'Aragón', en: 'en Aragón' },
  { slug: 'asturias', nombre: 'Asturias', en: 'en Asturias' },
  { slug: 'baleares', nombre: 'Illes Balears', en: 'en Baleares' },
  {
    slug: 'canarias', nombre: 'Canarias', en: 'en Canarias',
    nota: 'Cada isla tiene además su propia fiesta (Decreto 115/2026 del Gobierno de Canarias): El Hierro, 24 de septiembre (Nuestra Señora de los Reyes); Fuerteventura, 17 de septiembre (Nuestra Señora de la Peña); Gran Canaria, 8 de septiembre (Nuestra Señora del Pino); La Gomera, 4 de octubre (Nuestra Señora de Guadalupe); La Palma, 5 de agosto (Nuestra Señora de las Nieves); Lanzarote y La Graciosa, 15 de septiembre (Nuestra Señora de los Volcanes), y Tenerife, 2 de febrero (Virgen de la Candelaria).',
  },
  { slug: 'cantabria', nombre: 'Cantabria', en: 'en Cantabria' },
  { slug: 'castilla-la-mancha', nombre: 'Castilla-La Mancha', en: 'en Castilla-La Mancha' },
  { slug: 'castilla-y-leon', nombre: 'Castilla y León', en: 'en Castilla y León' },
  {
    slug: 'cataluna', nombre: 'Cataluña', en: 'en Cataluña',
    nota: 'En el territorio de Arán, el Lunes de Pascua (29 de marzo) se sustituye por el 17 de junio, Fiesta de Arán (Orden EMT/52/2026 de la Generalitat).',
  },
  { slug: 'extremadura', nombre: 'Extremadura', en: 'en Extremadura' },
  { slug: 'galicia', nombre: 'Galicia', en: 'en Galicia' },
  { slug: 'madrid', nombre: 'Comunidad de Madrid', en: 'en la Comunidad de Madrid' },
  { slug: 'murcia', nombre: 'Región de Murcia', en: 'en la Región de Murcia' },
  { slug: 'navarra', nombre: 'Navarra', en: 'en Navarra' },
  { slug: 'pais-vasco', nombre: 'País Vasco', en: 'en el País Vasco' },
  { slug: 'la-rioja', nombre: 'La Rioja', en: 'en La Rioja' },
  { slug: 'comunidad-valenciana', nombre: 'Comunitat Valenciana', en: 'en la Comunitat Valenciana' },
  { slug: 'ceuta', nombre: 'Ceuta', en: 'en Ceuta' },
  { slug: 'melilla', nombre: 'Melilla', en: 'en Melilla' },
];

const TODAS = COMUNIDADES.map((c) => c.slug);
const menos = (...x: string[]) => TODAS.filter((s) => !x.includes(s));

export type Tipo = 'nacional' | 'nacional-opcional' | 'autonomica';
export interface Festivo { fecha: string; nombre: string; tipo: Tipo; donde: string[] }

// tipo: «nacional» = fiesta nacional no sustituible (*); «nacional-opcional» = fiesta nacional que la comunidad
// podía sustituir y no lo ha hecho (**); «autonomica» = fiesta propia de la comunidad (***).
export const FESTIVOS_2027: Festivo[] = [
  { fecha: '2027-01-01', nombre: 'Año Nuevo', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-01-06', nombre: 'Epifanía del Señor (Reyes)', tipo: 'nacional-opcional', donde: TODAS },
  { fecha: '2027-03-01', nombre: 'Día de Andalucía', tipo: 'autonomica', donde: ['andalucia'] },
  { fecha: '2027-03-01', nombre: 'Día de les Illes Balears', tipo: 'autonomica', donde: ['baleares'] },
  { fecha: '2027-03-10', nombre: 'Fiesta del Eid Fitr', tipo: 'autonomica', donde: ['melilla'] },
  { fecha: '2027-03-19', nombre: 'San José', tipo: 'nacional-opcional', donde: ['galicia', 'madrid', 'murcia', 'navarra', 'comunidad-valenciana'] },
  { fecha: '2027-03-25', nombre: 'Jueves Santo', tipo: 'nacional-opcional', donde: menos('cataluna', 'comunidad-valenciana') },
  { fecha: '2027-03-26', nombre: 'Viernes Santo', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-03-29', nombre: 'Lunes de Pascua', tipo: 'autonomica', donde: ['baleares', 'cataluna', 'navarra', 'pais-vasco', 'la-rioja', 'comunidad-valenciana'] },
  { fecha: '2027-04-23', nombre: 'San Jorge, Día de Aragón', tipo: 'autonomica', donde: ['aragon'] },
  { fecha: '2027-04-23', nombre: 'Fiesta de Castilla y León', tipo: 'autonomica', donde: ['castilla-y-leon'] },
  { fecha: '2027-05-01', nombre: 'Fiesta del Trabajo', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-05-17', nombre: 'Día de las Letras Gallegas', tipo: 'autonomica', donde: ['galicia'] },
  { fecha: '2027-05-17', nombre: 'Fiesta del Sacrificio (Eid al Adha)', tipo: 'autonomica', donde: ['ceuta', 'melilla'] },
  { fecha: '2027-05-27', nombre: 'Corpus Christi', tipo: 'autonomica', donde: ['castilla-la-mancha'] },
  { fecha: '2027-05-31', nombre: 'Día de Castilla-La Mancha', tipo: 'autonomica', donde: ['castilla-la-mancha'] },
  { fecha: '2027-06-09', nombre: 'Día de la Región de Murcia', tipo: 'autonomica', donde: ['murcia'] },
  { fecha: '2027-06-09', nombre: 'Día de La Rioja', tipo: 'autonomica', donde: ['la-rioja'] },
  { fecha: '2027-06-24', nombre: 'San Juan', tipo: 'autonomica', donde: ['cataluna'] },
  { fecha: '2027-07-28', nombre: 'Día de las Instituciones de Cantabria', tipo: 'autonomica', donde: ['cantabria'] },
  { fecha: '2027-08-05', nombre: 'Nuestra Señora de África', tipo: 'autonomica', donde: ['ceuta'] },
  { fecha: '2027-08-16', nombre: 'Lunes siguiente a la Asunción de la Virgen', tipo: 'nacional-opcional', donde: ['andalucia', 'aragon', 'asturias', 'canarias', 'castilla-y-leon', 'madrid'] },
  { fecha: '2027-09-08', nombre: 'Día de Asturias', tipo: 'autonomica', donde: ['asturias'] },
  { fecha: '2027-09-08', nombre: 'Día de Extremadura', tipo: 'autonomica', donde: ['extremadura'] },
  { fecha: '2027-09-11', nombre: 'Diada Nacional de Cataluña', tipo: 'autonomica', donde: ['cataluna'] },
  { fecha: '2027-09-15', nombre: 'La Bien Aparecida', tipo: 'autonomica', donde: ['cantabria'] },
  { fecha: '2027-10-07', nombre: 'Aniversario del primer Gobierno Vasco', tipo: 'autonomica', donde: ['pais-vasco'] },
  { fecha: '2027-10-09', nombre: 'Día de la Comunitat Valenciana', tipo: 'autonomica', donde: ['comunidad-valenciana'] },
  { fecha: '2027-10-11', nombre: 'Fiesta que sustituye al 15 de agosto', tipo: 'autonomica', donde: ['extremadura'] },
  { fecha: '2027-10-12', nombre: 'Fiesta Nacional de España', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-11-01', nombre: 'Todos los Santos', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-12-06', nombre: 'Día de la Constitución', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-12-08', nombre: 'Inmaculada Concepción', tipo: 'nacional', donde: TODAS },
  { fecha: '2027-12-25', nombre: 'Navidad', tipo: 'nacional', donde: TODAS },
];

export const festivosDe = (slug: string) => FESTIVOS_2027.filter((f) => f.donde.includes(slug));
