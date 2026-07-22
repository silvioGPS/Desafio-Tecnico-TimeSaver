from __future__ import annotations

import logging
from functools import wraps

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import DatabaseUnavailable, get_user_by_identifier
from .services.appointments_client import AppointmentAPIError, fetch_appointments


auth_bp = Blueprint("auth", __name__)
main_bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/", methods=["GET"])
def index():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Preencha usuário/e-mail e senha para continuar.", "error")
            return render_template("login.html")

        try:
            user = get_user_by_identifier(identifier)
        except DatabaseUnavailable:
            current_app.logger.exception("Falha ao consultar o banco durante o login.")
            flash("Não foi possível acessar o banco de dados no momento.", "error")
            return render_template("login.html"), 503

        if user is not None and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["username"]
            session["user_email"] = user["email"]
            return redirect(url_for("main.dashboard"))

        flash("Credenciais inválidas. Verifique o usuário/e-mail e a senha.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Você saiu da sessão com sucesso.", "success")
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "Usuário"),
        user_email=session.get("user_email", ""),
    )


@main_bp.route("/appointments/data", methods=["GET"])
@login_required
def appointments_data():
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
        current_app.logger.exception("Erro inesperado ao carregar os agendamentos.")
        return jsonify(ok=False, message="Não foi possível carregar os agendamentos no momento.", records=[]), 500

    if not payload.records:
        return jsonify(ok=True, message="Nenhum agendamento encontrado.", records=[])

    return jsonify(
        ok=True,
        message=f"{len(payload.records)} agendamento(s) encontrado(s).",
        records=payload.records,
    )