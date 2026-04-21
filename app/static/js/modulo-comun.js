// Funciones compartidas entre los layouts de "Tablas" y "Configuración".

function cerrarModal() {
  const root = document.getElementById('modal-root');
  if (root) root.innerHTML = '';
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') cerrarModal();
});

// Buscador genérico de sidebar: filtra opciones que coincidan con el texto.
// Usa los mismos selectores que ambos sidebars comparten.
function inicializarBuscadorSidebar(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;

  input.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    const opciones = document.querySelectorAll(
      '.tablas-sidebar__opcion, .tablas-sidebar__opcion-suelta, .config-sidebar__opcion'
    );
    opciones.forEach((el) => {
      const match = el.textContent.toLowerCase().includes(q);
      el.style.display = !q || match ? '' : 'none';
    });

    if (q) {
      document.querySelectorAll('.tablas-sidebar__seccion').forEach((det) => {
        const tieneMatch = [...det.querySelectorAll('.tablas-sidebar__opcion')]
          .some((o) => o.style.display !== 'none');
        if (tieneMatch) det.setAttribute('open', '');
      });
    }
  });
}
