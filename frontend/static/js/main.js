/**
 * Main Application Script: Theme, Sidebar, Notifications, Utility Helpers
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSidebar();
  initToastContainer();
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem("smart_fitness_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  const themeToggleBtn = document.getElementById("themeToggleBtn");
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const nextTheme = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      localStorage.setItem("smart_fitness_theme", nextTheme);
      updateThemeIcon(nextTheme);
    });
  }
}

function updateThemeIcon(theme) {
  const icon = document.getElementById("themeToggleIcon");
  if (icon) {
    if (theme === "dark") {
      icon.className = "bi bi-sun-fill text-warning";
    } else {
      icon.className = "bi bi-moon-stars-fill text-secondary";
    }
  }
}

// Mobile Sidebar Toggle
function initSidebar() {
  const sidebarToggle = document.getElementById("sidebarToggleBtn");
  const sidebar = document.querySelector(".sidebar");
  const sidebarOverlay = document.getElementById("sidebarOverlay");

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("show");
      if (sidebarOverlay) sidebarOverlay.classList.toggle("show");
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", () => {
      sidebar.classList.remove("show");
      sidebarOverlay.classList.remove("show");
    });
  }
}

// Global Toast Notifications
function initToastContainer() {
  if (!document.getElementById("toastNotificationContainer")) {
    const container = document.createElement("div");
    container.id = "toastNotificationContainer";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    container.style.zIndex = "2000";
    document.body.appendChild(container);
  }
}

function showToast(title, message, type = "info") {
  const container = document.getElementById("toastNotificationContainer");
  if (!container) return;

  const toastId = "toast_" + Date.now();
  let bgClass = "bg-primary text-white";
  let icon = "bi-info-circle-fill";

  if (type === "success") {
    bgClass = "bg-success text-white";
    icon = "bi-check-circle-fill";
  } else if (type === "danger" || type === "critical") {
    bgClass = "bg-danger text-white";
    icon = "bi-exclamation-triangle-fill";
  } else if (type === "warning") {
    bgClass = "bg-warning text-dark";
    icon = "bi-exclamation-circle-fill";
  }

  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${icon} fs-5"></i>
          <div>
            <strong>${title}</strong><br>
            <small>${message}</small>
          </div>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML("beforeend", toastHtml);
  const toastElem = document.getElementById(toastId);
  if (window.bootstrap && bootstrap.Toast) {
    const bsToast = new bootstrap.Toast(toastElem, { delay: 5000 });
    bsToast.show();
    toastElem.addEventListener("hidden.bs.toast", () => toastElem.remove());
  }
}
