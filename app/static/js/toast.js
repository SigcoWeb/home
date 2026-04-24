/**
 * Toast notification system
 * API global: window.mostrarToast(mensaje, tipo, duracionMs)
 *
 * tipo: "success" | "error" | "warning" | "info"  (default: "info")
 * duracionMs: numero en ms (default: 4000). 0 o negativo => no auto-cierra.
 */
(function () {
  const ICONOS = {
    success: '✓',
    error: '✕',
    warning: '!',
    info: 'i',
  };

  function ensureContainer() {
    let c = document.getElementById('toast-container');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  function mostrarToast(mensaje, tipo, duracionMs) {
    tipo = tipo || 'info';
    duracionMs = typeof duracionMs === 'number' ? duracionMs : 4000;

    const container = ensureContainer();
    const el = document.createElement('div');
    el.className = 'toast toast--' + tipo;
    el.setAttribute('role', tipo === 'error' ? 'alert' : 'status');

    const icon = document.createElement('span');
    icon.className = 'toast-icon';
    icon.textContent = ICONOS[tipo] || ICONOS.info;

    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = mensaje;

    const close = document.createElement('button');
    close.className = 'toast-close';
    close.type = 'button';
    close.setAttribute('aria-label', 'Cerrar');
    close.textContent = '×';
    close.addEventListener('click', () => cerrar(el));

    el.appendChild(icon);
    el.appendChild(body);
    el.appendChild(close);
    container.appendChild(el);

    if (duracionMs > 0) {
      setTimeout(() => cerrar(el), duracionMs);
    }
    return el;
  }

  function cerrar(el) {
    if (!el || el.classList.contains('toast--leaving')) return;
    el.classList.add('toast--leaving');
    setTimeout(() => el.remove(), 220);
  }

  window.mostrarToast = mostrarToast;
  window.cerrarToast = cerrar;
})();
