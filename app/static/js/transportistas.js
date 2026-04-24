/**
 * Transportistas: manejo del modal con grilla embebida.
 * Todo el estado vive en window.transportistaState hasta Guardar Todo.
 */

// --- Validacion RUC modulo 11 ---
function validarRucPeru(ruc) {
  if (!ruc || !/^\d{11}$/.test(ruc)) return false;
  if (!["10", "15", "16", "17", "20"].includes(ruc.substring(0, 2))) return false;
  const factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
  let suma = 0;
  for (let i = 0; i < 10; i++) suma += parseInt(ruc[i], 10) * factores[i];
  const resto = suma % 11;
  const digitoEsperado = (11 - resto) % 10;
  return digitoEsperado === parseInt(ruc[10], 10);
}

// --- Validacion DNI ---
function validarDniPeru(dni) {
  return /^\d{8}$/.test(dni);
}

// --- RUC: activacion al digito 11 ---
function setupRucValidation(inputEl, feedbackEl) {
  inputEl.addEventListener("input", () => {
    inputEl.value = inputEl.value.replace(/\D/g, "").slice(0, 11);
    const v = inputEl.value;
    if (v.length < 11) {
      feedbackEl.textContent = "";
      feedbackEl.className = "";
      inputEl.classList.remove("campo-invalido", "campo-valido");
      return;
    }
    if (validarRucPeru(v)) {
      feedbackEl.textContent = "RUC valido";
      feedbackEl.className = "feedback-ok";
      inputEl.classList.add("campo-valido");
      inputEl.classList.remove("campo-invalido");
    } else {
      feedbackEl.textContent = "RUC invalido (digito verificador)";
      feedbackEl.className = "feedback-err";
      inputEl.classList.add("campo-invalido");
      inputEl.classList.remove("campo-valido");
    }
  });
}

// --- DNI: hook preparado para API en zW-07b ---
function setupDniHook(inputEl) {
  if (!inputEl) return;
  inputEl.addEventListener("input", () => {
    inputEl.value = inputEl.value.replace(/\D/g, "").slice(0, 8);
    if (inputEl.value.length === 8 && validarDniPeru(inputEl.value)) {
      // Placeholder para zW-07b: RENIEC -> nombre/apellidos.
    }
  });
}

// --- Uppercase en tiempo real preservando cursor ---
function setupUppercaseInput(inputEl) {
  if (!inputEl) return;
  inputEl.addEventListener("input", () => {
    const pos = inputEl.selectionStart;
    inputEl.value = inputEl.value.toUpperCase();
    inputEl.setSelectionRange(pos, pos);
  });
}

// --- Aplica uppercase a todos los campos relevantes del modal + sub-modal ---
function aplicarUppercaseGlobal() {
  const ids = [
    "tp-nombre", "tp-direccion", "tp-localidad",
    "vh-vehiculo", "vh-placa", "vh-nombre", "vh-apellidos", "vh-licencia"
  ];
  ids.forEach((id) => setupUppercaseInput(document.getElementById(id)));
}

