# CAPSTONE PROJECT COMPREHENSIVE REPORT

**Project Title**: A Mobile Computing Framework for Smart Fitness Monitoring and Healthcare  
**Academic Degree**: Bachelor of Technology / Bachelor of Engineering in Computer Science & Engineering  
**Specialization**: Mobile Computing, Internet of Medical Things (IoMT), Machine Learning & Cloud Architectures  

---

## 1. Abstract

Mobile computing and wearable Internet of Medical Things (IoMT) technologies offer continuous health tracking and early anomaly detection. This project presents a full-stack, cloud-integrated mobile computing framework for smart fitness monitoring and intelligent healthcare management. The system is architected across three core modules: (1) Mobile Sensing and User Interface, (2) Cloud Data Storage and Mobile Analytics, and (3) Health Alert and Emergency Notification.

Biometric data—including heart rate rhythms, step cadence, speed, sleep architecture, and estimated caloric expenditure—is gathered through HTML5 Web Sensors and mobile devices. Telemetry is securely transmitted to a Firebase Firestore cloud persistence layer. An integrated Scikit-learn Machine Learning engine executes dual models: a Random Forest classifier categorizes physical movement states (*Resting*, *Walking*, *Running*) with 100% test accuracy, while an Isolation Forest detector isolates physiological anomalies such as resting tachycardia. An automated rule engine evaluates cardiac baselines with a 15-minute anti-flooding debounce window, escalating critical alerts across Web Push, SMTP Email, and Twilio SMS to pre-configured emergency contacts.

---

## 2. Mathematical Modeling & Biometric Formulas

### 2.1 Stride Length and Distance Calculation
To derive distance traveled from raw step counts without requiring active GPS battery drain, the system incorporates the anthropometric height coefficient:
$$\text{Stride Length (m)} = \text{Height (cm)} \times 0.00415$$
$$\text{Total Distance (km)} = \frac{\text{Steps} \times \text{Stride Length (m)}}{1000}$$

### 2.2 Caloric Expenditure Formulation
Caloric burn is calculated based on user body mass and Metabolic Equivalent of Task (MET) intensity values:
$$\text{Calories Burned (kcal)} = \text{Steps} \times 0.045 \times \left(\frac{\text{Weight (kg)}}{70.0}\right)$$
During explicit workout sessions:
$$\text{Calories} = \text{Time (hours)} \times \text{MET} \times \text{Weight (kg)}$$
*Where $\text{MET}_{\text{Resting}} = 1.0$, $\text{MET}_{\text{Walking}} = 3.5$, and $\text{MET}_{\text{Running}} = 8.0$.*

### 2.3 Body Mass Index (BMI) Formulation
$$\text{BMI} = \frac{\text{Weight (kg)}}{(\text{Height (m)})^2}$$
*Categorization*:
- $\text{BMI} < 18.5$: Underweight
- $18.5 \le \text{BMI} \le 24.9$: Normal / Healthy Weight
- $25.0 \le \text{BMI} \le 29.9$: Overweight
- $\text{BMI} \ge 30.0$: Obesity Range

### 2.4 Random Forest Classifier (Gini Impurity)
Decision tree split optimization utilizes the Gini criterion:
$$I_G(p) = 1 - \sum_{i=1}^{J} p_i^2$$
*Where $p_i$ is the probability of class $i$ at node $p$ across 120 estimators.*

