from __future__ import annotations

import logging
import os
from typing import Any

from flask import Flask, jsonify, request


APPOINTMENTS = [
    {
        "patient": "Marina Souza",
        "cpf": "123.456.789-00",
        "doctor": "Dra. Carla Mendes",
        "specialty": "Cardiologia",
        "date": "2026-07-21",
        "time": "08:30",
        "insurance": "Unimed",
        "status": "Confirmado",
    },
    {
        "patient": "João Pedro Lima",
        "cpf": "987.654.321-11",
        "doctor": "Dr. Felipe Rocha",
        "specialty": "Dermatologia",
        "date": "2026-07-21",
        "time": "10:15",
        "insurance": "Bradesco Saúde",
        "status": "Aguardando",
    },
    {
        "patient": "Ana Beatriz Costa",
        "cpf": "444.555.666-77",
        "doctor": "Dra. Helena Prado",
        "specialty": "Pediatria",
        "date": "2026-07-22",
        "time": "13:40",
        "insurance": "SulAmérica",
        "status": "Concluído",
    },
    {
        "patient": "Paulo Henrique Alves",
        "cpf": "222.333.444-55",
        "doctor": "Dr. Eduardo Nunes",
        "specialty": "Ortopedia",
        "date": "2026-07-23",
        "time": "15:20",
        "insurance": "Particular",
        "status": "Cancelado",
    },
]


def _match_search(record: dict[str, Any], search: str) -> bool:
    if not search:
        return True
    text = search.lower()
    return any(text in str(record[key]).lower() for key in ("patient", "cpf", "doctor"))


def create_app() -> Flask:
    app = Flask(__name__)

    logging.basicConfig(
        level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/appointments")
    def appointments():
        mode = request.args.get("mode") or os.environ.get("APPOINTMENTS_API_MODE", "normal")
        search = request.args.get("search", "").strip()

        if mode == "down":
            return jsonify(error="temporarily unavailable"), 503

        if mode == "empty":
            return jsonify(appointments=[])

        if mode == "invalid":
            broken_record = {
                "patient": "Registro inválido",
                "cpf": "000.000.000-00",
                "doctor": "Sem médico",
                "specialty": "Sem especialidade",
                "date": "2026-07-21",
                "time": "12:00",
                "status": "Inconsistente",
            }
            return jsonify(appointments=[broken_record])

        filtered = [record for record in APPOINTMENTS if _match_search(record, search)]
        return jsonify(appointments=filtered)

    return app


if __name__ == "__main__":
    application = create_app()
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5001"))
    application.run(host=host, port=port)