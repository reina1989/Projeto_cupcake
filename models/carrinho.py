"""Regras do carrinho de compras.

São funções "puras": recebem o carrinho (um dicionário {id_do_produto: quantidade})
e devolvem um carrinho novo. Quem guarda o carrinho na sessão é o controller.
"""


def adicionar(carrinho, produto_id):
    novo = dict(carrinho)
    chave = str(produto_id)
    novo[chave] = novo.get(chave, 0) + 1
    return novo


def remover(carrinho, produto_id):
    """Tira uma unidade; se era a última, tira o item do carrinho."""
    novo = dict(carrinho)
    chave = str(produto_id)
    if novo.get(chave, 0) > 1:
        novo[chave] -= 1
    else:
        novo.pop(chave, None)
    return novo


def quantidade_total(carrinho):
    return sum(carrinho.values())


def montar_itens(carrinho, produtos):
    """Cruza o carrinho com a lista de produtos. Devolve (itens, total)."""
    itens, total = [], 0.0
    for p in produtos:
        qtd = carrinho.get(str(p["id"]))
        if qtd:
            subtotal = float(p["preco"]) * qtd
            itens.append({**p, "qtd": qtd, "sub": subtotal})
            total += subtotal
    return itens, total
