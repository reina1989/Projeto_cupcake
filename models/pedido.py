"""Pedidos: montagem da mensagem do WhatsApp e gravação no Supabase."""
import logging
import urllib.parse

from configuracao import Config
from models.banco import cliente_compartilhado

log = logging.getLogger(__name__)

PAGAMENTOS = ("Pix", "Dinheiro", "Cartão na entrega")


def pagamento_valido(pagamento):
    return pagamento in PAGAMENTOS


def montar_lista(itens):
    return "\n".join(f"{i['qtd']}x {i['nome']} - R$ {i['sub']:.2f}" for i in itens)


def montar_mensagem(perfil, lista, total, pagamento, endereco):
    return (f"Olá! Novo pedido de {perfil.get('nome')}:\n{lista}\n"
            f"Total: R$ {total:.2f}\nPagamento: {pagamento}\nEndereço: {endereco}")


def link_whatsapp(mensagem):
    return f"https://wa.me/{Config.WHATSAPP}?text=" + urllib.parse.quote(mensagem)


def salvar(perfil, endereco, pagamento, lista, total):
    """Grava o pedido no Supabase. Devolve True se deu certo, False se falhou."""
    try:
        cliente_compartilhado().table("pedidos").insert({
            "cliente": perfil.get("nome"), "email": perfil.get("email"),
            "telefone": perfil.get("telefone"), "endereco": endereco,
            "pagamento": pagamento, "itens": lista, "total": total}).execute()
        return True
    except Exception as erro:
        log.warning("Não salvou o pedido: %s", erro)
        return False
