"""Configurações do site.

Os valores secretos vêm do arquivo .env (no seu computador) ou das variáveis
de ambiente do serviço de hospedagem (no Render). Nada secreto fica no código.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _ler(nome, padrao=None):
    """Lê uma variável de ambiente, tirando espaços sobrando no começo e no fim."""
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    valor = valor.strip()
    return valor or padrao


class Config:
    SECRET_KEY = _ler("SECRET_KEY", "troque-esta-chave")
    SUPABASE_URL = _ler("SUPABASE_URL")
    SUPABASE_KEY = _ler("SUPABASE_KEY")
    # Chave "service_role": só o servidor usa, para excluir contas. NUNCA vai para o navegador.
    SUPABASE_SERVICE_KEY = _ler("SUPABASE_SERVICE_KEY") or _ler("SUPABASE_SERVICE_ROLE_KEY") or ""
    WHATSAPP = _ler("WHATSAPP", "5535991170720")
    INSTAGRAM = _ler("INSTAGRAM", "doceartecupcakes")
    # Endereço público do site (ex.: https://doce-arte.onrender.com). Opcional no teste local.
    APP_URL = _ler("APP_URL")
