from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import Usuario
from app.forms.LoginForm import LoginForm
from app.forms.RegisterNewUserForm import RegistrarUsuario  # <-- Importando seu form de cadastro

main_bp = Blueprint("main", __name__)
web_auth_bp = Blueprint("web_auth", __name__)


@main_bp.route("/")
def home():
    # Se o usuário já estiver logado, você pode redirecioná-lo para uma página interna (ex: de tickets)
    if current_user.is_authenticated:
        # Substitua 'main.home' pela rota da sua dashboard real futuramente se quiser
        return render_template("index.html") 
    return redirect(url_for("web_auth.login"))


@web_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))  # <-- Ajustado de 'main.index' para 'main.home'

    form = LoginForm()

    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))  # <-- Ajustado aqui também
        else:
            flash("E-mail ou senha incorretos.", "danger")

    return render_template("auth/login.html", form=form)


@web_auth_bp.route("/cadastro", methods=["GET", "POST"])  # <-- Habilitado POST para receber dados
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrarUsuario()  # <-- Instanciando seu formulário com WTForms e QuerySelectField

    if form.validate_on_submit():
        # Verifica se o e-mail já existe
        user_exists = Usuario.query.filter_by(email=form.email.data).first()
        if user_exists:
            flash("Este e-mail já está cadastrado no sistema.", "danger")
            return render_template("auth/cadastro.html", form=form)

        # Cria o novo usuário com os campos do seu formulário
        novo_usuario = Usuario(
            name=form.name.data,
            email=form.email.data,
            role_id=form.role.data.id  # Atribui o ID do Cargo selecionado no banco
        )
        novo_usuario.set_password(form.password.data)  # Criptografa a senha

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash("Usuário registrado com sucesso! Faça o login.", "success")
            return redirect(url_for("web_auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Erro ao salvar o usuário. Tente novamente.", "danger")

    return render_template("auth/cadastro.html", form=form)


@web_auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado com sucesso.", "info")
    return redirect(url_for("web_auth.login"))