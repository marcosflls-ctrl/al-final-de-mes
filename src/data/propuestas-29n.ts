// Propuestas de los partidos para el 29N por perfil, para /hacienda/que-proponen-para-tu-caso-29n/.
// Sale de la comparativa (src/content/posts/que-cambia-en-tu-bolsillo-segun-quien-gobierne-29n.md) y de las guías
// por temas, donde está la fuente de cada dato. Si cambia algo allí, hay que cambiarlo también aquí.
// Un partido sin entrada en un tema sale como «Sin propuesta concreta recogida».

export const ACTUALIZADO = '18 de noviembre de 2026';
export const PARTIDOS = ['PP', 'Vox', 'PSOE', 'Sumar', 'Podemos'] as const;
type Partido = (typeof PARTIDOS)[number];
type Tema = { tema: string; propuestas: Partial<Record<Partido, string>> };
type Perfil = { id: string; etiqueta: string; titulo: string; temas: Tema[]; guia: { href: string; texto: string } };

const IRPF: Tema = {
  tema: 'IRPF',
  propuestas: {
    PP: 'Actualizarlo con la inflación, salario mínimo exento y rebaja para menores de 35',
    Vox: 'Bajarlo y simplificarlo, con rebaja por hijos (sin cifras)',
    PSOE: 'Tipo máximo del 35 % para rentas del capital de más de 300.000 €; sin cambios recogidos en la tarifa general',
    Sumar: 'Bajarlo a los sueldos bajos y que el capital pague más parecido al trabajo',
    Podemos: 'Que las rentas del capital paguen lo mismo que las del trabajo',
  },
};

