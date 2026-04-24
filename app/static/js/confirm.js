/**
 * Modal de confirmacion reusable.
 * API: await window.mostrarConfirmacion(mensaje, opciones)
 *
 * opciones (todas opcionales):
 *   - titulo: string (default "Confirmar")
 *   - tipo: "peligro" | "advertencia" | "info" (default "peligro")
 *   - textoAceptar: string (default "Aceptar")
 *   - textoCancelar: string (default "Cancelar")
 *
 * Retorna Promise<boolean>: true si se acepta, false si se cancela.
 *
 * Uso:
 *   if (await mostrarConfirmacion("¿Eliminar este empleado?")) { ... }
 */
(function () {
  function mostrarConfirmacion(mensaje, opciones) {
    opciones = opciones || {};
    const titulo = opciones.titulo || 'Confirmar';
    const tipo = opciones.tipo || 'peligro';
    const textoAceptar = opciones.textoAceptar || 'Aceptar';
    const textoCancelar = opciones.textoCancelar || 'Cancelar';

    return new Promise((resolve) => {
      // Remover cualquier modal previo por seguridad
      const prev = document.getElementById('confirm-overlay');
      if (prev) prev.remove();

      const overlay = document.createElement('div');
      overlay.id = 'confirm-overlay';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');

      const box = document.createElement('div');
      box.className = 'confirm-box';

      const tituloEl = document.createElement('h3');
      tituloEl.className = 'confirm-titulo';
      tituloEl.textContent = titulo;

      const msgEl = document.createElement('p');
      msgEl.className = 'confirm-mensaje';
      msgEl.textContent = mensaje;

      const botones = document.createElement('div');
      botones.className = 'confirm-botones';

      const btnCancel = document.createElement('button');
      btnCancel.type = 'button';
      btnCancel.className = 'confirm-btn confirm-btn--cancel';
      btnCancel.textContent = textoCancelar;

      const btnAccept = document.createElement('button');
      btnAccept.type = 'button';
      btnAccept.className = 'confirm-btn confirm-btn--' + tipo;
      btnAccept.textContent = textoAceptar;

      botones.appendChild(btnCancel);
      botones.appendChild(btnAccept);
      box.appendChild(tituloEl);
      box.appendChild(msgEl);
      box.appendChild(botones);
      overlay.appendChild(box);
      document.body.appendChild(overlay);

      // Autofocus en Cancelar (mas seguro)
      setTimeout(() => btnCancel.focus(), 10);

      function cerrar(resultado) {
        overlay.classList.add('confirm-overlay--leaving');
        document.removeEventListener('keydown', onKey);
        setTimeout(() => {
          overlay.remove();
          resolve(resultado);
        }, 150);
      }

      function onKey(e) {
        if (e.key === 'Escape') {
          e.preventDefault();
          cerrar(false);
        } else if (e.key === 'Enter' && document.activeElement === btnAccept) {
          e.preventDefault();
          cerrar(true);
        } else if (e.key === 'Enter' && document.activeElement === btnCancel) {
          e.preventDefault();
          cerrar(false);
        }
      }

      btnCancel.addEventListener('click', () => cerrar(false));
      btnAccept.addEventListener('click', () => cerrar(true));
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) cerrar(false);
      });
      document.addEventListener('keydown', onKey);
    });
  }

  window.mostrarConfirmacion = mostrarConfirmacion;
})();

/**
 * Hook global: intercepta `htmx:confirm` cuando el elemento tiene
 * `data-confirmar="..."` y muestra el modal estilizado en lugar
 * del confirm() nativo que HTMX dispara con `hx-confirm`.
 *
 * Uso en templates:
 *   <button hx-delete="/path"
 *           data-confirmar="¿Eliminar este elemento?"
 *           data-confirmar-titulo="Eliminar"
 *           data-confirmar-aceptar="Eliminar"
 *           data-confirmar-tipo="peligro">Eliminar</button>
 *
 * Si el elemento no tiene data-confirmar, HTMX procede normalmente
 * (incluido hx-confirm legacy con confirm() nativo).
 */
document.addEventListener('htmx:confirm', function (evt) {
  const el = evt.detail && evt.detail.elt;
  if (!el || !el.hasAttribute || !el.hasAttribute('data-confirmar')) {
    return; // dejar que HTMX actue normal
  }

  // Prevenir el confirm() nativo de HTMX
  evt.preventDefault();

  const mensaje = el.getAttribute('data-confirmar') || '¿Confirmar accion?';
  const titulo = el.getAttribute('data-confirmar-titulo') || 'Confirmar';
  const textoAceptar = el.getAttribute('data-confirmar-aceptar') || 'Aceptar';
  const tipo = el.getAttribute('data-confirmar-tipo') || 'peligro';

  window.mostrarConfirmacion(mensaje, {
    titulo: titulo,
    tipo: tipo,
    textoAceptar: textoAceptar,
  }).then(function (ok) {
    if (ok) {
      // Continuar la accion HTMX original (saltando confirm nativo)
      evt.detail.issueRequest(true);
    }
    // Si cancela, no hacemos nada -> HTMX no envia la request.
  });
});
