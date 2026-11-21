/**
 * Chart.js Visualization Configurations
 * Builds responsive, sleek health graphs matching Apple Health aesthetics.
 */

const FitnessCharts = {
  // 1. Smooth Heart Rate Area Chart with Zone Gradients
  renderHeartRateChart(canvasId, timestamps, heartRates) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const chartCtx = ctx.getContext("2d");
    const gradient = chartCtx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(225, 29, 72, 0.45)");
    gradient.addColorStop(0.5, "rgba(244, 63, 94, 0.15)");
    gradient.addColorStop(1, "rgba(244, 63, 94, 0.0)");

    return new Chart(ctx, {
      type: "line",
      data: {
        labels: timestamps,
        datasets: [{
          label: "Heart Rate (BPM)",
          data: heartRates,
          borderColor: "#e11d48",
          borderWidth: 2.5,
          backgroundColor: gradient,
          fill: true,
          tension: 0.38,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#e11d48"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0f172a",
            titleFont: { size: 12, weight: "bold" },
            bodyFont: { size: 13 },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (item) => ` ${item.raw} BPM`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 7, font: { size: 11 }, color: "#94a3b8" }
          },
          y: {
            min: 40,
            max: 200,
            grid: { color: "rgba(148, 163, 184, 0.15)", borderDash: [4, 4] },
            ticks: { stepSize: 30, font: { size: 11 }, color: "#94a3b8" }
          }
        }
      }
    });
  },

  // 2. Weekly Move / Calorie Burn Bar Chart
  renderMoveWeeklyChart(canvasId, daysLabels, caloriesValues, avgCal) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: daysLabels,
        datasets: [{
          label: "Calories Burned (kcal)",
          data: caloriesValues,
          backgroundColor: caloriesValues.map(v => v >= avgCal ? "#ea580c" : "#fed7aa"),
          borderRadius: 6,
          barThickness: 16
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (item) => ` ${item.raw} kcal`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: "#94a3b8", font: { size: 11 } } },
          y: {
            grid: { color: "rgba(148, 163, 184, 0.12)" },
            ticks: { color: "#94a3b8", font: { size: 11 } }
          }
        }
      }
    });
  },

  // 3. Sleep Hypnogram & Stage Distribution Doughnut
  renderSleepStagesChart(canvasId, deepHours, remHours, lightHours, awakeHours) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Deep Sleep", "REM Sleep", "Light Sleep", "Awake"],
        datasets: [{
          data: [deepHours, remHours, lightHours, awakeHours],
          backgroundColor: ["#3b82f6", "#8b5cf6", "#06b6d4", "#f97316"],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "72%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { boxWidth: 12, padding: 14, font: { size: 11 }, color: "#64748b" }
          }
        }
      }
    });
  }
};

window.FitnessCharts = FitnessCharts;
