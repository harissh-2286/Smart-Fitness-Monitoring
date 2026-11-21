# A Mobile Computing Framework for Smart Fitness Monitoring and Healthcare

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Backend-Flask%20REST%20API-teal.svg)](https://flask.palletsprojects.com/)
[![Firebase Firestore](https://img.shields.io/badge/Database-Firebase%20Firestore-orange.svg)](https://firebase.google.com/)
[![Scikit-Learn ML](https://img.shields.io/badge/Machine%20Learning-Random%20Forest%20%7C%20Isolation%20Forest-green.svg)](https://scikit-learn.org/)
[![UI Style](https://img.shields.io/badge/Design-Apple%20Health%20Minimalist-0284c7.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing-brightgreen.svg)](testing/)

A full-stack, enterprise-grade, mobile-responsive Internet of Medical Things (IoMT) and healthcare computing platform developed for academic capstone demonstration.

---

## 1. Project Overview & Architecture

The framework monitors physiological wellness, archives telemetry in Firebase Firestore, executes dual-engine Scikit-learn Machine Learning (activity recognition and physiological anomaly detection), and coordinates multi-channel emergency escalations (Push, SMTP Email, and Twilio SMS).

```
                      +------------------------------------------------+
                      |       USER INTERFACE & MOBILE SENSING          |
                      |  - HTML5 DeviceMotion / Web Sensor API         |
                      |  - Apple Health-style Concentric Rings & Cards |
                      |  - Interactive Simulation Playground           |
                      +-----------------------+------------------------+
                                              | HTTPS / JSON
                                              v
                      +------------------------------------------------+
                      |         PYTHON FLASK REST API BACKEND          |
                      |  - JWT & Session Authentication (Bcrypt)       |
                      |  - User Data Isolation (RBAC)                  |
                      |  - Biometric Transformation (Stride / MET)     |
                      +-----------+------------------------+-----------+
                                  |                        |
          +-----------------------v-------+        +-------v-----------------------+
          |    FIREBASE FIRESTORE CLOUD   |        |   SCIKIT-LEARN ML ENGINE      |
          |  - Dual Mode (Cloud / Local)  |        |  - Random Forest Classifier   |
          |  - Users & HealthRecords      |        |  - Isolation Forest Anomaly   |
          |  - Analytics & Alert Audits   |        |  - StandardScaler Pipeline    |
          +-----------------------+-------+        +-------+-----------------------+
                                  |                        |
                                  +-----------+------------+
                                              |
                                              v
                      +------------------------------------------------+
                      |     HEALTH ALERT & NOTIFICATION ENGINE         |
                      |  - 15-Minute Intelligent Duplicate Debounce    |
                      |  - Web Push / FCM In-App Alerts                |
                      |  - SMTP Email Service                          |
                      |  - Twilio SMS Emergency Protocol               |
                      +------------------------------------------------+
```

---

## 2. The Three Core Modules

### Module 1: Mobile Sensing and User Interface
- **Cardiovascular Rhythm**: Continuous heart rate monitoring (BPM), minimum/maximum ranges, resting baseline, and 4 physiological zones (*Rest*, *Fat Burn*, *Cardio*, *Peak*).
- **Physical Mobility Tracking**: Daily steps, automated distance calculation based on user height stride ($Stride = Height \times 0.415$), caloric expenditure estimation ($MET \times Weight$).
- **Circadian Sleep Architecture**: Nocturnal sleep duration, sleep quality index, and stage distribution (*Deep*, *REM*, *Light*, *Awake*).
- **Dual-Mode Telemetry Generator**: Connects to live browser motion sensors (`DeviceMotionEvent`) with immediate fallback to physiologically calibrated simulation presets (*Resting*, *Walking*, *Running*, *Anomaly Spike*).

### Module 2: Cloud Data Storage and Mobile Analytics
- **Firebase Firestore Persistence**: Collections structured for `Users`, `HealthRecords`, `Analytics`, `Alerts`, and `EmergencyContacts`.
- **Zero-Setup Dual Engine**: Operates seamlessly with live Google Cloud Firestore credentials or via the built-in, thread-safe Local Firestore Engine for zero-dependency offline college presentations.
- **Biometric Analytics**: Body Mass Index ($BMI = Weight / Height^2$) with standard classification scales and clinical screening disclaimers; multi-factor activity score ($0-100$).

### Module 3: Health Alert & Emergency Notification
- **Intelligent Threshold Evaluation**: Automatically flags resting tachycardia ($>115\text{ BPM}$ resting), bradycardia ($<48\text{ BPM}$), peak overexertion ($>185\text{ BPM}$), and chronic sleep deficits ($<5\text{ hrs}$).
- **Automated Anti-Flooding Debounce**: Prevents alert fatigue by debouncing duplicate alerts within a 15-minute window.
- **Emergency Escalation Protocol**: Escalates critical alerts simultaneously to registered emergency contacts (physicians, family) via simulated or live SMTP Email and Twilio SMS.

---

## 3. Machine Learning Architecture

Two independent, serialized Scikit-learn models run inside `backend/services/analytics_service.py`:

```
Input Vector: [Heart Rate (BPM), Cadence (steps/min), Accel Magnitude (m/s²), Speed (km/h)]
                                    |
                                    v
                     +------------------------------+
                     | StandardScaler Preprocessing |
                     +--------------+---------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------------+             +-------------------------------+
|   Random Forest Classifier  |             |   Isolation Forest Detector   |
|   - 120 Estimators          |             |   - Contamination: 0.04       |
|   - Output: Class & Conf %  |             |   - Output: Anomaly Score     |
|   [Resting, Walking, Run]   |             |   [Normal, Low, Mod, High Risk|
+-----------------------------+             +-------------------------------+
```

### Model Performance Metrics (Evaluated on Test Partition)
- **Accuracy**: $100.00\%$
- **Weighted Precision**: $1.000$
- **Weighted Recall**: $1.000$
- **Weighted F1-Score**: $1.000$
- **Classes**: `Resting`, `Walking`, `Running`

> **Clinical Disclaimer**: Machine learning outputs represent experimental wellness indicators designed for mobile computing capstone demonstration and are not intended as clinical diagnostic tools.

---

## 4. Application Pages (12 Complete Pages)

| Page | Route | Description |
|---|---|---|
| **Landing Page** | `/` | Hero section, project scope, architecture overview, and telemetry preview. |
| **Login Page** | `/login` | Authentication form with quick one-click evaluator login buttons. |
| **Registration Page** | `/register` | Account onboarding with biometric metrics (age, height, weight). |
| **Main Dashboard** | `/dashboard` | Apple Health-style rainbow arcs, 4 stat cards, 7-day move chart, and sensor simulation controls. |
| **Heart Rate** | `/heart-rate` | Real-time animated pulse, 24-hr area chart, heart rate zones, and manual HR logging. |
| **Activity Tracking**| `/activity` | Daily step progress, weekly volume bars, distance in km, and real-time ML state display. |
| **Sleep Monitoring** | `/sleep` | Sleep duration vs 8.0 hr goal, sleep quality index, and hypnogram doughnut breakdown. |
| **Health Analytics** | `/analytics` | BMI screening gauge, activity score, ML evaluation metrics, and live inference playground. |
| **Health Alerts** | `/alerts` | Severity-filtered alerts table, notification status, and one-click alert resolution. |
| **Emergency Contacts**| `/emergency-contacts`| CRUD contacts, primary contact toggle, and simulated emergency dispatch test. |
| **User Profile** | `/profile` | Biometric profile settings, fitness targets, and JSON data export. |
| **Admin Dashboard** | `/admin` | Restricted panel: user directory, aggregate system health, and audit logs. |

---

## 5. Pre-Configured Demonstration Accounts

To ensure zero friction during college project vivas and presentations, the database auto-seeds these accounts on first run:

| Account Type | Email Address | Password | Permissions |
|---|---|---|---|
| **Demo User** | `demo@smartfitness.local` | `Demo@123456` | Full Health Dashboard & Telemetry |
| **Administrator** | `admin@smartfitness.local` | `Admin@123456` | Restricted Admin Monitoring Panel |

---

## 6. Installation & Execution Guide

### Step 1: Clone or Open Workspace
```bash
cd "c:\Users\haris\OneDrive\Desktop\Smart Fitness Monitoring"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Train / Verify Machine Learning Models
```bash
python machine_learning/train.py
```

### Step 4: Run Automated Test Suite
```bash
python -m pytest testing/ -v
```

### Step 5: Start the Web Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 7. Firebase Cloud Firestore Configuration (Optional)

By default, the platform runs in **`FIREBASE_MODE=emulated`**, storing data in `firebase/local_firestore_db.json`. 

To connect to a live Google Cloud Firebase project:
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a project and enable **Firestore Database** and **Firebase Authentication**.
3. Go to **Project Settings > Service Accounts** and generate a new private key.
4. Save the downloaded JSON file as `firebase/serviceAccountKey.json`.
5. In `.env`, change:
   ```env
   FIREBASE_MODE=cloud
   FIREBASE_SERVICE_ACCOUNT_KEY=firebase/serviceAccountKey.json
   FIREBASE_PROJECT_ID=your-firebase-project-id
   ```
6. Restart `python run.py`. The system will automatically connect to live Google Cloud Firestore!

---

## 8. REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/register` | Register a new user | No |
| `POST` | `/api/login` | Authenticate and obtain JWT token | No |
| `POST` | `/api/logout` | Terminate session | Yes |
| `GET` | `/api/profile` | Retrieve user profile & goals | Yes |
| `PUT` | `/api/profile` | Update profile metrics and targets | Yes |
| `POST` | `/api/health-data` | Ingest biometric telemetry record | Yes |
| `GET` | `/api/health-data` | Query historical health records | Yes |
| `GET` | `/api/dashboard` | Aggregated daily & weekly summary | Yes |
| `GET` | `/api/analytics` | Compute BMI and activity scores | Yes |
| `POST` | `/api/predict` | Scikit-learn inference on reading | Yes |
| `GET` | `/api/predictions` | History of ML predictions | Yes |
| `POST` | `/api/alerts` | Generate health alert | Yes |
| `GET` | `/api/alerts` | Query user alerts | Yes |
| `PUT` | `/api/alerts/<id>/resolve` | Resolve an active alert | Yes |
| `GET` | `/api/emergency-contacts`| List emergency contacts | Yes |
| `POST` | `/api/emergency-contacts`| Create emergency contact | Yes |
| `DELETE`| `/api/emergency-contacts/<id>`| Delete contact | Yes |
| `POST` | `/api/emergency-contacts/test`| Fire test emergency dispatch | Yes |
| `GET` | `/api/admin/overview` | Platform health & aggregate metrics | Admin Only |

---

## 9. Academic Viva Presentation Tips

When presenting this project to your guide or external examiner:

1. **Architecture Walkthrough**: Highlight the three distinct modules: Mobile Sensing $\rightarrow$ Cloud Analytics $\rightarrow$ Emergency Escalation.
2. **Apple Health Aesthetics**: Show the dashboard on mobile and desktop, showing the concentric activity arcs and 7-day Move chart.
3. **Hardware vs Simulation**: Demonstrate the Web Sensor API integration and use the simulator banner to inject *Resting*, *Walking*, *Running*, and *Anomaly Spike* readings in real-time.
4. **Machine Learning Viva Points**: Open the `/analytics` page to display the confusion matrix, explain the Random Forest hyperparameters, and show the live prediction playground.
5. **Safety Protocol**: Trigger an emergency dispatch test on `/emergency-contacts` to demonstrate multi-channel escalation with the 15-minute duplicate debounce rule.
