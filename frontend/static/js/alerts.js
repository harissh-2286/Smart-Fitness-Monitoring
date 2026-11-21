/**
 * Alerts Module: Health threshold triggers, resolution, and debounce visualization
 */

const AlertController = {
  async triggerAlert(type, message, severity = "medium", isTest = false) {
    try {
      const res = await fetch("/api/alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          alert_type: type,
          message: message,
          severity: severity,
          is_test: isTest
        })
      });
      return await res.json();
    } catch (err) {
      console.error("Alert trigger failed:", err);
      return null;
    }
  },

  async resolveAlert(alertId) {
    try {
      const res = await fetch(`/api/alerts/${alertId}/resolve`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" }
      });
      return await res.json();
    } catch (err) {
      console.error("Alert resolution failed:", err);
      return null;
    }
  },

  async fetchActiveAlerts() {
    try {
      const res = await fetch("/api/alerts?status=active");
      if (res.ok) {
        const data = await res.json();
        return data.alerts || [];
      }
    } catch (err) {
      console.error("Fetch alerts failed:", err);
    }
    return [];
  }
};

window.AlertController = AlertController;
