/* ═══════════════════════════════════════════
   FinIA – JavaScript Global
   Sidebar, Toast, Data atual, helpers
   ═══════════════════════════════════════════ */

// ── DATA ATUAL ──
(function () {
  const el = document.getElementById("todayDate");
  if (el) {
    const now = new Date();
    el.textContent = now.toLocaleDateString("pt-BR", {
      day: "2-digit", month: "short", year: "numeric"
    });
  }
})();

// ── SIDEBAR MOBILE ──
const sidebar        = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const menuToggle     = document.getElementById("menuToggle");

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    sidebarOverlay.classList.toggle("open");
  });
}

if (sidebarOverlay) {
  sidebarOverlay.addEventListener("click", () => {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("open");
  });
}

// ── TOAST ──
/**
 * Exibe uma notificação toast
 * @param {string} message - Texto da mensagem
 * @param {"success"|"error"|"info"} type - Tipo do toast
 * @param {number} duration - Duração em ms (padrão 3500)
 */
function showToast(message, type = "info", duration = 3500) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const icons = {
    success: "fa-circle-check",
    error:   "fa-circle-xmark",
    info:    "fa-circle-info"
  };

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}"
       style="color:${type==="success"?"#34D399":type==="error"?"#FB7185":"#818CF8"}; font-size:16px; flex-shrink:0;"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  // Animar entrada
  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add("show"));
  });

  // Remover após duração
  setTimeout(() => {
    toast.classList.remove("show");
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

// ── HIGHLIGHT NAV ATIVO ──
(function () {
  const path  = window.location.pathname;
  const items = document.querySelectorAll(".nav-item");
  items.forEach(item => {
    if (item.getAttribute("href") === path) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });
})();

// ── FORMATAÇÃO DE MOEDA ──
function formatBRL(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency", currency: "BRL"
  }).format(value);
}

// ── DEBOUNCE (busca) ──
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
