// ⚙️ CONFIGURACIÓN GENERAL — cambia aquí el nombre, dominio, AdSense y redes
export const SITE = {
  name: 'Al Final de Mes',
  tagline: 'Pensiones, paro, Hacienda y luz: lo que afecta a tu bolsillo, explicado claro',
  url: 'https://alfinaldemes.com', // también en astro.config.mjs
  lang: 'es',
  locale: 'es_ES',
  email: 'contacto@alfinaldemes.com',
  // Autor que firma los artículos (página /autor/)
  author: {
    name: 'Marcos Fernández León',
    slug: 'marcos-fernandez',
    // ← personalízala: tu formación o experiencia con estos temas da confianza a lectores y a Google
    bio: 'Fundador de Al Final de Mes. Explica los cambios en pensiones, prestaciones, impuestos y facturas que afectan a la economía de casa, siempre con el dato y la fuente oficial.',
  },
  // Datos legales del titular (aviso legal y privacidad)
  ownerName: 'Marcos Fernández León',
  ownerNif: '48158108H', // si lo dejas vacío, no se muestra
  // AdSense: se puede usar la misma cuenta de Zona Leonida añadiendo este sitio en AdSense.
  // Déjalo vacío hasta que Google apruebe el sitio nuevo.
  adsenseClient: '',
  // Cloudflare Web Analytics (sin cookies): pega el token cuando lo crees en Cloudflare.
  cfAnalyticsToken: '',
  // Redes sociales (deja vacío lo que aún no exista)
  social: { telegram: '', whatsapp: '', facebook: '', x: '' },
};

// Secciones. Las que tienen `abierta: false` todavía no salen en el menú.
export const CATEGORIES = {
  luz: {
    label: 'Luz',
    titulo: 'Precio de la luz y facturas',
    desc: 'El precio de la luz de hoy y de mañana por horas, las horas más baratas y las noticias sobre tarifas, bono social y factura eléctrica.',
  },
  pensiones: {
    label: 'Pensiones',
    titulo: 'Pensiones',
    desc: 'Subidas de las pensiones, fechas de cobro, pagas extra, jubilación y requisitos, explicados con los datos oficiales de la Seguridad Social.',
  },
  paro: {
    label: 'Paro y ayudas',
    titulo: 'Paro, subsidios y ayudas',
    desc: 'Prestación por desempleo, subsidios del SEPE, ingreso mínimo vital y ayudas públicas: requisitos, cuantías y cómo pedirlas.',
  },
  hacienda: {
    label: 'Hacienda',
    titulo: 'Hacienda, renta e impuestos',
    desc: 'Declaración de la renta, IRPF, deducciones, plazos y avisos de la Agencia Tributaria explicados para que no se te escape nada.',
  },
} as const;

export type CategoryKey = keyof typeof CATEGORIES;
