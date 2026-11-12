"""Testes automáticos do site. Para rodar: pytest   (ou: python -m unittest discover -s tests -t .)"""
import logging

# Os avisos de erro "de propósito" que os testes provocam não precisam aparecer na tela.
logging.disable(logging.CRITICAL)
