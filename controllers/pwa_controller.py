"""Arquivos do app instalável (PWA): service worker e manifesto."""
from flask import current_app


def service_worker():
    return current_app.send_static_file("sw.js"), 200, {
        "Content-Type": "application/javascript", "Service-Worker-Allowed": "/"}


def manifest():
    return current_app.send_static_file("manifest.json"), 200, {
        "Content-Type": "application/manifest+json"}


def registrar(app):
    app.add_url_rule("/sw.js", "service_worker", service_worker)
    app.add_url_rule("/manifest.json", "manifest", manifest)
