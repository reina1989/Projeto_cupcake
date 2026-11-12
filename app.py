"""Ponto de entrada do site Doce Arte Cupcakes.

Organização (padrão MVC):
  models/       -> regras e dados (Supabase)
  controllers/  -> recebem o pedido do cliente e decidem a resposta
  templates/    -> as páginas (View)
  static/       -> CSS, fotos e arquivos do app instalável

Para ligar o site:   python app.py
Na hospedagem:       gunicorn app:app
"""
import logging

from flask import Flask, session

from configuracao import Config
from controllers import conta_controller, loja_controller, pwa_controller
from models import carrinho as carrinho_model

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def verificar_configuracao():
    """Avisa no terminal se alguma chave importante estiver faltando."""
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        log.error("SUPABASE_URL e/ou SUPABASE_KEY não foram encontradas no .env: o site não vai conseguir acessar o banco.")
    if not Config.SUPABASE_SERVICE_KEY:
        log.warning("SUPABASE_SERVICE_KEY não foi encontrada no .env (exclusão de conta desativada).")


def criar_app(testing=False):
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    app.config["TESTING"] = testing

    @app.context_processor
    def globais():
        """Variáveis disponíveis em todas as páginas."""
        return dict(
            whats=Config.WHATSAPP,
            insta=Config.INSTAGRAM,
            qtd_carrinho=carrinho_model.quantidade_total(session.get("carrinho", {})),
            usuario=(session.get("perfil") or {}).get("nome"))

    for controlador in (loja_controller, conta_controller, pwa_controller):
        controlador.registrar(app)

    if not testing:
        verificar_configuracao()
    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
