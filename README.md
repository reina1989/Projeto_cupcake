# 🧁 Doce Arte Cupcakes

Site de pedidos online da **Doce Arte Cupcakes**. O cliente vê o cardápio com fotos, monta o carrinho, cria uma conta e envia o pedido pelo **WhatsApp**. O site também pode ser instalado no celular como um app (PWA).

Feito com **Python (Flask)** e **Supabase** (banco de dados e login).

---

## ✨ Funcionalidades

- **Cardápio** com foto, descrição e preço de cada sabor (baunilha, chocolate, morango e ninho)
- **Carrinho** com adicionar e remover itens
- **Cadastro e login** de clientes (e-mail e senha)
- **Olhinho 👁️** para mostrar e ocultar a senha em todos os campos de senha
- **Esqueci minha senha**: o cliente recebe um link por e-mail e cria uma nova senha
- **Minha conta**: página com os dados do cliente e botão para trocar a senha
- **Exclusão de conta**: o cliente confirma com a senha e a conta é apagada
- **Finalização do pedido**: escolhe a forma de pagamento (Pix, dinheiro ou cartão na entrega), confirma o endereço e o pedido é salvo e enviado pelo WhatsApp
- **App instalável (PWA)**: ícone, manifesto e service worker
- Botão flutuante de WhatsApp e link para o Instagram

---

## 🛠️ Tecnologias

