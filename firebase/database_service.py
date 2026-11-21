import os
import json
import uuid
import threading
import logging
from datetime import datetime, timezone
from pathlib import Path
from backend.config import Config
from firebase.firebase_config import get_firebase_manager

logger = logging.getLogger("SmartFitness.DatabaseService")

class LocalFirestoreEngine:
    """
    Thread-safe, high-fidelity local Firestore engine that emulates
    collections, documents, queries, and atomic persistence in JSON.
    Guarantees seamless zero-config operation during college vivas/evaluations.
    """
    def __init__(self, db_file_path=None):
        if db_file_path is None:
            self.db_path = Config.LOCAL_DB_PATH
        else:
            self.db_path = Path(db_file_path)
            
        self.lock = threading.Lock()
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            initial_data = {
                "Users": {},
                "HealthRecords": {},
                "Analytics": {},
                "Alerts": {},
                "EmergencyContacts": {}
            }
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading local firestore db: {e}")
            return {
                "Users": {},
                "HealthRecords": {},
                "Analytics": {},
                "Alerts": {},
                "EmergencyContacts": {}
            }

    def _write_data(self, data):
        try:
            temp_path = self.db_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(self.db_path)
        except Exception as e:
            logger.error(f"Error writing to local firestore db: {e}")

    # Generic Collection Operations
    def insert(self, collection_name, doc_id, doc_data):
        with self.lock:
            data = self._read_data()
            if collection_name not in data:
                data[collection_name] = {}
            data[collection_name][doc_id] = doc_data
            self._write_data(data)
            return doc_data

    def get(self, collection_name, doc_id):
        with self.lock:
            data = self._read_data()
            return data.get(collection_name, {}).get(doc_id)

    def update(self, collection_name, doc_id, updates):
        with self.lock:
            data = self._read_data()
            if collection_name in data and doc_id in data[collection_name]:
                data[collection_name][doc_id].update(updates)
                self._write_data(data)
                return data[collection_name][doc_id]
            return None

    def delete(self, collection_name, doc_id):
        with self.lock:
            data = self._read_data()
            if collection_name in data and doc_id in data[collection_name]:
                deleted = data[collection_name].pop(doc_id)
                self._write_data(data)
                return deleted
            return None

    def query(self, collection_name, filters=None, sort_by=None, reverse=False, limit=None):
        with self.lock:
            data = self._read_data()
            coll = data.get(collection_name, {})
            results = list(coll.values())

            if filters:
                for k, v in filters.items():
                    results = [item for item in results if item.get(k) == v]

            if sort_by:
                results.sort(key=lambda x: str(x.get(sort_by, "")), reverse=reverse)

            if limit:
                results = results[:limit]

            return results


