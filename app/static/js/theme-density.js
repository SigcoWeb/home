/**
 * SigcoWeb · Theme + Density switcher (zWalter-18)
 * Persistencia en localStorage. Aplica el tema antes del DOMContentLoaded
 * para evitar flash de tema incorrecto.
 */

function setTheme(name) {
  document.documentElement.setAttribute('data-theme', name);
  document.querySelectorAll('.theme-btn').forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.theme === name);
  });
  try { localStorage.setItem('sigco-theme', name); } catch (e) {}
}

function setDensity(name) {
  document.documentElement.setAttribute('data-density', name);
  try { localStorage.setItem('sigco-density', name); } catch (e) {}
}

(function initSigcoTheme() {
  var theme = 'sigco';
  var density = 'comfortable';
  try {
    theme = localStorage.getItem('sigco-theme') || 'sigco';
    density = localStorage.getItem('sigco-density') || 'comfortable';
  } catch (e) {}
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.setAttribute('data-density', density);

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.theme-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.theme === theme);
    });
    var sel = document.getElementById('density-select');
    if (sel) sel.value = density;
  });
})();

window.setTheme = setTheme;
window.setDensity = setDensity;
