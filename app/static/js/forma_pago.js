/**
 * Formas de Pago: manejo del modal y CRUD (zWalter-14).
 * Estado minimo: solo el id de la fila en edicion.
 */

const TIPOS_FORPAG = [
  "Contado", "Credito", "Tarjeta",
  "Transferencia", "Depósito", "Cheque", "Billetero",
];

// --- Uppercase en tiempo real preservando cursor ---
function setupUppercaseInput(inputEl) {
  if (!inputEl) return;
  inputEl.addEventListener('input', () => {
    const pos = inputEl.selectionStart;
    inputEl.value = inputEl.value.toUpperCase();
    inputEl.setSelectionRange(pos, pos);
  });
}

// --- Guardar (crea o actualiza segun state.id) ---
async function guardarFormaPago() {
  const state = window.formaPagoState || { id: null };

  const diasRaw = document.getElementById('fp-dias').value;
  const dias = parseInt(diasRaw === '' ? '0' : diasRaw, 10);

  const payload = {
    id_forpag: state.id,
    nombre_forpag: document.getElementById('fp-nombre').value.trim().toUpperCase(),
    tipo_forpag: document.getElementById('fp-tipo').value.trim(),
    compra: document.getElementById('fp-compra').checked,
    venta: document.getElementById('fp-venta').checked,
    pv: document.getElementById('fp-pv').checked,
    agenda: document.getElementById('fp-agenda').checked,
    dias: isNaN(dias) ? 0 : dias,
  };

  // Validaciones client-side
  if (!payload.nombre_forpag) {
    mostrarToast('La descripcion es obligatoria', 'warning');
    return;
  }
  if (!payload.tipo_forpag) {
    mostrarToast('Selecciona un tipo', 'warning');
    return;
  }
  if (!TIPOS_FORPAG.includes(payload.tipo_forpag)) {
    mostrarToast('Tipo de forma de pago invalido', 'warning');
    return;
  }
  if (payload.dias < 0 || payload.dias > 365) {
    mostrarToast('Dias debe estar entre 0 y 365', 'warning');
    return;
  }

  const btn = document.getElementById('btn-guardar-fp');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const resp = await fetch('/tablas/forma_pago', {
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
    window.formaPagoState = null;
    window.location.href = '/tablas/forma_pago';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarFormaPago(id, nombre) {
  const ok = await mostrarConfirmacion(
    `¿Eliminar la forma de pago "${nombre}"?`,
    { titulo: 'Eliminar forma de pago', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/forma_pago/' + id, { method: 'DELETE' });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-forma-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- Init del modal ---
function initFormaPagoModal() {
  setupUppercaseInput(document.getElementById('fp-nombre'));
  const nombre = document.getElementById('fp-nombre');
  if (nombre) {
    nombre.focus();
    nombre.select();
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('fp-nombre')) {
    initFormaPagoModal();
  }
});
