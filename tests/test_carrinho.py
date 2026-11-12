"""Testes unitários do carrinho (models/carrinho.py)."""
import unittest

from models import carrinho
from tests.ajudantes import produtos_exemplo


class TesteCarrinho(unittest.TestCase):

    def test_adicionar_item_novo(self):
        """Adicionar um produto novo coloca 1 unidade no carrinho."""
        self.assertEqual(carrinho.adicionar({}, 1), {"1": 1})

    def test_adicionar_mesmo_item_soma(self):
        """Adicionar o mesmo produto duas vezes soma as quantidades."""
        self.assertEqual(carrinho.adicionar({"1": 1}, "1"), {"1": 2})

    def test_adicionar_nao_altera_o_carrinho_original(self):
        """A função devolve um carrinho novo e não mexe no original."""
        original = {"1": 1}
        carrinho.adicionar(original, 1)
        self.assertEqual(original, {"1": 1})

    def test_remover_diminui_a_quantidade(self):
        """Remover um item com 2 unidades deixa 1."""
        self.assertEqual(carrinho.remover({"1": 2}, "1"), {"1": 1})

    def test_remover_ultima_unidade_tira_o_item(self):
        """Remover a última unidade tira o item do carrinho."""
        self.assertEqual(carrinho.remover({"1": 1}, "1"), {})

    def test_remover_item_inexistente_nao_da_erro(self):
        """Remover um produto que não está no carrinho não causa erro."""
        self.assertEqual(carrinho.remover({"1": 1}, "9"), {"1": 1})

    def test_quantidade_total(self):
        """A quantidade total soma todas as unidades."""
        self.assertEqual(carrinho.quantidade_total({"1": 2, "2": 3}), 5)

    def test_montar_itens_calcula_subtotal_e_total(self):
        """Subtotal e total são calculados com o preço de cada produto."""
        itens, total = carrinho.montar_itens({"1": 2, "2": 1}, produtos_exemplo())
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0]["sub"], 16.0)
        self.assertEqual(total, 24.0)

    def test_montar_itens_carrinho_vazio(self):
        """Carrinho vazio resulta em lista vazia e total zero."""
        self.assertEqual(carrinho.montar_itens({}, produtos_exemplo()), ([], 0.0))


if __name__ == "__main__":
    unittest.main()
