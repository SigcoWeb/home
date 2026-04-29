/**
 * Clasificador de Gastos: panel doble + modales (zWalter-16).
 * Click en Nivel 1 -> HTMX recarga panel Nivel 2 filtrado.
 */

// --- Marcar fila Nivel 1 como seleccionada ---
function seleccionarNivel1(rowEl, idClagas1) {
  document.querySelectorAll('.row-clagas1').forEach(r => r.classList.remove('selected'));
  rowEl.classList.add('selected');
  if (window.clasificadorGastosState) {
    window.clasificadorGastosState.selectedClagas1 = idClagas1;
  }
}

// --- Init del modal (al cargar via HTMX) ---
function initClasificadorModal() {
  const inp = document.getElementById('cg-nombre');
  if (inp) {
    inp.focus();
    inp.select();
  }
}

// --- Guardar (Nivel 1 o Nivel 2, crea o actualiza segun state.modo) ---
async function guardarClasificador() {
  const state = window.clasifModalState;
  if (!state) return;

  const nombre = document.getElementById('cg-nombre').value.trim();
  if (!nombre) {
    mostrarToast('El nombre es obligatorio', 'warning');
    return;
  }

  const payload = { nombre: nombre };
  let url, method;

  if (state.nivel === 1) {
    if (state.modo === 'nuevo') {
      url = '/tablas/clasificador_gastos/nivel1';
      method = 'POST';
    } else {
      url = '/tablas/clasificador_gastos/nivel1/' + state.id;
      method = 'PUT';
    }
  } else {
    payload.id_clagas1 = state.idPadre;
    if (state.modo === 'nuevo') {
      url = '/tablas/clasificador_gastos/nivel2';
      method = 'POST';
    } else {
      url = '/tablas/clasificador_gastos/nivel2/' + state.id;
      method = 'PUT';
    }
  }

  const btn = document.getElementById('btn-guardar-cg');
  if (btn) { btn.disabled = true; btn.textContent = 'Guardando...'; }

  try {
    const resp = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    if (!resp.ok || data.ok === false) {
      const msg = data.error || data.detail || ('HTTP ' + resp.status);
      mostrarToast(typeof msg === 'string' ? msg : 'Error al guardar', 'error');
      if (btn) { btn.disabled = false; btn.textContent = 'Guardar'; }
      return;
    }
    cerrarModal();
    window.location.href = '/tablas/clasificador_gastos';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    if (btn) { btn.disabled = false; btn.textContent = 'Guardar'; }
  }
}

// --- Eliminar Nivel 1 (con bloqueo si tiene hijos) ---
async function eliminarNivel1(id, nombre) {
  const ok = await mostrarConfirmacion(
    `¿Eliminar la categoría "${nombre}"?`,
    { titulo: 'Eliminar categoría', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/clasificador_gastos/nivel1/' + id, { method: 'DELETE' });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    window.location.href = '/tablas/clasificador_gastos';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- Eliminar Nivel 2 ---
async function eliminarNivel2(id, nombre) {
  const ok = await mostrarConfirmacion(
    `¿Eliminar la sub-categoría "${nombre}"?`,
    { titulo: 'Eliminar sub-categoría', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/clasificador_gastos/nivel2/' + id, { method: 'DELETE' });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-clagas2-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// HTMX: reinicializar modal cuando se carga
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('cg-nombre')) {
    initClasificadorModal();
  }
});
