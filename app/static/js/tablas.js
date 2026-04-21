// El cierre de modal y el helper genérico viven en modulo-comun.js.
// Este archivo sólo inicializa el buscador del sidebar de Tablas.

if (typeof inicializarBuscadorSidebar === 'function') {
  inicializarBuscadorSidebar('buscarOpcion');
}
