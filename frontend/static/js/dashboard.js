/**
 * Dashboard Controller: Real-time telemetry sync, goals updates, and ring animations
 */

class DashboardController {
  constructor() {
    this.refreshInterval = null;
  }

  init() {
    this.bindEvents();
    this.animateGauges();
  }

  bindEvents() {
    // Quick period selector
    const dateButtons = document.querySelectorAll(".date-range-selector");
    dateButtons.forEach(btn => {
      btn.addEventListener("click", (e) => {
        showToast("Telemetry Range", `Loaded data for ${e.target.dataset.range || 'selected period'}.`, "info");
      });
    });
  }

  animateGauges() {
    const stepsArc = document.getElementById("svgArcSteps");
    const caloriesArc = document.getElementById("svgArcCalories");
    const activeArc = document.getElementById("svgArcActive");

    if (stepsArc) stepsArc.style.transition = "stroke-dashoffset 1.2s ease-out";
    if (caloriesArc) caloriesArc.style.transition = "stroke-dashoffset 1.2s ease-out";
    if (activeArc) activeArc.style.transition = "stroke-dashoffset 1.2s ease-out";
  }

  async fetchLatestDashboardData() {
    try {
      const res = await fetch("/api/dashboard");
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.error("Dashboard sync error:", e);
    }
    return null;
  }
}

window.dashboardController = new DashboardController();
document.addEventListener("DOMContentLoaded", () => {
  window.dashboardController.init();
});
