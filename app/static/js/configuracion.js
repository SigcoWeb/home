// Inicializa el buscador del sidebar de Configuración.
// El cierre de modal y el buscador genérico viven en modulo-comun.js.

if (typeof inicializarBuscadorSidebar === 'function') {
  inicializarBuscadorSidebar('buscarOpcionConfig');
}

// Matriz de permisos: UX de checkboxes interdependientes.
// - Al desmarcar "Acceso" se desmarcan todos los btn_* de esa fila.
// - Al marcar cualquier btn_* se marca "Acceso" automáticamente.
document.addEventListener('change', (e) => {
  const target = e.target;
  if (!(target instanceof HTMLInputElement) || target.type !== 'checkbox') return;

  const fila = target.closest('.permisos-fila-opcion');
  if (!fila) return;

  if (target.classList.contains('perm-acceso') && !target.checked) {
    fila.querySelectorAll('.perm-btn').forEach((c) => { c.checked = false; });
  }
  if (target.classList.contains('perm-btn') && target.checked) {
    const acceso = fila.querySelector('.perm-acceso');
    if (acceso && !acceso.checked) acceso.checked = true;
  }
});
