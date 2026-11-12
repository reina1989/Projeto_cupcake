"""Cardápio, carrinho e finalização do pedido."""
from flask import flash, redirect, render_template, request, session, url_for

from models import carrinho as carrinho_model
from models import pedido as pedido_model
from models import produto as produto_model


def _itens_e_total():
    return carrinho_model.montar_itens(session.get("carrinho", {}), produto_model.listar())


def home():
    return render_template("index.html", produtos=produto_model.listar())


def adicionar(pid):
    session["carrinho"] = carrinho_model.adicionar(session.get("carrinho", {}), pid)
    flash("Adicionado ao carrinho! 🧁")
    return redirect(request.referrer or url_for("home"))


def remover(pid):
    session["carrinho"] = carrinho_model.remover(session.get("carrinho", {}), pid)
    return redirect(url_for("carrinho"))


def ver_carrinho():
    itens, total = _itens_e_total()
    return render_template("carrinho.html", itens=itens, total=total,
                           perfil=session.get("perfil") or {})


def finalizar():
    perfil = session.get("perfil")
    if not perfil:
        flash("Entre na sua conta para finalizar o pedido.")
        return redirect(url_for("login"))

    itens, total = _itens_e_total()
    if not itens:
        return redirect(url_for("carrinho"))

    endereco = request.form.get("endereco", "").strip()
    pagamento = request.form.get("pagamento", "")
    if not endereco:
        flash("Informe o endereço de entrega.")
        return redirect(url_for("carrinho"))
    if not pedido_model.pagamento_valido(pagamento):
        flash("Escolha uma forma de pagamento válida.")
        return redirect(url_for("carrinho"))

    lista = pedido_model.montar_lista(itens)
    pedido_model.salvar(perfil, endereco, pagamento, lista, total)  # se falhar, o pedido ainda vai pelo WhatsApp
    mensagem = pedido_model.montar_mensagem(perfil, lista, total, pagamento, endereco)
    session["carrinho"] = {}
    return redirect(pedido_model.link_whatsapp(mensagem))


def registrar(app):
    """Liga cada endereço do site à sua função."""
    app.add_url_rule("/", "home", home)
    app.add_url_rule("/add/<pid>", "add", adicionar, methods=["POST"])
    app.add_url_rule("/remover/<pid>", "remover", remover, methods=["POST"])
    app.add_url_rule("/carrinho", "carrinho", ver_carrinho)
    app.add_url_rule("/finalizar", "finalizar", finalizar, methods=["POST"])
