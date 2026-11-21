import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("SmartFitness.FirebaseConfig")

class FirebaseManager:
    """
    Manages connection to Google Firebase Cloud Firestore & Authentication.
    Provides graceful fallback to Local Emulated Engine when cloud credentials
    are not supplied or when working offline.
    """
    _instance = None
    _initialized = False

    def __init__(self, service_account_path=None, project_id=None, mode="emulated"):
        self.service_account_path = service_account_path
        self.project_id = project_id
        self.mode = mode
        self.firestore_client = None
        self.auth_client = None
        self.is_cloud = False
        self._initialize()

    def _initialize(self):
        if self.mode == "cloud":
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore, auth

                if not firebase_admin._apps:
                    if self.service_account_path and os.path.exists(self.service_account_path):
                        cred = credentials.Certificate(self.service_account_path)
                        firebase_admin.initialize_app(cred, {
                            'projectId': self.project_id
                        })
                        logger.info("Firebase Admin SDK initialized using service account certificate.")
                    else:
                        firebase_admin.initialize_app()
                        logger.info("Firebase Admin SDK initialized using default application credentials.")

                self.firestore_client = firestore.client()
                self.auth_client = auth
                self.is_cloud = True
                logger.info("Connected to live Google Cloud Firestore & Firebase Auth.")
                return
            except Exception as e:
                logger.warning(
                    f"Cloud Firebase initialization failed: {e}. "
                    "Falling back to high-fidelity Local Firestore Engine."
                )

        # Emulated Mode
        self.is_cloud = False
        logger.info("Running in Emulated Firestore Mode (local persistent JSON store).")

    def get_firestore(self):
        return self.firestore_client

    def get_auth(self):
        return self.auth_client


_firebase_manager = None

def get_firebase_manager(config=None):
    global _firebase_manager
    if _firebase_manager is None:
        mode = "emulated"
        service_account_path = None
        project_id = "smart-fitness-health-capstone"
        if config:
            mode = getattr(config, "FIREBASE_MODE", "emulated")
            service_account_path = getattr(config, "FIREBASE_SERVICE_ACCOUNT_KEY", None)
            project_id = getattr(config, "FIREBASE_PROJECT_ID", project_id)
        _firebase_manager = FirebaseManager(
            service_account_path=service_account_path,
            project_id=project_id,
            mode=mode
        )
    return _firebase_manager
