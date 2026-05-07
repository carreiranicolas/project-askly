from flask import Blueprint, redirect, render_template, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return redirect(url_for("web_auth.login"))


web_auth_bp = Blueprint("web_auth", __name__)


@web_auth_bp.route("/login")
def login():
    return render_template("auth/login.html")


@web_auth_bp.route("/cadastro")
def cadastro():
    return render_template("auth/cadastro.html")

