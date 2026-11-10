import os, urllib.parse
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from dotenv import load_dotenv

# ------------------------------------------------------------------
# CONFIGURAÇÃO (os valores secretos ficam no arquivo .env)
# ------------------------------------------------------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave")

URL, KEY = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
# Chave "service_role": só o servidor usa, para excluir contas. NUNCA vai para o navegador.
SERVICE_KEY = (os.getenv("SUPABASE_SERVICE_KEY")
               or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
if not SERVICE_KEY:
    print("AVISO: SUPABASE_SERVICE_KEY não foi encontrada no .env (exclusão de conta desativada).")
# Endereço público do site (ex.: https://doceartecupcakes.onrender.com). Opcional no teste local.
APP_URL = os.getenv("APP_URL")

WHATS = os.getenv("WHATSAPP", "5535991170720")
INSTA = os.getenv("INSTAGRAM", "doceartecupcakes")
db = create_client(URL, KEY)


@app.context_processor
def globais():
    """Variáveis disponíveis em todas as páginas."""
    c = session.get("carrinho", {})
    return dict(whats=WHATS, insta=INSTA, qtd_carrinho=sum(c.values()),
                usuario=(session.get("perfil") or {}).get("nome"))


# ------------------------------------------------------------------
# PRODUTOS E CARRINHO
# ------------------------------------------------------------------
# Palavras do nome do produto que ligam cada sabor à sua foto.
# O site procura na pasta "static" (e dentro das subpastas) um arquivo com esse nome:
# baunilha.jpg, chocolate.jpg, morango.jpg, ninho.jpg (também aceita .jpeg, .png, .webp).
SABORES = ["baunilha", "chocolate", "morango", "ninho"]
EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")


def achar_foto(sabor):
    """Procura o arquivo da foto do sabor dentro da pasta static."""
    base = app.static_folder
    for pasta, _, arquivos in os.walk(base):
        for arq in arquivos:
            nome, ext = os.path.splitext(arq)
            if nome.lower() == sabor and ext.lower() in EXTENSOES:
                caminho = os.path.relpath(os.path.join(pasta, arq), base)
                return caminho.replace(os.sep, "/")
    print(f"AVISO: não encontrei a foto do sabor '{sabor}' dentro da pasta static.")
    return None


def foto_do_produto(p):
    """Usa a imagem cadastrada no banco; se não tiver, usa a foto do sabor."""
    if p.get("imagem_url"):
        return p["imagem_url"]
    nome = (p.get("nome") or "").lower()
    for sabor in SABORES:
        if sabor in nome:
            arquivo = achar_foto(sabor)
            return url_for("static", filename=arquivo) if arquivo else None
    return None


def produtos():
    lista = db.table("produtos").select("*").order("id").execute().data
    for p in lista:
        p["imagem"] = foto_do_produto(p)
    return lista


def itens_carrinho():
    c = session.get("carrinho", {})
    itens, total = [], 0.0
    for p in produtos():
        q = c.get(str(p["id"]))
        if q:
            sub = float(p["preco"]) * q
            itens.append({**p, "qtd": q, "sub": sub})
            total += sub
    return itens, total


@app.route("/")
def home():
    return render_template("index.html", produtos=produtos())


@app.post("/add/<pid>")
def add(pid):
    c = session.get("carrinho", {})
    c[pid] = c.get(pid, 0) + 1
    session["carrinho"] = c
    flash("Adicionado ao carrinho! 🧁")
    return redirect(request.referrer or url_for("home"))


@app.post("/remover/<pid>")
def remover(pid):
    c = session.get("carrinho", {})
    if c.get(pid, 0) > 1:
        c[pid] -= 1
    else:
        c.pop(pid, None)
    session["carrinho"] = c
    return redirect(url_for("carrinho"))


@app.route("/carrinho")
def carrinho():
    itens, total = itens_carrinho()
    return render_template("carrinho.html", itens=itens, total=total,
                           perfil=session.get("perfil") or {})


@app.post("/finalizar")
def finalizar():
    if not session.get("perfil"):
        flash("Entre na sua conta para finalizar o pedido.")
        return redirect(url_for("login"))
    itens, total = itens_carrinho()
    if not itens:
        return redirect(url_for("carrinho"))
    perfil = session["perfil"]
    endereco = request.form["endereco"]
    pagamento = request.form["pagamento"]
    lista = "\n".join(f"{i['qtd']}x {i['nome']} - R$ {i['sub']:.2f}" for i in itens)
    try:
        db.table("pedidos").insert({
            "cliente": perfil.get("nome"), "email": perfil.get("email"),
            "telefone": perfil.get("telefone"), "endereco": endereco,
            "pagamento": pagamento, "itens": lista, "total": total}).execute()
    except Exception as e:
        print("Não salvou o pedido:", e)
    msg = (f"Olá! Novo pedido de {perfil.get('nome')}:\n{lista}\n"
           f"Total: R$ {total:.2f}\nPagamento: {pagamento}\nEndereço: {endereco}")
    session["carrinho"] = {}
    return redirect(f"https://wa.me/{WHATS}?text=" + urllib.parse.quote(msg))


# ------------------------------------------------------------------
# CADASTRO, LOGIN E SAIR
# ------------------------------------------------------------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        f = request.form
        # Dados extras que ficam guardados junto com a conta no Supabase
        dados = {k: f.get(k, "") for k in ("nome", "telefone", "rua", "numero",
                                           "complemento", "bairro")}
        try:
            novo = create_client(URL, KEY)
            novo.auth.sign_up({"email": f["email"], "password": f["senha"],
                               "options": {"data": dados}})
            flash("Conta criada! Agora é só entrar.")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Não deu certo: {e}")
    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            novo = create_client(URL, KEY)
            r = novo.auth.sign_in_with_password(
                {"email": request.form["email"], "password": request.form["senha"]})
            meta = r.user.user_metadata or {}
            nome = meta.get("nome") or r.user.email.split("@")[0]
            session["perfil"] = {**meta, "email": r.user.email, "nome": nome}
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Não foi possível entrar: {e}")
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.pop("perfil", None)
    return redirect(url_for("home"))


# ------------------------------------------------------------------
# NOVO: REDEFINIÇÃO DE SENHA ("esqueci minha senha")
# Passo 1: cliente informa o e-mail  -> Supabase envia um link por e-mail
# Passo 2: cliente clica no link     -> abre /redefinir -> escolhe a nova senha
# ------------------------------------------------------------------
@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form["email"].strip()
        base = (APP_URL or request.host_url).rstrip("/")
        try:
            requests.post(
                f"{URL}/auth/v1/recover",
                params={"redirect_to": base + "/redefinir"},  # para onde o link do e-mail leva
                headers={"apikey": KEY, "Content-Type": "application/json"},
                json={"email": email}, timeout=15)
        except Exception as e:
            print("Erro ao pedir e-mail de recuperação:", e)
        # Mesma mensagem sempre: assim ninguém descobre quais e-mails têm conta.
        flash("Se esse e-mail tiver cadastro, enviamos um link para criar uma nova senha. 📧")
        return redirect(url_for("login"))
    return render_template("esqueci_senha.html")


@app.route("/redefinir", methods=["GET", "POST"])
def redefinir():
    if request.method == "POST":
        token = request.form.get("token", "")
        senha = request.form.get("senha", "")
        if not token:
            flash("Link inválido ou vencido. Peça um novo.")
            return redirect(url_for("esqueci_senha"))
        if senha != request.form.get("senha2", "") or len(senha) < 6:
            flash("As senhas precisam ser iguais e ter pelo menos 6 caracteres.")
            return render_template("redefinir.html", token=token)
        motivo = "Não foi possível trocar a senha. Tente de novo."
        try:
            r = requests.put(
                f"{URL}/auth/v1/user",
                headers={"apikey": KEY, "Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                json={"password": senha}, timeout=15)
            if r.ok:
                flash("Senha alterada! Agora é só entrar. 🎉")
                return redirect(url_for("login"))
            print("Erro ao trocar senha:", r.status_code, r.text)
            try:
                codigo = r.json().get("error_code", "")
            except Exception:
                codigo = ""
            if codigo == "same_password":
                motivo = "A nova senha precisa ser diferente da senha anterior."
            elif codigo == "weak_password":
                motivo = "Essa senha é fraca demais. Use letras e números."
            elif r.status_code in (401, 403):
                flash("Esse link venceu ou já foi usado. Peça um novo.")
                return redirect(url_for("esqueci_senha"))
        except Exception as e:
            print("Erro ao trocar senha:", e)
        flash(motivo)
        return render_template("redefinir.html", token=token)
    return render_template("redefinir.html")


# ------------------------------------------------------------------
# NOVO: MINHA CONTA E EXCLUSÃO DE CONTA
# ------------------------------------------------------------------
@app.route("/conta")
def conta():
    if not session.get("perfil"):
        flash("Entre na sua conta para ver esta página.")
        return redirect(url_for("login"))
    return render_template("conta.html", perfil=session["perfil"])


@app.post("/conta/excluir")
def excluir_conta():
    perfil = session.get("perfil")
    if not perfil:
        return redirect(url_for("login"))

    if not SERVICE_KEY:
        flash("A exclusão automática ainda não foi configurada no servidor. Fale com a gente pelo WhatsApp.")
        return redirect(url_for("conta"))

    # Confirma que quem está pedindo é mesmo o dono da conta (pede a senha)
    try:
        novo = create_client(URL, KEY)
        r = novo.auth.sign_in_with_password(
            {"email": perfil["email"], "password": request.form.get("senha", "")})
        user_id = r.user.id
    except Exception:
        flash("Senha incorreta. Sua conta não foi excluída.")
        return redirect(url_for("conta"))

    # Exclui a conta no Supabase (precisa da chave service_role)
    try:
        resp = requests.delete(
            f"{URL}/auth/v1/admin/users/{user_id}",
            headers={"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"},
            timeout=15)
        if resp.ok:
            session.clear()
            flash("Sua conta foi excluída. Obrigada por ter adoçado seu dia com a gente! 💗")
            return redirect(url_for("home"))
        print("Erro ao excluir conta:", resp.text)
    except Exception as e:
        print("Erro ao excluir conta:", e)
    flash("Não foi possível excluir agora. Tente de novo ou chame no WhatsApp.")
    return redirect(url_for("conta"))


# ------------------------------------------------------------------
# PWA (app instalável)
# ------------------------------------------------------------------
@app.route("/sw.js")
def service_worker():
    return app.send_static_file("sw.js"), 200, {
        "Content-Type": "application/javascript", "Service-Worker-Allowed": "/"}


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json"), 200, {
        "Content-Type": "application/manifest+json"}


if __name__ == "__main__":
    app.run(debug=True)