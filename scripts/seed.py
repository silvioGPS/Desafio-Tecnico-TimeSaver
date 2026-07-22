from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask
from werkzeug.security import generate_password_hash

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.db import seed_default_user


def main() -> None:
    app: Flask = create_app()
    with app.app_context():
        seed_default_user(generate_password_hash("Agenda@123"))
    print("Banco preparado com o usuário admin / Agenda@123")


if __name__ == "__main__":
    main()