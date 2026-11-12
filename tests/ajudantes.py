"""Peças de apoio dos testes: um "banco de mentira" para não depender do Supabase."""
from types import SimpleNamespace

from app import criar_app

PERFIL_EXEMPLO = {"nome": "Maria", "email": "maria@exemplo.com", "telefone": "35999990000",
                  "rua": "Rua das Flores", "bairro": "Centro"}


def produtos_exemplo():
    return [
        {"id": 1, "nome": "Cupcake de Baunilha", "descricao": "Massa fofinha", "preco": 8.0, "imagem_url": None},
        {"id": 2, "nome": "Cupcake de Ninho", "descricao": "Creme de Ninho", "preco": 8.0, "imagem_url": None},
    ]


class TabelaFalsa:
    def __init__(self, dados=None):
        self.dados = dados or []
        self.inseridos = []

    def select(self, *_):
        return self

    def order(self, *_):
        return self

    def insert(self, linha):
        self.inseridos.append(linha)
        return self

    def execute(self):
        return SimpleNamespace(data=self.dados)


class BancoFalso:
    def __init__(self):
        self.tabelas = {"produtos": TabelaFalsa(produtos_exemplo()), "pedidos": TabelaFalsa()}

    def table(self, nome):
        return self.tabelas[nome]


def resposta_falsa(ok=True, status=200, json=None):
    """Imitação da resposta do Supabase nas chamadas feitas com 'requests'."""
    return SimpleNamespace(ok=ok, status_code=status, text="", json=lambda: json or {})


def cliente_auth_falso(email="maria@exemplo.com", metadados=None, id_usuario="abc-123", erro=None):
    """Imitação do cliente do Supabase para login/cadastro."""
    def entrar(_dados):
        if erro:
            raise erro
        usuario = SimpleNamespace(email=email, user_metadata=metadados, id=id_usuario)
        return SimpleNamespace(user=usuario)

    def cadastrar(dados):
        if erro:
            raise erro
        cadastrar.recebido = dados

    auth = SimpleNamespace(sign_in_with_password=entrar, sign_up=cadastrar)
    return SimpleNamespace(auth=auth)


def novo_navegador():
    """Cria o site em modo de teste e um 'navegador' de mentira para visitar as páginas."""
    app = criar_app(testing=True)
    return app, app.test_client()


def preparar_sessao(navegador, perfil=None, carrinho=None):
    with navegador.session_transaction() as sessao:
        if perfil is not None:
            sessao["perfil"] = perfil
        if carrinho is not None:
            sessao["carrinho"] = carrinho
