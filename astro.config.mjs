import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import fs from 'node:fs';

// Fecha de última modificación de cada artículo (updated o date) para el mapa del sitio
const lastmod = {};
for (const f of fs.readdirSync('src/content/posts').filter((f) => f.endsWith('.md'))) {
  const head = fs.readFileSync(`src/content/posts/${f}`, 'utf8').split('\n---', 2)[0];
  const get = (k) => (head.match(new RegExp(`^${k}:\\s*["']?([^"'\\n]+)`, 'm')) || [])[1];
  if (/^draft:\s*true/m.test(head)) continue; // los borradores no se publican
  const fecha = get('updated') || get('date');
  const cat = get('category');
  // los artículos programados para más adelante tampoco están publicados todavía
  if (fecha && cat && !Number.isNaN(Date.parse(fecha)) && Date.parse(fecha) <= Date.now()) lastmod[`/${cat}/${f.replace(/\.md$/, '')}/`] = new Date(fecha).toISOString();
}

// Páginas de datos que se actualizan solas: su fecha es la del último dato descargado
const datos = (f) => {
  try { return new Date(JSON.parse(fs.readFileSync(`src/data/${f}.json`, 'utf8')).actualizado).toISOString(); } catch { return undefined; }
};
const paginasDeDatos = [
  ['/gasolina/', datos('carburantes')],       // incluye las páginas de cada provincia y municipio
  ['/luz/', datos('luz')],
  ['/ipc/', datos('ipc')],
  ['/vivienda/euribor-hoy/', datos('euribor')],
  ['/divisas/', datos('divisas')],
];
// Páginas generadas que se revisan a mano (sueldos, calendario laboral): fecha en src/data/fechas-paginas.json
const fechasPaginas = JSON.parse(fs.readFileSync('src/data/fechas-paginas.json', 'utf8'));
for (const [pre, f] of Object.entries(fechasPaginas)) if (pre.startsWith('/')) paginasDeDatos.push([pre, new Date(f).toISOString()]);
// Portada y portadas de sección: la fecha del artículo más reciente
const masReciente = (prefijo) => Object.entries(lastmod).filter(([u]) => u.startsWith(prefijo)).map(([, f]) => f).sort().pop();

export default defineConfig({
  site: 'https://alfinaldemes.com',
  trailingSlash: 'always',
  integrations: [sitemap({
    filter: (page) => !page.includes('/buscar/') && !page.includes('/hacienda/comisiones-fondos/'),
    serialize: (item) => {
      const ruta = new URL(item.url).pathname;
      let m = lastmod[ruta];
      if (!m) {
        const d = paginasDeDatos.find(([pre]) => ruta === pre || (pre.endsWith('/') && ruta.startsWith(pre) && pre !== '/luz/'));
        if (d) m = d[1];
        else if (ruta === '/') m = masReciente('/');
        else if (/^\/(luz|pensiones|paro|vivienda|hacienda)\/$/.test(ruta)) m = masReciente(ruta);
      }
      return m ? { ...item, lastmod: m } : item;
    },
  })],
});