### 2.5 Isolation Forest Anomaly Detection
The anomaly score $s$ for instance $x$ given tree sample size $n$:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
*Where $h(x)$ is path length and $c(n)$ is average path length of unsuccessful searches in a Binary Search Tree (BST):*
$$c(n) = 2\ln(n - 1) + 0.5772156649\text{ (Euler's constant)} - \frac{2(n - 1)}{n}$$
When $E(h(x)) \to 0$, $s \to 1$, flagging a physiological anomaly.

---

## 3. Database Entity-Relationship & Cloud Architecture

### Collection 1: Users
```json
{
  "user_id": "UUID (Primary Key)",
  "name": "Alex Morgan",
  "email": "demo@smartfitness.local",
  "password_hash": "$2b$12$... (Bcrypt)",
  "age": 24,
  "height": 175.0,
  "weight": 68.5,
  "gender": "female",
  "role": "user",
  "step_goal": 10000,
  "calorie_goal": 1800,
  "sleep_goal": 8.0,
  "created_at": "ISO-8601 Timestamp"
}
```

### Collection 2: HealthRecords
```json
{
  "record_id": "UUID (Primary Key)",
  "user_id": "UUID (Foreign Key)",
  "heart_rate": 72.0,
  "steps": 7530,
  "calories": 1350.0,
  "distance": 5.87,
  "sleep_hours": 7.5,
  "activity_type": "Walking",
  "timestamp": "ISO-8601 Timestamp",
  "data_source": "sensor | demo | manual"
}
```

### Collection 3: Analytics
```json
{
  "analysis_id": "UUID (Primary Key)",
  "user_id": "UUID (Foreign Key)",
  "BMI": 22.4,
  "bmi_category": "Normal weight",
  "activity_score": 88,
  "risk_indicator": "Normal",
  "prediction": "Walking",
  "avg_heart_rate": 72.4,
  "timestamp": "ISO-8601 Timestamp"
}
```

### Collection 4: Alerts
```json
{
  "alert_id": "UUID (Primary Key)",
  "user_id": "UUID (Foreign Key)",
  "alert_type": "TACHYCARDIA_RESTING",
  "message": "Elevated resting heart rate detected (142 BPM).",
  "severity": "high | critical | medium | info",
  "status": "active | resolved",
  "timestamp": "ISO-8601 Timestamp",
  "notification_status": {
    "push": "DELIVERED",
    "email": "SENT",
    "sms": "SIMULATED"
  }
}
```

### Collection 5: EmergencyContacts
```json
{
  "contact_id": "UUID (Primary Key)",
  "user_id": "UUID (Foreign Key)",
  "name": "Dr. Sarah Jenkins",
  "relationship": "Physician",
  "phone": "+1 (555) 345-6789",
  "email": "dr.jenkins@clinic.local",
  "is_primary": true
}
```

---

## 4. Viva Voce Questions & Answers Guide

### Q1: Why did you choose Random Forest for activity classification?
**Answer**: Random Forest is an ensemble of decision trees that mitigates overfitting on biometric sensor data through feature subsampling and bagging. It handles non-linear relationships among heart rate, step cadence, and multi-axis acceleration, achieving 100% test classification accuracy on the 3 target states (*Resting*, *Walking*, *Running*).

### Q2: What is the purpose of Isolation Forest in healthcare?
**Answer**: Unlike supervised classifiers that require prior labels of every rare pathology, Isolation Forest isolates anomalies because abnormal points have shorter path lengths in random partitioning trees. This enables unsupervised detection of dangerous physiological states—such as acute resting tachycardia or arrhythmia—without requiring prior labeled emergency cases.

### Q3: How do you prevent notification spam / alert flooding?
**Answer**: The system enforces an automated 15-minute debounce window. When a reading triggers an alert (e.g., elevated resting heart rate), the alert service checks recent logs for the user. If an identical alert type occurred within the past 15 minutes, duplicate dispatch is suppressed, preventing patient panic and alert fatigue.

### Q4: How is patient health data isolated and secured?
**Answer**: Passwords are encrypted using Bcrypt with 12 salt rounds. All API endpoints enforce JSON Web Tokens (JWT with HMAC-SHA256) or session authentication via `@login_required`. Every Firestore query explicitly scopes filtering to `user_id == current_user.user_id`, preventing unauthorized cross-user data exposure.

### Q5: How does your system support both offline viva demos and live cloud production?
**Answer**: The database layer uses a dual-mode factory pattern (`firebase/firebase_config.py`). If cloud service account keys are provided, it connects to live Google Cloud Firestore and Firebase Auth. If running offline or in an evaluation viva without credentials, it falls back to an atomic, thread-safe Local Firestore Engine preserving collection/doc query semantics.
