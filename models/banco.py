"""Conexão com o Supabase.

A biblioteca "supabase" só é carregada na hora de usar, assim o site (e os
testes) iniciam mesmo sem as chaves configuradas.
"""
from configuracao import Config

_compartilhado = None


def cliente_compartilhado():
    """Conexão reaproveitada, usada para ler produtos e salvar pedidos."""
    global _compartilhado
    if _compartilhado is None:
        from supabase import create_client
        _compartilhado = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    return _compartilhado


def cliente_novo():
    """Conexão nova, usada no login e cadastro (assim a sessão de um cliente não se mistura com a de outro)."""
    from supabase import create_client
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
