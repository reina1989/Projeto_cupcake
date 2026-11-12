"""Contas de clientes: cadastro, login, nova senha e exclusão (Supabase Auth).

Quando algo dá errado, as funções levantam ErroUsuario com uma mensagem em
português, pronta para mostrar ao cliente. O erro técnico vai só para o log.
"""
import logging

import requests

from configuracao import Config
from models.banco import cliente_novo

log = logging.getLogger(__name__)

TEMPO_LIMITE = 15  # segundos de espera pelo Supabase
CAMPOS_PERFIL = ("nome", "telefone", "rua", "numero", "complemento", "bairro")
MENSAGEM_PADRAO = "Não foi possível concluir agora. Tente novamente em instantes."

_MENSAGENS = [
    (("invalid login",), "E-mail ou senha incorretos."),
    (("email not confirmed",), "Confirme seu e-mail antes de entrar. Veja sua caixa de entrada."),
    (("already registered", "already been registered"), "Esse e-mail já tem cadastro. Tente entrar."),
    (("at least", "weak password", "password should"), "A senha precisa ter pelo menos 6 caracteres."),
    (("invalid format", "validate email"), "Digite um e-mail válido."),
    (("rate limit", "security purposes", "too many"), "Muitas tentativas. Aguarde alguns minutos e tente de novo."),
]


class ErroUsuario(Exception):
    """Erro com mensagem amigável para o cliente."""


class LinkVencido(ErroUsuario):
    """O link de nova senha venceu ou já foi usado."""


def traduzir_erro(erro):
    """Transforma o erro técnico do Supabase em uma frase simples em português."""
    texto = str(erro).lower()
    for palavras, mensagem in _MENSAGENS:
        if any(p in texto for p in palavras):
            return mensagem
    return MENSAGEM_PADRAO


def _cabecalho(chave, token=None):
    cabecalho = {"apikey": chave, "Content-Type": "application/json"}
    cabecalho["Authorization"] = f"Bearer {token or chave}"
    return cabecalho


def cadastrar(email, senha, dados):
    """Cria a conta. 'dados' (nome, telefone, rua...) ficam guardados junto com ela."""
    try:
        cliente_novo().auth.sign_up(
            {"email": email, "password": senha, "options": {"data": dados}})
    except Exception as erro:
        log.warning("Erro no cadastro: %s", erro)
        raise ErroUsuario(traduzir_erro(erro)) from erro


def entrar(email, senha):
    """Confere e-mail e senha. Devolve o perfil do cliente (dicionário)."""
    try:
        resposta = cliente_novo().auth.sign_in_with_password({"email": email, "password": senha})
    except Exception as erro:
        log.warning("Erro no login: %s", erro)
        raise ErroUsuario(traduzir_erro(erro)) from erro
    dados = resposta.user.user_metadata or {}
    nome = dados.get("nome") or resposta.user.email.split("@")[0]
    return {**dados, "email": resposta.user.email, "nome": nome}


def pedir_link_nova_senha(email, endereco_do_site):
    """Pede ao Supabase para enviar o e-mail com o link de nova senha.

    Não levanta erro nem diz se o e-mail existe: assim ninguém descobre quem tem cadastro.
    """
    try:
        requests.post(
            f"{Config.SUPABASE_URL}/auth/v1/recover",
            params={"redirect_to": endereco_do_site.rstrip("/") + "/redefinir"},
            headers={"apikey": Config.SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email}, timeout=TEMPO_LIMITE)
    except Exception as erro:
        log.warning("Erro ao pedir e-mail de recuperação: %s", erro)


def trocar_senha(token, nova_senha):
    """Troca a senha usando o 'token' que veio no link do e-mail."""
    try:
        resposta = requests.put(
            f"{Config.SUPABASE_URL}/auth/v1/user",
            headers=_cabecalho(Config.SUPABASE_KEY, token),
            json={"password": nova_senha}, timeout=TEMPO_LIMITE)
    except Exception as erro:
        log.warning("Erro ao trocar senha: %s", erro)
        raise ErroUsuario("Não foi possível trocar a senha. Tente de novo.") from erro
    if resposta.ok:
        return
    log.warning("Erro ao trocar senha: %s %s", resposta.status_code, getattr(resposta, "text", ""))
    try:
        codigo = resposta.json().get("error_code", "")
    except Exception:
        codigo = ""
    if codigo == "same_password":
        raise ErroUsuario("A nova senha precisa ser diferente da senha anterior.")
    if codigo == "weak_password":
        raise ErroUsuario("Essa senha é fraca demais. Use letras e números.")
    if resposta.status_code in (401, 403):
        raise LinkVencido("Esse link venceu ou já foi usado. Peça um novo.")
    raise ErroUsuario("Não foi possível trocar a senha. Tente de novo.")


def excluir_conta(email, senha):
    """Exclui a conta do cliente, depois de conferir a senha dele."""
    if not Config.SUPABASE_SERVICE_KEY:
        raise ErroUsuario("A exclusão automática ainda não foi configurada no servidor. "
                          "Fale com a gente pelo WhatsApp.")
    try:
        resposta = cliente_novo().auth.sign_in_with_password({"email": email, "password": senha})
        id_do_usuario = resposta.user.id
    except Exception as erro:
        log.warning("Senha incorreta ao excluir conta: %s", erro)
        raise ErroUsuario("Senha incorreta. Sua conta não foi excluída.") from erro
    try:
        apagou = requests.delete(
            f"{Config.SUPABASE_URL}/auth/v1/admin/users/{id_do_usuario}",
            headers={"apikey": Config.SUPABASE_SERVICE_KEY,
                     "Authorization": f"Bearer {Config.SUPABASE_SERVICE_KEY}"},
            timeout=TEMPO_LIMITE)
        if apagou.ok:
            return
        log.warning("Erro ao excluir conta: %s", getattr(apagou, "text", ""))
    except Exception as erro:
        log.warning("Erro ao excluir conta: %s", erro)
    raise ErroUsuario("Não foi possível excluir agora. Tente de novo ou chame no WhatsApp.")
