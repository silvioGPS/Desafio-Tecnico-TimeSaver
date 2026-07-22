from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "agenda_medica.sqlite3"))
    APPOINTMENTS_API_URL = os.environ.get("APPOINTMENTS_API_URL", "http://localhost:5001/appointments")
    APPOINTMENTS_API_TIMEOUT = int(os.environ.get("APPOINTMENTS_API_TIMEOUT", "5"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")