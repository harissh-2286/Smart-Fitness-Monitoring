/**
 * Notifications Module: Web Push integration, Sound cues, and In-app notifications
 */

class NotificationManager {
  constructor() {
    this.hasWebNotificationPermission = false;
    this.checkPermission();
  }

  checkPermission() {
    if ("Notification" in window) {
      this.hasWebNotificationPermission = Notification.permission === "granted";
    }
  }

  async requestPermission() {
    if ("Notification" in window) {
      const perm = await Notification.requestPermission();
      this.hasWebNotificationPermission = perm === "granted";
      if (this.hasWebNotificationPermission) {
        showToast("Notifications Enabled", "You will receive real-time health alerts.", "success");
      }
      return this.hasWebNotificationPermission;
    }
    return false;
  }

  dispatchNotification(title, body, severity = "info") {
    // 1. Always display Toast in browser
    showToast(title, body, severity === "critical" ? "critical" : (severity === "high" ? "warning" : "info"));

    // 2. If browser notification permission granted, trigger system notification
    if (this.hasWebNotificationPermission && "Notification" in window) {
      try {
        new Notification(title, {
          body: body,
          icon: "/static/images/logo.svg",
          tag: "smart-fitness-alert"
        });
      } catch (e) {
        console.warn("Browser notification error:", e);
      }
    }
  }
}

window.notificationManager = new NotificationManager();