export const PERFILES: Perfil[] = [
  {
    id: 'asalariado', etiqueta: 'Trabajo por cuenta ajena', titulo: 'Si trabajas por cuenta ajena',
    temas: [
      IRPF,
      { tema: 'Jornada', propuestas: { PP: 'No apoyó la reducción a 37,5 horas', Vox: 'En contra de reducirla por ley', PSOE: '37,5 horas y avanzar a 35 negociando', Sumar: '32 horas', Podemos: '30 horas' } },
      { tema: 'Otras', propuestas: { PP: 'Autónomos: cuota cero el primer año y sin IVA por debajo de 85.000 €', Vox: 'Autónomos: cuota cero si ganan menos del salario mínimo', PSOE: 'Bajas por cáncer al 75 % desde el primer día y paro para becarios', Sumar: 'Reparto obligatorio de parte de los beneficios', Podemos: 'Despido de 45 días por año y salarios con el IPC' } },
    ],
    guia: { href: '/paro/empleo-elecciones-29n-balance-y-propuestas/', texto: 'empleo y elecciones del 29N' },
  },
  {
    id: 'smi', etiqueta: 'Cobro el salario mínimo o cerca', titulo: 'Si cobras el salario mínimo o algo más',
    temas: [
      { tema: 'Salario mínimo', propuestas: { PP: 'Que no pague IRPF; sin cifra de subida', Vox: 'Sin cifra', PSOE: 'Por ley, por encima del 60 % del salario medio', Sumar: 'Por ley, el 60 % del salario medio neto', Podemos: '1.800 € al mes' } },
      { tema: 'IRPF', propuestas: IRPF.propuestas },
    ],
    guia: { href: '/paro/salario-minimo-2027/', texto: 'salario mínimo 2027' },
  },
  {
    id: 'pensionista', etiqueta: 'Cobro una pensión', titulo: 'Si cobras una pensión',
    temas: [
      { tema: 'Subida con el IPC', propuestas: { PP: 'Sí', Vox: 'Pagarlas «como sea»', PSOE: 'Sí, y blindarlo en la Constitución', Sumar: 'Sí; ninguna mínima por debajo del salario mínimo', Podemos: 'Subir las mínimas, sin cifra' } },
      { tema: 'El sistema', propuestas: { PP: 'Mantener el sistema público y un pacto de Estado por la dependencia', Vox: 'Sostenerlo con más empleo y natalidad, sin capitalización', PSOE: 'Un año más de cotización por cada hijo', Sumar: 'Volver a la jubilación a los 65', Podemos: 'Jubilación a los 63' } },
    ],
    guia: { href: '/pensiones/pensiones-elecciones-29n-balance-y-propuestas/', texto: 'pensiones y elecciones del 29N' },
  },
  {
    id: 'inquilino', etiqueta: 'Vivo de alquiler', titulo: 'Si vives de alquiler',
    temas: [
      { tema: 'Decretos de alquiler', propuestas: { PP: 'En contra', Vox: 'En contra', PSOE: 'Mantenerlos y reforzarlos', Sumar: 'Sus impulsores', Podemos: 'A favor' } },
      { tema: 'Tu renta', propuestas: { PP: 'Derogar la Ley de Vivienda y ventajas para caseros que renueven por debajo del IPC', Vox: 'Derogar la Ley de Vivienda y ayudas con «prioridad nacional»', PSOE: 'Congelar las rentas por encima del índice en zonas tensionadas; seguro de impago para jóvenes', Sumar: 'Alquiler máximo del 25 % de los ingresos medios de la zona', Podemos: 'Bajar los alquileres un 40 %' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'comprador', etiqueta: 'Quiero comprar vivienda', titulo: 'Si quieres comprar vivienda',
    temas: [
      { tema: 'Ayudas a la compra', propuestas: { PP: 'IVA al 4 % para menores de 40, avales para la entrada y «Hucha Hogar Joven»', Vox: 'IVA 0 % en la primera vivienda nueva y sin ITP en la usada', PSOE: 'Préstamos para pagar la entrada; más de 25.000 millones en avales y préstamos del ICO' } },
      { tema: 'Oferta de vivienda', propuestas: { PP: 'Un millón de hogares en la legislatura y licencias en tres meses', Vox: 'Liberalizar el suelo', PSOE: '100.000 viviendas públicas', Sumar: '1,5 millones de viviendas públicas de alquiler en doce años' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'casero', etiqueta: 'Tengo un piso alquilado', titulo: 'Si tienes un piso alquilado',
    temas: [
      { tema: 'Tu renta', propuestas: { PP: 'Ventajas fiscales si renuevas por debajo del IPC', Vox: 'Derogar la Ley de Vivienda', PSOE: 'Congelar las rentas por encima del índice en zonas tensionadas', Sumar: 'Alquiler máximo del 25 % de los ingresos medios de la zona', Podemos: 'Bajar los alquileres un 40 %' } },
      { tema: 'Grandes propietarios', propuestas: { PSOE: 'Impuesto a fondos y grandes propietarios por las viviendas que no alquilen', Sumar: 'Expropiación por fases a partir de 50 viviendas, solo a empresas' } },
    ],
    guia: { href: '/vivienda/vivienda-elecciones-29n-balance-y-propuestas/', texto: 'vivienda y elecciones del 29N' },
  },
  {
    id: 'familia', etiqueta: 'Tengo hijos a mi cargo', titulo: 'Si tienes hijos a tu cargo',
    temas: [
      { tema: 'Ayudas por hijos', propuestas: { PP: 'Actualizar el IRPF con la inflación', Vox: 'Rebaja del IRPF por hijos (sin cifras)', PSOE: 'Prestación por crianza sin cuantía todavía y 1.000 € al nacer en una cuenta pública', Sumar: '200 € al mes por cada menor', Podemos: 'Revisar el pago de los permisos de maternidad y paternidad' } },
      { tema: 'Compra de vivienda', propuestas: { PP: 'IVA al 4 % para menores de 40 y avales para la entrada', PSOE: 'Préstamos para pagar la entrada' } },
    ],
    guia: { href: '/hacienda/impuestos-elecciones-29n-balance-y-propuestas/', texto: 'impuestos y elecciones del 29N' },
  },
  {
    id: 'energia', etiqueta: 'Me preocupan la luz y la gasolina', titulo: 'Luz y gasolina',
    temas: [
      { tema: 'Impuestos de la energía', propuestas: { PP: 'Quitar el impuesto del 7 % a la producción eléctrica', Vox: 'Rebaja «masiva» de los de la luz, sin cifras', PSOE: 'Rebajas solo cuando se disparan los precios', Sumar: 'Bajar el IVA de la energía y tres horas de luz gratis al día', Podemos: 'Intervenir el precio de la luz' } },
      { tema: 'Nucleares', propuestas: { PP: 'Quitar el calendario de cierre en 100 días', Vox: 'Quitar el calendario de cierre', PSOE: 'Almaraz, hasta 2030', Sumar: 'En contra de alargar algunas' } },
    ],
    guia: { href: '/luz/luz-carburantes-elecciones-29n-balance-y-propuestas/', texto: 'luz, gasolina y elecciones del 29N' },
  },
];