| O quê | Para quê |
|---|---|
| [Flask](https://flask.palletsprojects.com/) | Servidor do site (Python) |
| [Supabase](https://supabase.com/) | Banco de dados (produtos e pedidos) e autenticação de clientes |
| HTML + CSS | Páginas e visual (sem frameworks) |
| Gunicorn | Servidor usado na publicação |
| Render | Hospedagem sugerida (plano gratuito) |

---

## 📁 Estrutura do projeto

O código segue o padrão **MVC** (Model, View, Controller). Veja a explicação completa em [`docs/arquitetura-mvc.md`](docs/arquitetura-mvc.md).

```
.
├── app.py                  # Ponto de entrada: cria o site e liga as rotas
├── configuracao.py         # Lê as chaves do .env
├── requirements.txt        # Bibliotecas do site
├── requirements-dev.txt    # Biblioteca de testes (pytest)
├── supabase.sql            # Cria as tabelas no Supabase
├── pytest.ini              # Configuração dos testes
├── .gitignore              # Arquivos que não vão para o GitHub (.env etc.)
├── models/                 # MODEL: regras e dados (Supabase)
│   ├── banco.py            # Conexão com o Supabase
│   ├── carrinho.py         # Regras do carrinho
│   ├── produto.py          # Produtos e fotos dos sabores
│   ├── pedido.py           # Mensagem do WhatsApp e gravação do pedido
│   └── usuario.py          # Cadastro, login, nova senha e exclusão de conta
├── controllers/            # CONTROLLER: recebe o pedido e escolhe a resposta
│   ├── loja_controller.py  # Cardápio, carrinho e finalizar pedido
│   ├── conta_controller.py # Cadastro, login, nova senha, minha conta
│   └── pwa_controller.py   # Arquivos do app instalável
├── templates/              # VIEW: páginas HTML
│   ├── base.html           # Modelo base (menu, rodapé, olhinho da senha)
│   ├── index.html          # Cardápio
│   ├── carrinho.html       # Carrinho e finalização do pedido
│   ├── cadastro.html       # Criar conta
│   ├── login.html          # Entrar
│   ├── esqueci_senha.html  # Pedir link de nova senha
│   ├── redefinir.html      # Criar a nova senha
│   └── conta.html          # Minha conta e exclusão de conta
├── static/                 # VIEW: arquivos públicos
│   ├── style.css           # Visual do site
│   ├── manifest.json       # Configuração do app instalável
│   ├── sw.js               # Service worker (PWA)
│   ├── icon-192.png        # Ícone do app
│   ├── icon-512.png        # Ícone do app
│   └── img/                # Fotos dos sabores (baunilha, chocolate, morango, ninho)
├── tests/                  # Testes automáticos
│   ├── ajudantes.py        # Banco de mentira usado nos testes
│   ├── test_carrinho.py
│   ├── test_pedido.py
│   ├── test_produto.py
│   ├── test_usuario.py
│   └── test_rotas.py
└── docs/
    ├── arquitetura-mvc.md        # Como o código está organizado
    └── testes-automatizados.md   # Lista dos testes e resultado
```

---

## 🔐 Variáveis de ambiente

As senhas e chaves **não ficam no código**. Crie um arquivo chamado `.env` na pasta do projeto (ao lado do `app.py`) com o seguinte conteúdo:

```env
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_KEY=sua_chave_publica_anon
SUPABASE_SERVICE_KEY=sua_chave_service_role
SECRET_KEY=uma-frase-longa-e-aleatoria
WHATSAPP=55DDDNUMERO
INSTAGRAM=doceartecupcakes
APP_URL=https://seu-site.onrender.com
```

| Variável | Para que serve |
|---|---|
| `SUPABASE_URL` | Endereço do seu projeto no Supabase |
| `SUPABASE_KEY` | Chave pública (anon) do Supabase |
| `SUPABASE_SERVICE_KEY` | Chave **service_role**, usada só para excluir contas. **Secreta** |
| `SECRET_KEY` | Protege o login e o carrinho dos clientes. Use um texto longo e aleatório |
| `WHATSAPP` | Número que recebe os pedidos, com país e DDD (ex.: `5535999999999`) |
| `INSTAGRAM` | Nome do perfil, sem o `@` |
| `APP_URL` | Endereço público do site. Usado no link de "esqueci minha senha". Pode ficar de fora nos testes no computador |

> ⚠️ **Nunca envie o `.env` para o GitHub.** A chave `SUPABASE_SERVICE_KEY` dá acesso total ao projeto. O arquivo `.gitignore` já ignora o `.env`.

---

## 🗄️ Configurando o Supabase

1. Crie um projeto em [supabase.com](https://supabase.com/).
2. Abra o **SQL Editor**, cole o conteúdo do arquivo [`supabase.sql`](supabase.sql) e clique em **Run**. Isso cria as tabelas `produtos` e `pedidos` e cadastra os 4 sabores.
3. Em **Project Settings → API**, copie a URL e as chaves para o seu `.env`.
4. Em **Authentication → URL Configuration**:
   - **Site URL**: o endereço do seu site publicado
   - **Redirect URLs**: adicione `https://SEU-SITE/redefinir` (e `http://127.0.0.1:5000/redefinir` para testar no computador)

Sem o passo 4, o link de "esqueci minha senha" não funciona.

Os dados do cliente (nome, telefone, rua, número, complemento e bairro) ficam guardados junto com a conta no próprio Supabase Auth.

---

## 💻 Rodando no seu computador

Você precisa ter o [Python](https://www.python.org/downloads/) instalado.

```bash
# 1. Entre na pasta do projeto
cd doce-arte-cupcakes

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instale as bibliotecas
pip install -r requirements.txt

# 4. Crie o arquivo .env (veja a seção de variáveis acima)

# 5. Ligue o site
python app.py
```

Abra no navegador: **http://127.0.0.1:5000**

---

## 🚀 Publicando na internet (Render)

1. Envie o projeto para o GitHub (sem o `.env`).
2. Em [render.com](https://render.com/), entre com o GitHub e clique em **New + → Web Service**.
3. Escolha este repositório e preencha:

   | Campo | Valor |
   |---|---|
   | Language | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app` |
   | Instance Type | `Free` |

4. Em **Environment Variables**, cadastre as mesmas variáveis do `.env`.
5. Clique em **Create Web Service**. Depois que o endereço for criado, adicione a variável `APP_URL` com ele (sem barra no final) e atualize a configuração de URLs no Supabase.

A cada atualização enviada ao GitHub, o Render publica a nova versão automaticamente.

> No plano gratuito do Render, o site "dorme" após alguns minutos sem acessos e pode levar cerca de 1 minuto para acordar no primeiro acesso.

---

## 📱 Instalando no celular como app

O site pode ser instalado no celular e abre em tela cheia, com o ícone da Doce Arte, como se fosse um aplicativo da loja. Não precisa de Play Store nem App Store, e é grátis.

> O site precisa estar publicado com endereço `https` (o Render já fornece). Instalar a partir do endereço local `127.0.0.1` não funciona no celular.

### Android (Chrome)

1. Abra o site no **Google Chrome**.
2. Toque nos **três pontinhos ⋮** no canto superior direito.
3. Toque em **Instalar app** (em alguns celulares aparece como **Adicionar à tela inicial**).
4. Confirme em **Instalar**.
5. O ícone 🧁 **Doce Arte** aparece na tela inicial do celular.

### iPhone (Safari)

1. Abra o site no **Safari** (é o navegador com o ícone de bússola).
2. Toque no botão **Compartilhar** (o quadrado com uma seta para cima, na barra de baixo).
3. Role as opções e toque em **Adicionar à Tela de Início**.
4. Toque em **Adicionar**, no canto superior direito.
5. O ícone 🧁 **Doce Arte** aparece na tela inicial do iPhone.

### Computador (Chrome ou Edge)

Na barra de endereço, clique no ícone de **instalar** (um monitor com uma seta) e depois em **Instalar**.

### Para divulgar aos clientes

Mande o endereço do site pelo WhatsApp ou Instagram junto com o passo a passo acima. Um QR Code do endereço, impresso na embalagem ou no cartão da loja, também ajuda: o cliente aponta a câmera, abre o site e instala.

### Se a opção de instalar não aparecer

- Confira se o site está abrindo com `https`.
- No Android, use o Chrome. No iPhone, use o Safari.
- Atualize a página algumas vezes e tente de novo.
- Se o app já foi instalado antes, a opção não aparece de novo.

---

## ✅ Testes automáticos

O projeto tem **75 testes automáticos** que conferem carrinho, pedidos, fotos, login, cadastro, nova senha, exclusão de conta e as páginas do site. Eles não acessam o Supabase de verdade (usam um banco de mentira), então rodam em menos de 1 segundo.

```bash
pip install -r requirements-dev.txt   # instala o pytest (uma vez só)
pytest                                # roda todos os testes
```

Sem instalar nada, também funciona: `python -m unittest discover -s tests -t . -v`

A lista completa dos testes está em [`docs/testes-automatizados.md`](docs/testes-automatizados.md).

---

## 🧭 Rotas do site

| Rota | O que faz |
|---|---|
| `/` | Cardápio |
| `/carrinho` | Carrinho e finalização do pedido |
| `/cadastro` | Criar conta |
| `/login` e `/sair` | Entrar e sair |
| `/esqueci-senha` | Pedir o link de nova senha |
| `/redefinir` | Criar a nova senha (abre pelo link do e-mail) |
| `/conta` | Minha conta |
| `/conta/excluir` | Exclui a conta (somente envio de formulário) |
| `/sw.js` e `/manifest.json` | Arquivos do app instalável |

---

## 🍰 Como adicionar ou mudar sabores

- **Novo sabor:** cadastre na tabela `produtos` do Supabase (**Table Editor**), com nome, descrição e preço.
- **Foto do sabor:** o site procura na pasta `static` um arquivo com o nome do sabor (ex.: `ninho.jpg`). Para um sabor novo, coloque a foto em `static/img/` e inclua a palavra do sabor na lista `SABORES` do arquivo `models/produto.py`. Outra opção é preencher a coluna `imagem_url` do produto com o link de uma imagem.
- **Preço ou descrição:** edite direto no Supabase, sem mexer no código.

---

## 🔒 Segurança e privacidade

- As chaves ficam em variáveis de ambiente, nunca no código.
- A tabela `pedidos` aceita apenas a criação de novos pedidos, e a tabela `produtos` aceita apenas leitura.
- Ao excluir a conta, o cadastro e o acesso do cliente são apagados. Os **pedidos já feitos continuam registrados** na tabela `pedidos` para controle da loja.
- A mensagem de "esqueci minha senha" é sempre a mesma, existindo o e-mail ou não, para não revelar quem tem cadastro.

---

## 📝 Observações

- O pedido não tem pagamento online: o cliente escolhe a forma de pagamento e combina o restante pelo WhatsApp.
- O app instalável (PWA) precisa de endereço seguro (`https`), que o Render já fornece. Veja como instalar na seção [Instalando no celular como app](#-instalando-no-celular-como-app).

---

Feito com carinho para a **Doce Arte Cupcakes** 💗
