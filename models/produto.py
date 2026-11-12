"""Produtos (cupcakes) lidos do Supabase e suas fotos."""
import os

from flask import current_app, url_for

from models.banco import cliente_compartilhado

# Palavras do nome do produto que ligam cada sabor à sua foto.
# O site procura na pasta "static" um arquivo com esse nome (baunilha.jpg, ninho.png...).
SABORES = ["baunilha", "chocolate", "morango", "ninho"]
EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")


def achar_foto(sabor, pasta_static):
    """Procura a foto do sabor dentro da pasta static (e subpastas). Devolve o caminho relativo ou None."""
    for pasta, _, arquivos in os.walk(pasta_static):
        for arquivo in arquivos:
            nome, extensao = os.path.splitext(arquivo)
            if nome.lower() == sabor and extensao.lower() in EXTENSOES:
                caminho = os.path.relpath(os.path.join(pasta, arquivo), pasta_static)
                return caminho.replace(os.sep, "/")
    return None


def foto_do_produto(produto):
    """Usa a imagem cadastrada no banco; se não tiver, usa a foto do sabor."""
    if produto.get("imagem_url"):
        return produto["imagem_url"]
    nome = (produto.get("nome") or "").lower()
    for sabor in SABORES:
        if sabor in nome:
            arquivo = achar_foto(sabor, current_app.static_folder)
            return url_for("static", filename=arquivo) if arquivo else None
    return None


def listar():
    """Todos os produtos do banco, já com o campo 'imagem' preenchido."""
    produtos = cliente_compartilhado().table("produtos").select("*").order("id").execute().data
    for produto in produtos:
        produto["imagem"] = foto_do_produto(produto)
    return produtos
