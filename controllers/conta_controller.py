"""Cadastro, login, nova senha, minha conta e exclusão de conta."""
from flask import flash, redirect, render_template, request, session, url_for

from configuracao import Config
from models import usuario as usuario_model
from models.usuario import ErroUsuario, LinkVencido


def cadastro():
    if request.method == "POST":
        formulario = request.form
        email = formulario.get("email", "").strip()
        senha = formulario.get("senha", "")
        if not email or not senha:
            flash("Preencha o e-mail e a senha.")
            return render_template("cadastro.html")
        dados = {campo: formulario.get(campo, "") for campo in usuario_model.CAMPOS_PERFIL}
        try:
            usuario_model.cadastrar(email, senha, dados)
            flash("Conta criada! Agora é só entrar.")
            return redirect(url_for("login"))
        except ErroUsuario as erro:
            flash(str(erro))
    return render_template("cadastro.html")


def login():
    if request.method == "POST":
        try:
            session["perfil"] = usuario_model.entrar(
                request.form.get("email", "").strip(), request.form.get("senha", ""))
            return redirect(url_for("home"))
        except ErroUsuario as erro:
            flash(str(erro))
    return render_template("login.html")


def sair():
    session.pop("perfil", None)
    return redirect(url_for("home"))


def esqueci_senha():
    if request.method == "POST":
        endereco_do_site = (Config.APP_URL or request.host_url).rstrip("/")
        usuario_model.pedir_link_nova_senha(request.form.get("email", "").strip(), endereco_do_site)
        # Mesma mensagem sempre: assim ninguém descobre quais e-mails têm conta.
        flash("Se esse e-mail tiver cadastro, enviamos um link para criar uma nova senha. 📧")
        return redirect(url_for("login"))
    return render_template("esqueci_senha.html")


def redefinir():
    if request.method == "POST":
        token = request.form.get("token", "")
        senha = request.form.get("senha", "")
        if not token:
            flash("Link inválido ou vencido. Peça um novo.")
            return redirect(url_for("esqueci_senha"))
        if senha != request.form.get("senha2", "") or len(senha) < 6:
            flash("As senhas precisam ser iguais e ter pelo menos 6 caracteres.")
            return render_template("redefinir.html", token=token)
        try:
            usuario_model.trocar_senha(token, senha)
            flash("Senha alterada! Agora é só entrar. 🎉")
            return redirect(url_for("login"))
        except LinkVencido as erro:
            flash(str(erro))
            return redirect(url_for("esqueci_senha"))
        except ErroUsuario as erro:
            flash(str(erro))
            return render_template("redefinir.html", token=token)
    return render_template("redefinir.html")


def minha_conta():
    if not session.get("perfil"):
        flash("Entre na sua conta para ver esta página.")
        return redirect(url_for("login"))
    return render_template("conta.html", perfil=session["perfil"])


def excluir_conta():
    perfil = session.get("perfil")
    if not perfil:
        return redirect(url_for("login"))
    try:
        usuario_model.excluir_conta(perfil["email"], request.form.get("senha", ""))
    except ErroUsuario as erro:
        flash(str(erro))
        return redirect(url_for("conta"))
    session.clear()
    flash("Sua conta foi excluída. Obrigada por ter adoçado seu dia com a gente! 💗")
    return redirect(url_for("home"))


def registrar(app):
    """Liga cada endereço do site à sua função."""
    app.add_url_rule("/cadastro", "cadastro", cadastro, methods=["GET", "POST"])
    app.add_url_rule("/login", "login", login, methods=["GET", "POST"])
    app.add_url_rule("/sair", "sair", sair)
    app.add_url_rule("/esqueci-senha", "esqueci_senha", esqueci_senha, methods=["GET", "POST"])
    app.add_url_rule("/redefinir", "redefinir", redefinir, methods=["GET", "POST"])
    app.add_url_rule("/conta", "conta", minha_conta)
    app.add_url_rule("/conta/excluir", "excluir_conta", excluir_conta, methods=["POST"])