// --- Render tabla de vehiculos en el modal padre ---
function renderizarTablaVehiculos() {
  const tbody = document.querySelector("#tabla-vehiculos tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  const vivos = window.transportistaState.vehiculos.filter((v) => !v._eliminado);
  vivos.forEach((v, idx) => {
    const tr = document.createElement("tr");
    tr.dataset.index = v._vehiculoIndex;
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${escaparHtml(v.vehiculo || "")}</td>
      <td>${escaparHtml(v.placa || "")}</td>
      <td>${escaparHtml(v.dni_chofer || "")}</td>
      <td>${escaparHtml(((v.nombre_chofer || "") + " " + (v.apellidos_chofer || "")).trim())}</td>
      <td>${escaparHtml(v.licencia || "")}</td>
    `;
    tr.addEventListener("click", () => {
      document.querySelectorAll("#tabla-vehiculos tbody tr").forEach((r) => r.classList.remove("row-selected"));
      tr.classList.add("row-selected");
      window.transportistaState.vehiculoSeleccionado = parseInt(tr.dataset.index, 10);
    });
    tr.addEventListener("dblclick", () => {
      window.transportistaState.vehiculoSeleccionado = parseInt(tr.dataset.index, 10);
      abrirSubmodalVehiculo(window.transportistaState.vehiculoSeleccionado);
    });
    tbody.appendChild(tr);
  });
}

function escaparHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// --- Abrir sub-modal con datos (null = nuevo) ---
function abrirSubmodalVehiculo(indexExistente) {
  const submodal = document.getElementById("submodal-vehiculo");
  if (!submodal) return;
  submodal.style.display = "flex";

  const vh =
    indexExistente !== null && indexExistente !== undefined
      ? window.transportistaState.vehiculos[indexExistente]
      : null;

  document.getElementById("vh-vehiculo").value = vh ? vh.vehiculo || "" : "";
  document.getElementById("vh-placa").value = vh ? vh.placa || "" : "";
  document.getElementById("vh-dni").value = vh ? vh.dni_chofer || "" : "";
  document.getElementById("vh-nombre").value = vh ? vh.nombre_chofer || "" : "";
  document.getElementById("vh-apellidos").value = vh ? vh.apellidos_chofer || "" : "";
  document.getElementById("vh-licencia").value = vh ? vh.licencia || "" : "";
  document.getElementById("vh-nota").value = vh ? vh.nota || "" : "";
  document.getElementById("vh-estado").checked = vh ? vh.estado !== false : true;

  submodal.dataset.editIndex = indexExistente === null || indexExistente === undefined ? "" : String(indexExistente);
  setupDniHook(document.getElementById("vh-dni"));
  aplicarUppercaseGlobal();
}

function editarVehiculoSeleccionado() {
  const idx = window.transportistaState.vehiculoSeleccionado;
  if (idx === null || idx === undefined) {
    mostrarToast("Selecciona un vehiculo primero", "warning");
    return;
  }
  abrirSubmodalVehiculo(idx);
}

function cerrarSubmodalVehiculo() {
  const s = document.getElementById("submodal-vehiculo");
  if (s) s.style.display = "none";
}

function aceptarSubmodalVehiculo() {
  const submodal = document.getElementById("submodal-vehiculo");
  const editIndex = submodal.dataset.editIndex;

  // Recopilar datos con uppercase (excepto nota)
  const datos = {
    vehiculo: document.getElementById("vh-vehiculo").value.trim().toUpperCase(),
    placa: document.getElementById("vh-placa").value.trim().toUpperCase(),
    dni_chofer: document.getElementById("vh-dni").value.trim() || null,
    nombre_chofer: document.getElementById("vh-nombre").value.trim().toUpperCase() || null,
    apellidos_chofer: document.getElementById("vh-apellidos").value.trim().toUpperCase() || null,
    licencia: document.getElementById("vh-licencia").value.trim().toUpperCase() || null,
    nota: document.getElementById("vh-nota").value.trim() || null,
    estado: document.getElementById("vh-estado").checked,
    _eliminado: false
  };

  if (!datos.vehiculo || !datos.placa) {
    mostrarToast("Vehiculo y Placa son obligatorios", "warning");
    return;
  }
  if (datos.dni_chofer && !validarDniPeru(datos.dni_chofer)) {
    mostrarToast("DNI debe tener 8 digitos", "warning");
    return;
  }

  // Si hay chofer (DNI, nombre o apellidos), la licencia es obligatoria
  const tieneChofer = !!(datos.dni_chofer || datos.nombre_chofer || datos.apellidos_chofer);
  if (tieneChofer && !datos.licencia) {
    mostrarToast("Si hay chofer, la licencia es obligatoria", "warning");
    return;
  }

  if (editIndex === "" || editIndex === undefined) {
    // Nuevo
    datos.id_vehiculo = null;
    datos._vehiculoIndex = window.transportistaState.vehiculos.length;
    window.transportistaState.vehiculos.push(datos);
  } else {
    // Editar: reemplazar el objeto completo preservando id y _vehiculoIndex
    const idx = parseInt(editIndex, 10);
    const existente = window.transportistaState.vehiculos[idx];
    datos.id_vehiculo = existente.id_vehiculo;
    datos._vehiculoIndex = existente._vehiculoIndex;
    window.transportistaState.vehiculos[idx] = datos;
  }

  renderizarTablaVehiculos();
  cerrarSubmodalVehiculo();
}

function quitarVehiculoSeleccionado() {
  const idx = window.transportistaState.vehiculoSeleccionado;
  if (idx === null || idx === undefined) {
    mostrarToast("Selecciona un vehiculo primero", "warning");
    return;
  }
  const v = window.transportistaState.vehiculos[idx];
  if (v.id_vehiculo === null || v.id_vehiculo === undefined) {
    window.transportistaState.vehiculos.splice(idx, 1);
    window.transportistaState.vehiculos.forEach((v2, i) => (v2._vehiculoIndex = i));
  } else {
    v._eliminado = true;
  }
  window.transportistaState.vehiculoSeleccionado = null;
  renderizarTablaVehiculos();
}

// --- Guardar Todo ---
async function guardarTodo() {
  const state = window.transportistaState;

  const payload = {
    id_transportista: state.id,
    ruc: document.getElementById("tp-ruc").value.trim(),
    nombre: document.getElementById("tp-nombre").value.trim(),
    direccion: document.getElementById("tp-direccion").value.trim() || null,
    localidad: document.getElementById("tp-localidad").value.trim() || null,
    celular: document.getElementById("tp-celular").value.trim() || null,
    correo: document.getElementById("tp-correo").value.trim() || null,
    estado: document.getElementById("tp-estado").checked,
    vehiculos: state.vehiculos.map((v) => ({
      id_vehiculo: v.id_vehiculo,
      vehiculo: v.vehiculo,
      placa: v.placa,
      dni_chofer: v.dni_chofer,
      nombre_chofer: v.nombre_chofer,
      apellidos_chofer: v.apellidos_chofer,
      licencia: v.licencia,
      nota: v.nota,
      estado: v.estado,
      _eliminado: !!v._eliminado
    }))
  };

  if (!validarRucPeru(payload.ruc)) {
    mostrarToast("RUC invalido", "warning");
    return;
  }
  if (!payload.nombre) {
    mostrarToast("Razon Social / Nombre es obligatorio", "warning");
    return;
  }

  const btn = document.getElementById("btn-guardar-todo");
  btn.disabled = true;
  btn.textContent = "Guardando...";

  try {
    const resp = await fetch("/tablas/transportistas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      const msg = data.error || data.detail || ("HTTP " + resp.status);
      mostrarToast(typeof msg === "string" ? msg : "Error al guardar", "error");
      btn.disabled = false;
      btn.textContent = "Guardar Todo";
      return;
    }
    cerrarModal();
    window.location.href = "/tablas/transportistas";
  } catch (err) {
    mostrarToast("Error de red. Intenta nuevamente.", "error");
    btn.disabled = false;
    btn.textContent = "Guardar Todo";
  }
}

// --- Eliminar desde el listado ---
async function eliminarTransportista(id) {
  const ok = await mostrarConfirmacion(
    "¿Eliminar este transportista y todos sus vehiculos? Esta acción no se puede deshacer.",
    { titulo: "Eliminar transportista", tipo: "peligro", textoAceptar: "Eliminar" }
  );
  if (!ok) return;
  try {
    const resp = await fetch("/tablas/transportistas/" + id, { method: "DELETE" });
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {}
    if (!resp.ok || data.ok === false) {
      mostrarToast(data.error || data.detail || ("Error HTTP " + resp.status), "error");
      return;
    }
    const row = document.getElementById("row-transportista-" + id);
    if (row) row.remove();
  } catch (err) {
    mostrarToast("Error de red. Intenta nuevamente.", "error");
  }
}

// --- Init del modal (llamado inline al insertar el modal) ---
function initTransportistaModal() {
  const rucInput = document.getElementById("tp-ruc");
  const rucFeedback = document.getElementById("tp-ruc-feedback");
  if (rucInput && rucFeedback) setupRucValidation(rucInput, rucFeedback);
  renderizarTablaVehiculos();
  aplicarUppercaseGlobal();
}

// Fallback: si HTMX inyecta el modal, tambien init en afterSwap.
document.addEventListener("htmx:afterSwap", (e) => {
  if (e.target && e.target.id === "modal-root") {
    initTransportistaModal();
  }
});
