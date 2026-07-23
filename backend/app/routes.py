from __future__ import annotations

import logging
from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash

from .db import DatabaseUnavailable, get_user_by_identifier
from .services.appointments_client import AppointmentAPIError, fetch_appointments


auth_bp = Blueprint("auth", __name__)


def _authenticate_user(identifier: str, password: str):
    user = get_user_by_identifier(identifier)
    if user is not None and check_password_hash(user["password_hash"], password):
        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["username"]
        session["user_email"] = user["email"]
        return user
    return None


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    identifier = str(payload.get("identifier", "")).strip()
    password = str(payload.get("password", ""))

    if not identifier or not password:
        return jsonify(ok=False, message="Preencha usuário/e-mail e senha para continuar."), 400

    try:
        user = _authenticate_user(identifier, password)
    except DatabaseUnavailable:
        current_app.logger.exception("Falha ao consultar o banco durante o login da API.")
        return jsonify(ok=False, message="Não foi possível acessar o banco de dados no momento."), 503

    if user is None:
        return jsonify(ok=False, message="Credenciais inválidas. Verifique o usuário/e-mail e a senha."), 401

    return jsonify(
        ok=True,
        user={
            "id": user["id"],
            "name": user["username"],
            "email": user["email"],
        },
    )


@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify(ok=True, message="Sessão encerrada com sucesso.")


@auth_bp.route("/api/me", methods=["GET"])
def api_me():
    if "user_id" not in session:
        return jsonify(ok=False, authenticated=False), 401

    return jsonify(
        ok=True,
        authenticated=True,
        user={
            "id": session.get("user_id"),
            "name": session.get("user_name", "Usuário"),
            "email": session.get("user_email", ""),
        },
    )


@auth_bp.route("/", methods=["GET"])
def index():
    return jsonify(ok=True, service="agenda-medica-api")


@auth_bp.route("/api/appointments", methods=["GET"])
def api_appointments():
    if "user_id" not in session:
        return jsonify(ok=False, message="Autenticação necessária.", records=[]), 401

    search = request.args.get("search", "").strip()

    try:
        payload = fetch_appointments(
            api_url=current_app.config["APPOINTMENTS_API_URL"],
            timeout=current_app.config["APPOINTMENTS_API_TIMEOUT"],
            search=search,
        )
    except AppointmentAPIError as exc:
        current_app.logger.warning("Falha ao consultar a API de agendamentos: %s", exc)
        return jsonify(ok=False, message=str(exc), records=[]), 502
    except Exception:
        current_app.logger.exception("Erro inesperado ao carregar os agendamentos da API.")
        return jsonify(ok=False, message="Não foi possível carregar os agendamentos no momento.", records=[]), 500

    if not payload.records:
        return jsonify(ok=True, message="Nenhum agendamento encontrado.", records=[])

    return jsonify(
        ok=True,
        message=f"{len(payload.records)} agendamento(s) encontrado(s).",
        records=payload.records,
    )