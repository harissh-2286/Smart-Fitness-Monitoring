/**
 * Mobile Sensing and Sensor Simulation Module
 * Integrates Web Sensor API (Accelerometer / DeviceMotion)
 * and provides realistic simulation presets with live ingestion.
 */

class MobileSensorManager {
  constructor() {
    this.isRealSensorActive = false;
    this.isSimulationRunning = false;
    this.simInterval = null;
    this.currentState = "Resting"; // Resting, Walking, Running
  }

  // 1. Check Browser Hardware Sensor Support
  checkHardwareSensorSupport() {
    return {
      deviceMotion: "DeviceMotionEvent" in window,
      genericSensor: "Accelerometer" in window
    };
  }

  // 2. Start Real Device Sensing (if supported by mobile browser)
  async startRealSensorTracking(onReadingCallback) {
    if (typeof DeviceMotionEvent !== "undefined" && typeof DeviceMotionEvent.requestPermission === "function") {
      try {
        const permission = await DeviceMotionEvent.requestPermission();
        if (permission !== "granted") {
          showToast("Sensor Notice", "Motion sensor access denied. Switching to Demo Simulation.", "warning");
          return false;
        }
      } catch (err) {
        console.warn("Motion permission error:", err);
      }
    }

    if ("ondevicemotion" in window) {
      window.addEventListener("devicemotion", (event) => {
        const acc = event.accelerationIncludingGravity || { x: 0, y: 9.8, z: 0 };
        const magnitude = Math.sqrt(acc.x * acc.x + acc.y * acc.y + acc.z * acc.z);
        if (onReadingCallback) {
          onReadingCallback({
            source: "hardware_sensor",
            accel_magnitude: parseFloat(magnitude.toFixed(2)),
            timestamp: new Date().toISOString()
          });
        }
      });
      this.isRealSensorActive = true;
      showToast("Sensor Active", "Connected to device motion hardware.", "success");
      return true;
    } else {
      showToast("Hardware Notice", "No hardware motion sensor on this device. Demo simulation available.", "info");
      return false;
    }
  }

  // 3. Preset Simulation Generator
  getPresetData(presetName) {
    switch (presetName) {
      case "Resting":
        return {
          activity_type: "Resting",
          heart_rate: Math.floor(62 + Math.random() * 12),
          steps: 0,
          step_cadence: 0,
          accel_magnitude: parseFloat((9.8 + (Math.random() * 0.4 - 0.2)).toFixed(2)),
          speed_kmh: 0.0,
          data_source: "demo"
        };
      case "Walking":
        return {
          activity_type: "Walking",
          heart_rate: Math.floor(95 + Math.random() * 18),
          steps: Math.floor(80 + Math.random() * 30),
          step_cadence: Math.floor(90 + Math.random() * 15),
          accel_magnitude: parseFloat((12.5 + (Math.random() * 2 - 1)).toFixed(2)),
          speed_kmh: parseFloat((4.5 + (Math.random() * 0.8 - 0.4)).toFixed(1)),
          data_source: "demo"
        };
      case "Running":
        return {
          activity_type: "Running",
          heart_rate: Math.floor(145 + Math.random() * 25),
          steps: Math.floor(150 + Math.random() * 40),
          step_cadence: Math.floor(160 + Math.random() * 15),
          accel_magnitude: parseFloat((19.5 + (Math.random() * 4 - 2)).toFixed(2)),
          speed_kmh: parseFloat((10.5 + (Math.random() * 2 - 1)).toFixed(1)),
          data_source: "demo"
        };
      case "Anomaly_Spike":
        return {
          activity_type: "Resting",
          heart_rate: Math.floor(172 + Math.random() * 12), // Resting tachycardia anomaly!
          steps: 0,
          step_cadence: 0,
          accel_magnitude: 9.81,
          speed_kmh: 0.0,
          data_source: "demo"
        };
      default:
        return this.getPresetData("Resting");
    }
  }

  // 4. Send Reading to Backend API
  async transmitReading(readingPayload) {
    try {
      const response = await fetch("/api/health-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(readingPayload)
      });
      const res = await response.json();
      
      if (response.ok) {
        if (res.alerts_triggered && res.alerts_triggered.length > 0) {
          res.alerts_triggered.forEach((alt) => {
            showToast(
              `Alert: ${alt.alert_type.replace('_', ' ')}`,
              alt.message,
              alt.severity === "critical" ? "critical" : "warning"
            );
          });
        }
        return res;
      } else {
        showToast("Transmission Error", res.error || "Failed to record health reading", "danger");
      }
    } catch (err) {
      console.error("Transmission network error:", err);
    }
    return null;
  }
}

window.mobileSensorManager = new MobileSensorManager();
