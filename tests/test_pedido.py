"""Testes do pedido (models/pedido.py): mensagem do WhatsApp e gravação."""
import unittest
from unittest.mock import patch

from configuracao import Config
from models import pedido
from tests.ajudantes import PERFIL_EXEMPLO, BancoFalso

ITENS = [{"qtd": 2, "nome": "Cupcake de Ninho", "sub": 16.0}]


class TestePedido(unittest.TestCase):

    def test_montar_lista_de_itens(self):
        """A lista do pedido mostra quantidade, nome e subtotal."""
        self.assertEqual(pedido.montar_lista(ITENS), "2x Cupcake de Ninho - R$ 16.00")

    def test_mensagem_contem_os_dados_do_pedido(self):
        """A mensagem do WhatsApp traz cliente, itens, total, pagamento e endereço."""
        texto = pedido.montar_mensagem(PERFIL_EXEMPLO, "2x Ninho", 16.0, "Pix", "Rua A, 10")
        for esperado in ("Maria", "2x Ninho", "R$ 16.00", "Pix", "Rua A, 10"):
            self.assertIn(esperado, texto)

    def test_link_do_whatsapp_usa_o_numero_e_codifica_o_texto(self):
        """O link usa o número da loja e codifica espaços e quebras de linha."""
        with patch.object(Config, "WHATSAPP", "5511999999999"):
            link = pedido.link_whatsapp("Olá mundo\nlinha 2")
        self.assertTrue(link.startswith("https://wa.me/5511999999999?text="))
        self.assertIn("Ol%C3%A1%20mundo%0Alinha%202", link)

    def test_pagamento_valido(self):
        """Só as formas de pagamento oferecidas pela loja são aceitas."""
        self.assertTrue(pedido.pagamento_valido("Pix"))
        self.assertFalse(pedido.pagamento_valido("Fiado"))

    def test_salvar_grava_o_pedido_no_banco(self):
        """Salvar envia os dados do cliente e do pedido para a tabela pedidos."""
        banco = BancoFalso()
        with patch("models.pedido.cliente_compartilhado", return_value=banco):
            ok = pedido.salvar(PERFIL_EXEMPLO, "Rua A, 10", "Pix", "2x Ninho", 16.0)
        self.assertTrue(ok)
        linha = banco.tabelas["pedidos"].inseridos[0]
        self.assertEqual(linha["cliente"], "Maria")
        self.assertEqual(linha["total"], 16.0)
        self.assertEqual(linha["pagamento"], "Pix")

    def test_salvar_devolve_falso_se_o_banco_falhar(self):
        """Se o banco falhar, salvar não derruba o site: devolve False."""
        with patch("models.pedido.cliente_compartilhado", side_effect=RuntimeError("fora do ar")):
            self.assertFalse(pedido.salvar(PERFIL_EXEMPLO, "Rua A", "Pix", "x", 1.0))


if __name__ == "__main__":
    unittest.main()
