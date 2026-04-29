/**
 * Documentos SUNAT: manejo del modal y CRUD (zWalter-15).
 * Estado minimo: solo el id de la fila en edicion.
 */

// --- Uppercase en tiempo real preservando cursor ---
function setupUppercaseInput(inputEl) {
  if (!inputEl) return;
  inputEl.addEventListener('input', () => {
    const pos = inputEl.selectionStart;
    inputEl.value = inputEl.value.toUpperCase();
    inputEl.setSelectionRange(pos, pos);
  });
}

// --- Codigo: solo 2 digitos ---
function setupCodigoInput(inputEl) {
  if (!inputEl) return;
  inputEl.addEventListener('input', () => {
    inputEl.value = inputEl.value.replace(/\D/g, '').slice(0, 2);
  });
}

// --- Guardar (crea o actualiza segun state.id) ---
async function guardarDocSunat() {
  const state = window.docSunatState || { id: null };

  const payload = {
    id_docsunat: state.id,
    codigo_docsunat: document.getElementById('ds-codigo').value.trim(),
    nombre_docsunat: document.getElementById('ds-nombre').value.trim().toUpperCase(),
    abreviado_docsunat: document.getElementById('ds-abreviado').value.trim().toUpperCase() || null,
    flag_compra:     document.getElementById('ds-flag-compra').checked     ? 1 : 0,
    flag_venta:      document.getElementById('ds-flag-venta').checked      ? 1 : 0,
    flag_gasto:      document.getElementById('ds-flag-gasto').checked      ? 1 : 0,
    flag_guia:       document.getElementById('ds-flag-guia').checked       ? 1 : 0,
    flag_percepcion: document.getElementById('ds-flag-percepcion').checked ? 1 : 0,
    flag_retencion:  document.getElementById('ds-flag-retencion').checked  ? 1 : 0,
  };

  // Validaciones client-side
  if (!/^\d{2}$/.test(payload.codigo_docsunat)) {
    mostrarToast('El codigo debe ser exactamente 2 digitos numericos', 'warning');
    return;
  }
  if (!payload.nombre_docsunat) {
    mostrarToast('El nombre es obligatorio', 'warning');
    return;
  }

  const btn = document.getElementById('btn-guardar-ds');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const resp = await fetch('/tablas/docsunat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      const msg = data.error || data.detail || ('HTTP ' + resp.status);
      mostrarToast(typeof msg === 'string' ? msg : 'Error al guardar', 'error');
      btn.disabled = false;
      btn.textContent = 'Guardar';
      return;
    }
    cerrarModal();
    window.docSunatState = null;
    window.location.href = '/tablas/docsunat';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarDocSunat(id, nombre) {
  const ok = await mostrarConfirmacion(
    `¿Eliminar el documento "${nombre}"?`,
    { titulo: 'Eliminar documento SUNAT', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/docsunat/' + id, { method: 'DELETE' });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-doc-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- Init del modal ---
function initDocSunatModal() {
  setupCodigoInput(document.getElementById('ds-codigo'));
  setupUppercaseInput(document.getElementById('ds-nombre'));
  setupUppercaseInput(document.getElementById('ds-abreviado'));

  const state = window.docSunatState || { id: null };
  const codigo = document.getElementById('ds-codigo');
  const nombre = document.getElementById('ds-nombre');
  if (state.id === null && codigo) {
    codigo.focus();
    codigo.select();
  } else if (nombre) {
    nombre.focus();
    nombre.select();
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('ds-codigo')) {
    initDocSunatModal();
  }
});
