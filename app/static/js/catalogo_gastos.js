/**
 * Catalogo de Gastos: manejo del modal, dropdowns en cascada y CRUD (zWalter-17).
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

// --- Cargar opciones de Clasificador 2 al cambiar Clasificador 1 ---
async function cargarClagas2() {
  const idClagas1 = document.getElementById('cg-clagas1').value;
  const selectClagas2 = document.getElementById('cg-clagas2');
  if (!selectClagas2) return;

  selectClagas2.innerHTML = '<option value="">— seleccionar —</option>';
  if (!idClagas1) return;

  try {
    const resp = await fetch('/tablas/catalogo_gastos/clagas2_options/' + idClagas1);
    const data = await resp.json();
    if (data.ok && Array.isArray(data.options)) {
      data.options.forEach(opt => {
        const o = document.createElement('option');
        o.value = opt.id_clagas2;
        o.textContent = opt.nombre_clagas2;
        selectClagas2.appendChild(o);
      });
    }
  } catch (err) {
    mostrarToast('No se pudo cargar las sub-categorias', 'error');
  }
}

// --- Guardar (crea o actualiza segun state.id) ---
async function guardarCatalogoGasto() {
  const state = window.catalogoGastosState || { id: null };

  const codigo = document.getElementById('cg-codigo').value.trim().toUpperCase();
  const nombre = document.getElementById('cg-nombre').value.trim().toUpperCase();
  const idUnidad = parseInt(document.getElementById('cg-unidad').value, 10);
  const idClagas1 = parseInt(document.getElementById('cg-clagas1').value, 10);
  const idClagas2 = parseInt(document.getElementById('cg-clagas2').value, 10);
  const precioStr = document.getElementById('cg-precio').value.trim();
  const nota = document.getElementById('cg-nota').value.trim();
  const estado = document.getElementById('cg-estado').checked;

  // Validaciones
  if (!codigo) {
    mostrarToast('El codigo es obligatorio', 'warning');
    return;
  }
  if (!nombre) {
    mostrarToast('El nombre del gasto es obligatorio', 'warning');
    return;
  }
  if (!idUnidad) {
    mostrarToast('Selecciona una unidad', 'warning');
    return;
  }
  if (!idClagas1) {
    mostrarToast('Selecciona Clasificador 1', 'warning');
    return;
  }
  if (!idClagas2) {
    mostrarToast('Selecciona Clasificador 2', 'warning');
    return;
  }

  let precioCosto = null;
  if (precioStr) {
    precioCosto = parseFloat(precioStr.replace(',', '.'));
    if (isNaN(precioCosto) || precioCosto < 0) {
      mostrarToast('Precio Costo debe ser mayor o igual a 0', 'warning');
      return;
    }
  }

  const payload = {
    id_gasto: state.id,
    codigo_gasto: codigo,
    nombre_gasto: nombre,
    id_unidad: idUnidad,
    id_clagas1: idClagas1,
    id_clagas2: idClagas2,
    precio_costo: precioCosto,
    nota: nota || null,
    estado: estado,
  };

  const btn = document.getElementById('btn-guardar-cg');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const resp = await fetch('/tablas/catalogo_gastos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    if (!resp.ok || data.ok === false) {
      const msg = data.error || data.detail || ('HTTP ' + resp.status);
      mostrarToast(typeof msg === 'string' ? msg : 'Error al guardar', 'error');
      btn.disabled = false;
      btn.textContent = 'Guardar';
      return;
    }
    cerrarModal();
    window.catalogoGastosState = null;
    window.location.href = '/tablas/catalogo_gastos';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarCatalogoGasto(id, nombre) {
  const ok = await mostrarConfirmacion(
    `¿Eliminar el gasto "${nombre}"?`,
    { titulo: 'Eliminar gasto', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/catalogo_gastos/' + id, { method: 'DELETE' });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-gasto-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- Init del modal ---
function initCatalogoGastosModal() {
  setupUppercaseInput(document.getElementById('cg-codigo'));
  setupUppercaseInput(document.getElementById('cg-nombre'));

  const codigo = document.getElementById('cg-codigo');
  if (codigo) {
    codigo.focus();
    codigo.select();
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('cg-codigo')) {
    initCatalogoGastosModal();
  }
});
