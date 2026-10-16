/**
 * Comprar o alquilar: compara el patrimonio que tendrías al cabo de N años en cada caso.
 * Se parte del mismo dinero inicial (entrada + gastos de compra) y del mismo gasto mensual:
 * quien paga menos cada mes invierte la diferencia, igual que el inquilino invierte la entrada.
 */
export interface Supuestos {
  precio: number;
  entradaPct: number;        // % del precio que pagas de entrada
  impuestosCompraPct: number; // ITP (vivienda usada) o IVA + AJD (nueva)
  otrosGastosCompraPct: number; // notaría, registro, gestoría, tasación
  tipoHipoteca: number;      // % TAE aproximada, tipo fijo
  plazoHipoteca: number;     // años
  gastosPropietarioPct: number; // IBI, comunidad, seguro y mantenimiento al año, % del precio
  revalorizacion: number;    // % anual del precio de la vivienda
  gastosVentaPct: number;    // % del valor al vender (agencia, plusvalía…)
  alquiler: number;          // € al mes
  subidaAlquiler: number;    // % anual
  rentabilidad: number;      // % anual neta que obtendrías invirtiendo
  anios: number;
}

export interface Anio { anio: number; patrimonioCompra: number; patrimonioAlquiler: number; cuotaMes: number; alquilerMes: number }

export function cuotaHipoteca(capital: number, tipoAnual: number, anios: number): number {
  const i = tipoAnual / 100 / 12, n = anios * 12;
  if (capital <= 0 || n <= 0) return 0;
  return Math.abs(i) < 1e-9 ? capital / n : (capital * i) / (1 - Math.pow(1 + i, -n));
}

export function simular(s: Supuestos): Anio[] {
  const entrada = (s.precio * s.entradaPct) / 100;
  const gastosCompra = (s.precio * (s.impuestosCompraPct + s.otrosGastosCompraPct)) / 100;
  let pendiente = s.precio - entrada;
  const cuota = cuotaHipoteca(pendiente, s.tipoHipoteca, s.plazoHipoteca);
  const iMes = s.tipoHipoteca / 100 / 12;
  const rMes = Math.pow(1 + s.rentabilidad / 100, 1 / 12) - 1;

  let cartInquilino = entrada + gastosCompra; // el inquilino invierte lo que el comprador se gasta al principio
  let cartComprador = 0;                      // el comprador invierte si un mes paga menos que el inquilino
  let valor = s.precio;
  let alquiler = s.alquiler;
  const res: Anio[] = [];
  for (let a = 1; a <= s.anios; a++) {
    const gastosPropMes = (valor * s.gastosPropietarioPct) / 100 / 12;
    let cuotaAnio = 0;
    for (let m = 0; m < 12; m++) {
      const mesHip = (a - 1) * 12 + m;
      const pagoHip = mesHip < s.plazoHipoteca * 12 && pendiente > 0.005 ? cuota : 0;
      if (pagoHip) {
        const intereses = pendiente * iMes;
        pendiente = Math.max(0, pendiente - (pagoHip - intereses));
      }
      const gastoComprador = pagoHip + gastosPropMes;
      cuotaAnio = pagoHip;
      cartInquilino *= 1 + rMes;
      cartComprador *= 1 + rMes;
      const dif = gastoComprador - alquiler;
      if (dif > 0) cartInquilino += dif; else cartComprador += -dif;
    }
    valor *= 1 + s.revalorizacion / 100;
    const patrimonioCompra = valor * (1 - s.gastosVentaPct / 100) - pendiente + cartComprador;
    res.push({ anio: a, patrimonioCompra, patrimonioAlquiler: cartInquilino, cuotaMes: cuotaAnio, alquilerMes: alquiler });
    alquiler *= 1 + s.subidaAlquiler / 100;
  }
  return res;
}

/** Primer año a partir del cual comprar sale mejor y ya no deja de serlo (null si no ocurre). */
export function anioEquilibrio(r: Anio[]): number | null {
  for (let i = 0; i < r.length; i++) if (r.slice(i).every((x) => x.patrimonioCompra >= x.patrimonioAlquiler)) return r[i].anio;
  return null;
}
