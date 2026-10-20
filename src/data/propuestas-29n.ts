// Propuestas de los partidos para el 29N por perfil, para /hacienda/que-proponen-para-tu-caso-29n/.
// Sale de la comparativa (src/content/posts/que-cambia-en-tu-bolsillo-segun-quien-gobierne-29n.md) y de las guías
// por temas, donde está la fuente de cada dato. Si cambia algo allí, hay que cambiarlo también aquí.
// Un partido sin entrada en un tema sale como «Sin propuesta concreta recogida».

export const ACTUALIZADO = '20 de octubre de 2026';
export const PARTIDOS = ['PP', 'Vox', 'PSOE', 'Sumar', 'Podemos'] as const;
type Partido = (typeof PARTIDOS)[number];
type Tema = { tema: string; propuestas: Partial<Record<Partido, string>> };
type Perfil = { id: string; etiqueta: string; titulo: string; temas: Tema[]; guia: { href: string; texto: string } };

const IRPF: Tema = {
  tema: 'IRPF',
  propuestas: {
    PP: 'Actualizarlo con la inflación y duplicar el mínimo por hijos',
    Vox: 'Mínimo exento de 22.000 € y solo dos tipos, del 15 % y el 25 %',
    PSOE: 'Más progresividad, sin cifras',
    Sumar: 'Que paguen más las rentas, patrimonios y herencias altas',
    Podemos: 'Que paguen más las grandes empresas y patrimonios',
  },
};

export const PERFILES: Perfil[] = [
  {
    id: 'asalariado', etiqueta: 'Trabajo por cuenta ajena', titulo: 'Si trabajas por cuenta ajena',
    temas: [
      IRPF,
      { tema: 'Jornada', propuestas: { PP: 'No apoyó la reducción a 37,5 horas', Vox: 'En contra de reducirla por ley', PSOE: '36 horas antes de 2030', Sumar: 'Impulsó las 37,5 horas', Podemos: '35 horas' } },
      { tema: 'Otras', propuestas: { PP: 'Rebajar lo que se cobra en las bajas y permitir más horas extra', Sumar: 'Registro horario digital' } },
    ],
    guia: { href: '/paro/empleo-elecciones-29n-balance-y-propuestas/', texto: 'empleo y elecciones del 29N' },
  },
  {
    id: 'smi', etiqueta: 'Cobro el salario mínimo o cerca', titulo: 'Si cobras el salario mínimo o algo más',
    temas: [
      { tema: 'Salario mínimo', propuestas: { PP: 'Ligarlo a la productividad, sin cifra', Vox: 'Sin cifra', PSOE: 'El 60 % del salario medio', Sumar: 'Seguir subiéndolo', Podemos: '1.800 € al mes' } },
      { tema: 'IRPF', propuestas: IRPF.propuestas },
    ],
    guia: { href: '/paro/salario-minimo-2027/', texto: 'salario mínimo 2027' },
  },
  {
    id: 'pensionista', etiqueta: 'Cobro una pensión', titulo: 'Si cobras una pensión',
    temas: [
      { tema: 'Subida con el IPC', propuestas: { PP: 'Sí', Vox: 'Pagarlas «como sea»', PSOE: 'Sí; la de 2027, aprobada antes de fin de año', Sumar: 'Sí' } },
      { tema: 'El sistema', propuestas: { PP: 'Mantener el sistema público y asegurar que sea viable', Vox: 'Un modelo mixto que añada capitalización', PSOE: 'Acusa a PP y Vox de querer recortar', Sumar: '«No hay ningún riesgo»' } },
    ],
    guia: { href: '/pensiones/pensiones-elecciones-29n-balance-y-propuestas/', texto: 'pensiones y elecciones del 29N' },
  },
  {
    id: 'inquilino', etiqueta: 'Vivo de alquiler', titulo: 'Si vives de alquiler',
    temas: [
      { tema: 'Decretos de alquiler', propuestas: { PP: 'En contra', Vox: 'En contra', PSOE: 'Mantenerlos y reforzarlos', Sumar: 'Ir más allá: contratos indefinidos y rentas congeladas' } },
      { tema: 'Qué plantean', propuestas: { PP: 'Construir 250.000 viviendas al año', Vox: 'Vivienda social con «prioridad nacional» y liberalizar suelo', PSOE: 'Proteger a los inquilinos', Sumar: 'Más protección frente a los desahucios' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'comprador', etiqueta: 'Quiero comprar vivienda', titulo: 'Si quieres comprar vivienda',
    temas: [
      { tema: 'Ayudas a la compra', propuestas: { PP: 'IVA al 4 % y avales del 100 % para jóvenes', Vox: 'Liberalizar suelo para que haya más vivienda', PSOE: 'Préstamos para pagar la entrada' } },
      { tema: 'Oferta de vivienda', propuestas: { PP: '250.000 viviendas al año', Vox: 'Construir vivienda social de forma masiva' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'casero', etiqueta: 'Tengo un piso alquilado', titulo: 'Si tienes un piso alquilado',
    temas: [
      { tema: 'Decretos de alquiler', propuestas: { PP: 'En contra', Vox: 'En contra', PSOE: 'Mantenerlos y reforzarlos', Sumar: 'Contratos indefinidos y rentas congeladas' } },
      { tema: 'Impuestos', propuestas: { Sumar: 'Que paguen más los patrimonios altos', Podemos: 'Que paguen más los grandes patrimonios' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'familia', etiqueta: 'Tengo hijos a mi cargo', titulo: 'Si tienes hijos a tu cargo',
    temas: [
      { tema: 'IRPF', propuestas: { PP: 'Duplicar el mínimo por hijos', Vox: 'Mínimo exento de 22.000 € para todos', PSOE: 'Más progresividad, sin cifras' } },
      { tema: 'Compra de vivienda', propuestas: { PP: 'IVA al 4 % y avales del 100 % para jóvenes', PSOE: 'Préstamos para pagar la entrada' } },
    ],
    guia: { href: '/hacienda/impuestos-elecciones-29n-balance-y-propuestas/', texto: 'impuestos y elecciones del 29N' },
  },
  {
    id: 'energia', etiqueta: 'Me preocupan la luz y la gasolina', titulo: 'Luz y gasolina',
    temas: [
      { tema: 'Impuestos de la energía', propuestas: { PP: 'IVA de la energía al 10 % de forma permanente', Vox: 'Bajarlos', PSOE: 'Rebajas solo cuando se disparan los precios', Sumar: 'Sin propuesta fiscal', Podemos: 'Una empresa pública de energía' } },
      { tema: 'Nucleares', propuestas: { PP: 'Mantenerlas más allá de 2030', Vox: 'Alargar su vida', PSOE: 'Almaraz, hasta 2030', Sumar: 'En contra de alargar algunas' } },
    ],
    guia: { href: '/luz/luz-carburantes-elecciones-29n-balance-y-propuestas/', texto: 'luz, gasolina y elecciones del 29N' },
  },
];
