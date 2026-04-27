/**
 * base.js — interacciones globales del layout (zWalter-11).
 * - toggleSidebar(): colapsa/expande el sidebar lateral en Tablas / Configuración.
 *   Persiste preferencia en localStorage para mantenerla entre páginas.
 * - toggleUserDropdown(): muestra/oculta el menú de usuario en la topbar.
 */

function toggleSidebar() {
  const sidebar = document.querySelector('.tablas-sidebar');
  if (!sidebar) return;
  sidebar.classList.toggle('sidebar-colapsado');
  const colapsado = sidebar.classList.contains('sidebar-colapsado');
  try {
    localStorage.setItem('sidebar-colapsado', colapsado ? '1' : '0');
  } catch (_) {}
}

function toggleUserDropdown() {
  const menu = document.getElementById('user-dropdown-menu');
  if (!menu) return;
  if (menu.hasAttribute('hidden')) {
    menu.removeAttribute('hidden');
  } else {
    menu.setAttribute('hidden', '');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Aplicar preferencia de sidebar al cargar
  try {
    if (localStorage.getItem('sidebar-colapsado') === '1') {
      const sidebar = document.querySelector('.tablas-sidebar');
      if (sidebar) sidebar.classList.add('sidebar-colapsado');
    }
  } catch (_) {}
});

// Cerrar dropdown si se clickea fuera
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('user-dropdown');
  const menu = document.getElementById('user-dropdown-menu');
  if (!dropdown || !menu) return;
  if (!dropdown.contains(e.target)) {
    menu.setAttribute('hidden', '');
  }
});

window.toggleSidebar = toggleSidebar;
window.toggleUserDropdown = toggleUserDropdown;