class DatabaseService:
    """
    Unified Database Abstraction Layer.
    Dispatches to Cloud Firestore or Local Engine based on configuration.
    """
    def __init__(self):
        self.fb_manager = get_firebase_manager(Config)
        self.is_cloud = self.fb_manager.is_cloud
        self.local_engine = LocalFirestoreEngine()

    # ================= USER OPERATIONS =================
    def create_user(self, user_dict):
        user_id = user_dict.get("user_id") or str(uuid.uuid4())
        user_dict["user_id"] = user_id
        if "created_at" not in user_dict:
            user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        if "step_goal" not in user_dict:
            user_dict["step_goal"] = 10000
        if "calorie_goal" not in user_dict:
            user_dict["calorie_goal"] = 2000
        if "sleep_goal" not in user_dict:
            user_dict["sleep_goal"] = 8.0
        if "role" not in user_dict:
            user_dict["role"] = "user"

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("Users").document(user_id).set(user_dict)
                return user_dict
            except Exception as e:
                logger.error(f"Cloud Firestore create_user failed: {e}")

        return self.local_engine.insert("Users", user_id, user_dict)

    def get_user_by_id(self, user_id):
        if not user_id:
            return None
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                doc = db.collection("Users").document(user_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Cloud Firestore get_user_by_id failed: {e}")

        return self.local_engine.get("Users", user_id)

    def get_user_by_email(self, email):
        if not email:
            return None
        email_clean = email.strip().lower()

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                docs = db.collection("Users").where("email", "==", email_clean).limit(1).get()
                for doc in docs:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Cloud Firestore get_user_by_email failed: {e}")

        results = self.local_engine.query("Users", filters={"email": email_clean})
        return results[0] if results else None

    def update_user(self, user_id, update_fields):
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("Users").document(user_id).update(update_fields)
                return self.get_user_by_id(user_id)
            except Exception as e:
                logger.error(f"Cloud Firestore update_user failed: {e}")

        return self.local_engine.update("Users", user_id, update_fields)

    def list_all_users(self):
        """Admin only listing"""
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                docs = db.collection("Users").get()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Cloud Firestore list_all_users failed: {e}")

        return self.local_engine.query("Users", sort_by="created_at", reverse=True)

    # ================= HEALTH RECORDS OPERATIONS =================
    def add_health_record(self, record_data):
        record_id = record_data.get("record_id") or str(uuid.uuid4())
        record_data["record_id"] = record_id
        if "timestamp" not in record_data:
            record_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        if "data_source" not in record_data:
            record_data["data_source"] = "sensor"

        # Auto-compute distance in km if steps provided & distance missing
        if record_data.get("steps") is not None and not record_data.get("distance"):
            # approx 0.00078 km per step for an average adult
            record_data["distance"] = round(float(record_data["steps"]) * 0.00078, 2)

        # Auto-estimate calories if missing: roughly 0.045 kcal per step + resting
        if record_data.get("calories") is None and record_data.get("steps") is not None:
            record_data["calories"] = round(float(record_data["steps"]) * 0.045, 1)

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("HealthRecords").document(record_id).set(record_data)
                return record_data
            except Exception as e:
                logger.error(f"Cloud Firestore add_health_record failed: {e}")

        return self.local_engine.insert("HealthRecords", record_id, record_data)

    def get_health_records(self, user_id, limit=50, sort_desc=True):
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                query = db.collection("HealthRecords").where("user_id", "==", user_id)
                query = query.order_by("timestamp", direction=firestore.Query.DESCENDING if sort_desc else firestore.Query.ASCENDING)
                if limit:
                    query = query.limit(limit)
                docs = query.get()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Cloud Firestore get_health_records failed: {e}")

        return self.local_engine.query(
            "HealthRecords",
            filters={"user_id": user_id},
            sort_by="timestamp",
            reverse=sort_desc,
            limit=limit
        )

    def get_latest_health_record(self, user_id):
        records = self.get_health_records(user_id, limit=1, sort_desc=True)
        return records[0] if records else None

    # ================= ANALYTICS OPERATIONS =================
    def save_analytics(self, analytics_data):
        analysis_id = analytics_data.get("analysis_id") or str(uuid.uuid4())
        analytics_data["analysis_id"] = analysis_id
        if "timestamp" not in analytics_data:
            analytics_data["timestamp"] = datetime.now(timezone.utc).isoformat()

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("Analytics").document(analysis_id).set(analytics_data)
                return analytics_data
            except Exception as e:
                logger.error(f"Cloud Firestore save_analytics failed: {e}")

        return self.local_engine.insert("Analytics", analysis_id, analytics_data)

    def get_latest_analytics(self, user_id):
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                docs = db.collection("Analytics").where("user_id", "==", user_id)\
                         .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                         .limit(1).get()
                for doc in docs:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Cloud Firestore get_latest_analytics failed: {e}")

        results = self.local_engine.query(
            "Analytics",
            filters={"user_id": user_id},
            sort_by="timestamp",
            reverse=True,
            limit=1
        )
        return results[0] if results else None

    def get_analytics_history(self, user_id, limit=30):
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                docs = db.collection("Analytics").where("user_id", "==", user_id)\
                         .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                         .limit(limit).get()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Cloud Firestore get_analytics_history failed: {e}")

        return self.local_engine.query(
            "Analytics",
            filters={"user_id": user_id},
            sort_by="timestamp",
            reverse=True,
            limit=limit
        )

    # ================= ALERTS OPERATIONS =================
    def create_alert(self, alert_data):
        alert_id = alert_data.get("alert_id") or str(uuid.uuid4())
        alert_data["alert_id"] = alert_id
        if "timestamp" not in alert_data:
            alert_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        if "status" not in alert_data:
            alert_data["status"] = "active"
        if "severity" not in alert_data:
            alert_data["severity"] = "medium"

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("Alerts").document(alert_id).set(alert_data)
                return alert_data
            except Exception as e:
                logger.error(f"Cloud Firestore create_alert failed: {e}")

        return self.local_engine.insert("Alerts", alert_id, alert_data)

    def get_alerts(self, user_id=None, status=None, limit=50):
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if status:
            filters["status"] = status

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                query = db.collection("Alerts")
                for k, v in filters.items():
                    query = query.where(k, "==", v)
                query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
                if limit:
                    query = query.limit(limit)
                docs = query.get()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Cloud Firestore get_alerts failed: {e}")

        return self.local_engine.query(
            "Alerts",
            filters=filters,
            sort_by="timestamp",
            reverse=True,
            limit=limit
        )

    def update_alert_status(self, alert_id, new_status):
        updates = {
            "status": new_status,
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("Alerts").document(alert_id).update(updates)
                doc = db.collection("Alerts").document(alert_id).get()
                return doc.to_dict() if doc.exists else None
            except Exception as e:
                logger.error(f"Cloud Firestore update_alert_status failed: {e}")

        return self.local_engine.update("Alerts", alert_id, updates)

    # ================= EMERGENCY CONTACTS =================
    def add_emergency_contact(self, contact_data):
        contact_id = contact_data.get("contact_id") or str(uuid.uuid4())
        contact_data["contact_id"] = contact_id
        if "created_at" not in contact_data:
            contact_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if "is_primary" not in contact_data:
            contact_data["is_primary"] = False

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("EmergencyContacts").document(contact_id).set(contact_data)
                return contact_data
            except Exception as e:
                logger.error(f"Cloud Firestore add_emergency_contact failed: {e}")

        return self.local_engine.insert("EmergencyContacts", contact_id, contact_data)

    def get_emergency_contacts(self, user_id):
        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                docs = db.collection("EmergencyContacts").where("user_id", "==", user_id).get()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Cloud Firestore get_emergency_contacts failed: {e}")

        return self.local_engine.query("EmergencyContacts", filters={"user_id": user_id})

    def update_emergency_contact(self, contact_id, user_id, updates):
        # Ensure contact belongs to user
        contact = self.local_engine.get("EmergencyContacts", contact_id)
        if not contact or contact.get("user_id") != user_id:
            return None

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("EmergencyContacts").document(contact_id).update(updates)
                doc = db.collection("EmergencyContacts").document(contact_id).get()
                return doc.to_dict() if doc.exists else None
            except Exception as e:
                logger.error(f"Cloud Firestore update_emergency_contact failed: {e}")

        return self.local_engine.update("EmergencyContacts", contact_id, updates)

    def delete_emergency_contact(self, contact_id, user_id):
        contact = self.local_engine.get("EmergencyContacts", contact_id)
        if not contact or contact.get("user_id") != user_id:
            return False

        if self.is_cloud:
            try:
                db = self.fb_manager.get_firestore()
                db.collection("EmergencyContacts").document(contact_id).delete()
                return True
            except Exception as e:
                logger.error(f"Cloud Firestore delete_emergency_contact failed: {e}")

        return self.local_engine.delete("EmergencyContacts", contact_id) is not None

    # ================= AGGREGATE SYSTEM METRICS (FOR ADMIN) =================
    def get_aggregate_stats(self):
        all_users = self.list_all_users()
        all_records = self.local_engine.query("HealthRecords")
        all_alerts = self.local_engine.query("Alerts")

        active_alerts = [a for a in all_alerts if a.get("status") == "active"]
        critical_alerts = [a for a in all_alerts if a.get("severity") == "critical"]

        # Calculate averages safely
        avg_hr = 0
        hrs = [r.get("heart_rate") for r in all_records if r.get("heart_rate")]
        if hrs:
            avg_hr = round(sum(hrs) / len(hrs), 1)

        total_steps = sum(r.get("steps", 0) for r in all_records if r.get("steps"))

        return {
            "total_users": len(all_users),
            "total_records": len(all_records),
            "total_alerts": len(all_alerts),
            "active_alerts_count": len(active_alerts),
            "critical_alerts_count": len(critical_alerts),
            "avg_heart_rate": avg_hr,
            "total_system_steps": total_steps,
            "db_mode": "Google Cloud Firestore" if self.is_cloud else "Local Firestore Engine (Emulated)",
            "status": "Healthy"
        }


_db_service = None

def get_db_service():
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
