"""Testes dos produtos e das fotos (models/produto.py)."""
import os
import tempfile
import unittest
from unittest.mock import patch

from models import produto
from tests.ajudantes import BancoFalso, novo_navegador


class TesteFotos(unittest.TestCase):

    def test_achar_foto_em_subpasta(self):
        """A foto do sabor é encontrada mesmo dentro de uma subpasta."""
        with tempfile.TemporaryDirectory() as pasta:
            os.makedirs(os.path.join(pasta, "img"))
            open(os.path.join(pasta, "img", "ninho.jpg"), "wb").close()
            self.assertEqual(produto.achar_foto("ninho", pasta), "img/ninho.jpg")

    def test_achar_foto_ignora_maiusculas_e_aceita_outras_extensoes(self):
        """Nome em maiúsculas e extensões como .PNG também funcionam."""
        with tempfile.TemporaryDirectory() as pasta:
            open(os.path.join(pasta, "Morango.PNG"), "wb").close()
            self.assertEqual(produto.achar_foto("morango", pasta), "Morango.PNG")

    def test_achar_foto_devolve_nada_quando_nao_existe(self):
        """Sem arquivo do sabor, o resultado é None (e o site mostra o desenho)."""
        with tempfile.TemporaryDirectory() as pasta:
            self.assertIsNone(produto.achar_foto("baunilha", pasta))

    def test_foto_cadastrada_no_banco_tem_prioridade(self):
        """Se o produto tem imagem_url no banco, ela é a usada."""
        p = {"nome": "Cupcake de Ninho", "imagem_url": "https://exemplo.com/foto.jpg"}
        self.assertEqual(produto.foto_do_produto(p), "https://exemplo.com/foto.jpg")


class TesteProdutoNoSite(unittest.TestCase):

    def setUp(self):
        self.app, _ = novo_navegador()

    def test_foto_do_sabor_usa_o_arquivo_da_pasta_static(self):
        """'Cupcake de Ninho' recebe a foto ninho.jpg que está na pasta static."""
        with self.app.test_request_context():
            self.assertEqual(produto.foto_do_produto({"nome": "Cupcake de Ninho"}), "/static/img/ninho.jpg")

    def test_sabor_sem_foto_devolve_nada(self):
        """Se não achar o arquivo do sabor, devolve None."""
        with self.app.test_request_context(), patch("models.produto.achar_foto", return_value=None):
            self.assertIsNone(produto.foto_do_produto({"nome": "Cupcake de Ninho"}))

    def test_produto_de_sabor_desconhecido_fica_sem_foto(self):
        """Um sabor que não está na lista fica sem foto."""
        with self.app.test_request_context():
            self.assertIsNone(produto.foto_do_produto({"nome": "Cupcake de Limão"}))

    def test_listar_preenche_o_campo_imagem(self):
        """A lista de produtos vem com o campo 'imagem' preenchido."""
        with self.app.test_request_context(), \
                patch("models.produto.cliente_compartilhado", return_value=BancoFalso()):
            lista = produto.listar()
        self.assertEqual(len(lista), 2)
        self.assertEqual(lista[0]["imagem"], "/static/img/baunilha.jpg")


if __name__ == "__main__":
    unittest.main()
