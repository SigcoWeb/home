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
    mostrarToast('La fecha es obligatoria', 'warning');
    return;
  }
  if (!compra || parseFloat(compra) <= 0) {
    mostrarToast('La compra debe ser mayor a cero', 'warning');
    return;
  }
  if (!venta || parseFloat(venta) <= 0) {
    mostrarToast('La venta debe ser mayor a cero', 'warning');
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
      mostrarToast(typeof msg === 'string' ? msg : 'Error al guardar', 'error');
      btn.disabled = false;
      btn.textContent = 'Guardar';
      return;
    }
    cerrarModal();
    window.tipocambioState = null;
    window.location.href = '/tablas/tipocambio';
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// --- Eliminar desde el listado ---
async function eliminarTipoCambio(id) {
  const ok = await mostrarConfirmacion(
    '¿Eliminar este tipo de cambio?',
    { titulo: 'Eliminar tipo de cambio', tipo: 'peligro', textoAceptar: 'Eliminar' }
  );
  if (!ok) return;
  try {
    const resp = await fetch('/tablas/tipocambio/' + id, { method: 'DELETE' });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ('Error HTTP ' + resp.status), 'error');
      return;
    }
    const row = document.getElementById('row-tipocambio-' + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast('Error de red. Intenta nuevamente.', 'error');
  }
}

// --- TC SUNAT (zWalter-13): banner de estado ---
function _setBannerTcSunat(estado, mensaje) {
  const banner = document.getElementById('banner-tc-sunat');
  if (!banner) return;

  banner.classList.remove(
    'banner-tc-sunat--ok',
    'banner-tc-sunat--warn',
    'banner-tc-sunat--loading'
  );

  if (estado === null) {
    banner.setAttribute('hidden', '');
    return;
  }

  banner.removeAttribute('hidden');
  banner.classList.add('banner-tc-sunat--' + estado);

  const icon = banner.querySelector('.banner-tc-icon');
  const msg = banner.querySelector('.banner-tc-mensaje');
  if (icon) {
    icon.textContent = estado === 'ok' ? '✓'
                     : estado === 'warn' ? '⚠'
                     : '…';
  }
  if (msg) msg.textContent = mensaje;
}

// --- Convertir fecha del input (yyyy-mm-dd) a partes dd/mm/yyyy para la API ---
function _partesFechaParaApi(fechaIso) {
  if (!fechaIso || fechaIso.length !== 10) return null;
  const partes = fechaIso.split('-');
  if (partes.length !== 3) return null;
  return { yyyy: partes[0], mm: partes[1], dd: partes[2] };
}


// --- Convertir fecha del input (yyyy-mm-dd) a dd/mm/yyyy para la API ---
function _formatearFechaParaApi(fechaIso) {
    if (!fechaIso || fechaIso.length !== 10) return null;
    const partes = fechaIso.split("-");
    if (partes.length !== 3) return null;
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

// Guard simple: si ya hay fetch en curso, los siguientes se ignoran
let _tcSunatPendiente = false;

async function obtenerTcSunat(fechaIso) {
    const fechaApi = _formatearFechaParaApi(fechaIso);
    if (!fechaApi) {
        _setBannerTcSunat(null);
        return;
    }

    // Si ya hay un fetch activo, no apilar
    if (_tcSunatPendiente) return;
    _tcSunatPendiente = true;

    _setBannerTcSunat("loading", "Consultando TC SUNAT...");

    try {
        const resp = await fetch(`/tablas/tipocambio/api/sunat/${fechaApi}`);
        const data = await resp.json();

        if (data.ok) {
            const compraSunat = document.getElementById("tc-compra-sunat");
            const ventaSunat = document.getElementById("tc-venta-sunat");
            if (compraSunat) compraSunat.value = Number(data.compra).toFixed(3);
            if (ventaSunat) ventaSunat.value = Number(data.venta).toFixed(3);

            _setBannerTcSunat(
                "ok",
                `TC SUNAT obtenido: C ${Number(data.compra).toFixed(3)} / V ${Number(data.venta).toFixed(3)}`
            );
        } else {
            _setBannerTcSunat(
                "warn",
                "No se pudo obtener TC SUNAT, complete manualmente"
            );
        }
    } catch (err) {
        _setBannerTcSunat(
            "warn",
            "No se pudo obtener TC SUNAT, complete manualmente"
        );
    } finally {
        _tcSunatPendiente = false;
    }
}

// --- Hook al input de fecha: re-fetch al cambiar ---
function _engancharFechaSunat() {
  const fechaInput = document.getElementById('tc-fecha');
  if (!fechaInput) return;
  if (fechaInput.dataset.sunatHooked === '1') return;
  fechaInput.dataset.sunatHooked = '1';

  fechaInput.addEventListener('change', () => {
    if (fechaInput.value) {
      obtenerTcSunat(fechaInput.value);
    }
  });
}

// --- Init del modal ---
function initTipoCambioModal() {
  setupUppercaseInput(document.getElementById('tc-nota'));

  const fecha = document.getElementById('tc-fecha');
  const compra = document.getElementById('tc-compra');
  const state = window.tipocambioState || { id: null };

  if (fecha && !fecha.value) {
    // Default a hoy cuando es nuevo
    const hoy = new Date().toISOString().split('T')[0];
    fecha.value = hoy;
    fecha.focus();
  } else if (compra) {
    compra.focus();
    compra.select();
  }

  // Hook de re-fetch al cambiar la fecha
  _engancharFechaSunat();

  // Auto-fetch SOLO en modo Nuevo (no en edición)
  if (state.id === null && fecha && fecha.value) {
    obtenerTcSunat(fecha.value);
  }
}

// HTMX: reinicializar cuando se carga el modal
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && e.target.id === 'modal-root' && document.getElementById('tc-fecha')) {
    initTipoCambioModal();
  }
});
