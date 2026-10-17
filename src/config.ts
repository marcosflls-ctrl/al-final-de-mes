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
    name: 'Redacción Al Final de Mes',
    slug: 'redaccion',
    bio: 'El equipo de Al Final de Mes explica los cambios en pensiones, prestaciones, impuestos y facturas que afectan a la economía de casa, siempre con el dato y la fuente oficial.',
  },
  // Datos legales del titular (aviso legal y privacidad)
  ownerName: 'Marcos Fernández León',
  ownerNif: '48158108H', // si lo dejas vacío, no se muestra
  // AdSense: se puede usar la misma cuenta de Zona Leonida añadiendo este sitio en AdSense.
  // Déjalo vacío hasta que Google apruebe el sitio nuevo.
  adsenseClient: 'ca-pub-2093028838178784',
  // Cloudflare Web Analytics (sin cookies): pega el token cuando lo crees en Cloudflare.
  cfAnalyticsToken: '',
  // Redes sociales (deja vacío lo que aún no exista)
  social: { telegram: '', whatsapp: '', facebook: '', x: '' },
  // Webs hermanas, para enlazarlas en el pie
  hermanas: [{ nombre: 'Dinero en Claro', url: 'https://dineroenclaro.com/', texto: 'ahorro e inversión explicados con datos oficiales: depósitos, Letras del Tesoro, fondos, bolsa y planes de pensiones' }],
};

// Secciones. Las que tienen `abierta: false` todavía no salen en el menú.
export const CATEGORIES = {
  luz: {
    label: 'Luz y carburantes',
    titulo: 'Precio de la luz, el gas y los carburantes',
    // Si una sección tiene `menu`, en la cabecera sale como desplegable con estos enlaces
    menu: [
      { href: '/luz/', label: 'Precio de la luz', rutas: ['/luz/'] },
      { href: '/luz/cuanto-cuesta-cada-electrodomestico/', label: 'Coste de cada electrodoméstico', rutas: ['/luz/cuanto-cuesta-cada-electrodomestico/'] },
      { href: '/gasolina/', label: 'Gasolina y diésel', rutas: ['/gasolina/'] },
    ],
    desc: 'El precio de la luz de hoy y de mañana por horas, y las noticias sobre la factura eléctrica, el gas, el butano, la gasolina y el bono social.',
  },
  pensiones: {
    label: 'Pensiones',
    titulo: 'Pensiones',
    desc: 'Subidas de las pensiones, fechas de cobro, pagas extra, jubilación y requisitos, explicados con los datos oficiales de la Seguridad Social.',
  },
  paro: {
    label: 'Empleo y paro',
    titulo: 'Empleo, paro y ayudas',
    desc: 'Salario mínimo, nóminas, prestación por desempleo, subsidios del SEPE, ingreso mínimo vital y ayudas públicas: requisitos, cuantías y cómo pedirlas.',
  },
  vivienda: {
    label: 'Vivienda',
    titulo: 'Vivienda, alquiler e hipotecas',
    desc: 'Alquiler, prórrogas y subidas de renta, ayudas a la vivienda, hipotecas y euríbor: lo que cambia para inquilinos, propietarios y compradores.',
  },
  hacienda: {
    label: 'Hacienda',
    titulo: 'Hacienda, renta e impuestos',
    desc: 'Declaración de la renta, IRPF, IVA, deducciones, plazos y avisos de la Agencia Tributaria explicados para que no se te escape nada.',
  },
} as const;

export type CategoryKey = keyof typeof CATEGORIES;
