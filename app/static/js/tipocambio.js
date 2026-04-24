/**
 * Tipo de Cambio: manejo del modal simple.
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

// --- Guardar (crea o actualiza segun state.id) ---
async function guardarTipoCambio() {
  const state = window.tipocambioState || { id: null };

  const fecha = document.getElementById('tc-fecha').value;
  const compra = document.getElementById('tc-compra').value;
  const venta = document.getElementById('tc-venta').value;
  const compraSunat = document.getElementById('tc-compra-sunat').value || '0';
  const ventaSunat = document.getElementById('tc-venta-sunat').value || '0';
  const nota = document.getElementById('tc-nota').value.trim().toUpperCase() || null;

  // Validacion client-side
  if (!fecha) {
    alert('La fecha es obligatoria');
    return;
  }
  if (!compra || parseFloat(compra) <= 0) {
    alert('La compra debe ser mayor a cero');
    return;
  }
  if (!venta || parseFloat(venta) <= 0) {
    alert('La venta debe ser mayor a cero');
    return;
  }

  const payload = {
    id_tc: state.id,
    fecha_tc: fecha,
    compra: compra,
    venta: venta,
    compra_sunat: compraSunat,
    venta_sunat: ventaSunat,
    nota: nota,
  };

  const btn = document.getElementById('btn-guardar-tc');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const resp = await fetch('/tablas/tipocambio', {
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
      alert('Error: ' + (typeof msg === 'string' ? msg : JSON.stringify(msg)));
      btn.disabled = false;
      btn.textContent = 'Guardar';
      return;
    }
    cerrarModal();
    window.tipocambioState = null;
    window.location.href = '/tablas/tipocambio';
  } catch (err) {
    alert('Error de red: ' + err);
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarTipoCambio(id) {
  if (!confirm('¿Eliminar este tipo de cambio?')) return;
  try {
    const resp = await fetch('/tablas/tipocambio/' + id, { method: 'DELETE' });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      alert('Error: ' + (data.error || data.detail || 'HTTP ' + resp.status));
      return;
    }
    const row = document.getElementById('row-tipocambio-' + id);
    if (row) row.remove();
  } catch (err) {
    alert('Error de red: ' + err);
  }
}

// --- Init del modal ---
function initTipoCambioModal() {
  setupUppercaseInput(document.getElementById('tc-nota'));

  const fecha = document.getElementById('tc-fecha');
  const compra = document.getElementById('tc-compra');
  if (fecha && !fecha.value) {
    // Default a hoy cuando es nuevo
    const hoy = new Date().toISOString().split('T')[0];
    fecha.value = hoy;
    fecha.focus();
  } else if (compra) {
    compra.focus();
    compra.select();
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('tc-fecha')) {
    initTipoCambioModal();
  }
});
