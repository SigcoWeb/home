/**
 * Personal: manejo del modal simple con muchos campos.
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

function aplicarUppercaseGlobal() {
  const ids = ['pe-nombre', 'pe-direccion', 'pe-cargo', 'pe-observacion'];
  ids.forEach((id) => setupUppercaseInput(document.getElementById(id)));
}

// --- DNI: solo digitos, max 8 ---
function setupDniInput() {
  const dni = document.getElementById('pe-dni');
  if (!dni) return;
  dni.addEventListener('input', () => {
    dni.value = dni.value.replace(/\D/g, '').slice(0, 8);
  });
}

// --- Celular: solo digitos, + - y espacios ---
function setupCelularInput() {
  const cel = document.getElementById('pe-celular');
  if (!cel) return;
  cel.addEventListener('input', () => {
    cel.value = cel.value.replace(/[^\d+\-\s]/g, '');
  });
}

// --- Guardar (crea o actualiza segun state.id) ---
async function guardarPersonal() {
  const state = window.personalState || { id: null };
  const fechaCeseVal = document.getElementById('pe-fecha-cese').value;

  const payload = {
    id_personal: state.id,
    dni: document.getElementById('pe-dni').value.trim(),
    nombre: document.getElementById('pe-nombre').value.trim().toUpperCase(),
    direccion: document.getElementById('pe-direccion').value.trim().toUpperCase() || null,
    celular: document.getElementById('pe-celular').value.trim() || null,
    fecha_ingreso: document.getElementById('pe-fecha-ingreso').value,
    fecha_cese: fechaCeseVal || null, // vacio => null => vigente
    cargo: document.getElementById('pe-cargo').value.trim().toUpperCase() || null,
    comision_factura: document.getElementById('pe-comision-factura').value || '0',
    comision_producto: document.getElementById('pe-comision-producto').checked,
    comision_familia: document.getElementById('pe-comision-familia').checked,
    repartidor: document.getElementById('pe-repartidor').checked,
    mesero: document.getElementById('pe-mesero').checked,
    observacion: document.getElementById('pe-observacion').value.trim().toUpperCase() || null,
    estado: document.getElementById('pe-estado').checked,
  };

  // Validaciones client-side
  if (!payload.dni || !/^\d{8}$/.test(payload.dni)) {
    mostrarToast('DNI debe tener 8 digitos', 'warning');
    return;
  }
  if (!payload.nombre) {
    mostrarToast('El nombre es obligatorio', 'warning');
    return;
  }
  if (!payload.fecha_ingreso) {
    mostrarToast('La fecha de ingreso es obligatoria', 'warning');
    return;
  }
  if (payload.fecha_cese && payload.fecha_cese < payload.fecha_ingreso) {
    mostrarToast('La fecha de cese no puede ser anterior a la fecha de ingreso', 'warning');
    return;
  }

  const btn = document.getElementById('btn-guardar-pe');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const resp = await fetch('/tablas/personal', {
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
    window.personalState = null;
    window.location.href = '/tablas/personal';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarPersonal(id) {
  const ok = await mostrarConfirmacion(
    '¿Eliminar este empleado?',
    { titulo: 'Eliminar empleado', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/personal/' + id, { method: 'DELETE' });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-personal-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- Init del modal ---
function initPersonalModal() {
  aplicarUppercaseGlobal();
  setupDniInput();
  setupCelularInput();

  const dni = document.getElementById('pe-dni');
  const nombre = document.getElementById('pe-nombre');
  if (dni && !dni.value) {
    dni.focus();
  } else if (nombre) {
    nombre.focus();
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('pe-dni')) {
    initPersonalModal();
  }
});
