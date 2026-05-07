from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template('layouts/base.html')


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def auth():
    return render_template("layouts/auth.html")

