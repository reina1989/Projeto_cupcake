# Testes automatizados

Este documento descreve os testes automáticos do site **Doce Arte Cupcakes**. Eles fazem a **verificação** do software: conferem, sem ninguém clicar, se o código faz o que foi especificado.

A **validação** (se o sistema atende o que o cliente espera) é feita com pessoas reais, nos testes com colegas descritos na pasta `docs/situacao-3-testes/`.

## Resultado da última execução

- **75 testes executados, 75 aprovados, 0 com falha**
- Data da execução: 12/11/2026
- Os testes não acessam o Supabase de verdade: usam um "banco de mentira" (`tests/ajudantes.py`). Assim rodam rápido, de graça e sem mexer em dados reais.

## Como rodar

```bash
pip install -r requirements-dev.txt   # instala o pytest (uma vez só)
pytest                                 # roda todos os testes
```

Sem instalar nada, também dá para rodar com o Python puro: `python -m unittest discover -s tests -t . -v`

## Tipos de teste

| Tipo | Onde | O que cobre |
|---|---|---|
| Unitário | `test_carrinho.py`, `test_pedido.py`, `test_produto.py`, `test_usuario.py` | Regras isoladas da camada **Model** |
| Integração | `test_rotas.py` | **Controller + View** funcionando juntos: páginas, sessão, redirecionamentos e mensagens |

## Casos de teste

### Carrinho de compras (`tests/test_carrinho.py`)

| Nº | O que é verificado | Resultado |
|---|---|---|
| 1 | Adicionar um produto novo coloca 1 unidade no carrinho. | ✅ Passou |
| 2 | Adicionar o mesmo produto duas vezes soma as quantidades. | ✅ Passou |
| 3 | A função devolve um carrinho novo e não mexe no original. | ✅ Passou |
| 4 | Subtotal e total são calculados com o preço de cada produto. | ✅ Passou |
| 5 | Carrinho vazio resulta em lista vazia e total zero. | ✅ Passou |
| 6 | A quantidade total soma todas as unidades. | ✅ Passou |
| 7 | Remover um item com 2 unidades deixa 1. | ✅ Passou |
| 8 | Remover um produto que não está no carrinho não causa erro. | ✅ Passou |
| 9 | Remover a última unidade tira o item do carrinho. | ✅ Passou |

### Pedido: mensagem do WhatsApp e gravação (`tests/test_pedido.py`)

| Nº | O que é verificado | Resultado |
|---|---|---|
| 10 | O link usa o número da loja e codifica espaços e quebras de linha. | ✅ Passou |
| 11 | A mensagem do WhatsApp traz cliente, itens, total, pagamento e endereço. | ✅ Passou |
| 12 | A lista do pedido mostra quantidade, nome e subtotal. | ✅ Passou |
| 13 | Só as formas de pagamento oferecidas pela loja são aceitas. | ✅ Passou |
| 14 | Se o banco falhar, salvar não derruba o site: devolve False. | ✅ Passou |
| 15 | Salvar envia os dados do cliente e do pedido para a tabela pedidos. | ✅ Passou |

### Produtos e fotos dos sabores (`tests/test_produto.py`)

| Nº | O que é verificado | Resultado |
|---|---|---|
| 16 | Sem arquivo do sabor, o resultado é None (e o site mostra o desenho). | ✅ Passou |
| 17 | A foto do sabor é encontrada mesmo dentro de uma subpasta. | ✅ Passou |
| 18 | Nome em maiúsculas e extensões como .PNG também funcionam. | ✅ Passou |
| 19 | Se o produto tem imagem_url no banco, ela é a usada. | ✅ Passou |
| 20 | 'Cupcake de Ninho' recebe a foto ninho.jpg que está na pasta static. | ✅ Passou |
| 21 | A lista de produtos vem com o campo 'imagem' preenchido. | ✅ Passou |
| 22 | Um sabor que não está na lista fica sem foto. | ✅ Passou |
| 23 | Se não achar o arquivo do sabor, devolve None. | ✅ Passou |

### Páginas do site: cardápio, carrinho, contas, nova senha e exclusão (`tests/test_rotas.py`)

| Nº | O que é verificado | Resultado |
|---|---|---|
| 24 | Os arquivos do app instalável são entregues com o tipo correto. | ✅ Passou |
| 25 | Clicar em Adicionar coloca o produto no carrinho. | ✅ Passou |
| 26 | O cardápio abre e mostra os produtos cadastrados. | ✅ Passou |
| 27 | Cada sabor aparece com a sua foto. | ✅ Passou |
| 28 | A página do carrinho soma o valor dos itens. | ✅ Passou |
| 29 | Sem login, o carrinho avisa que é preciso entrar para finalizar. | ✅ Passou |
| 30 | Sem itens, aparece a mensagem de carrinho vazio. | ✅ Passou |
| 31 | O menu mostra quantos itens há no carrinho. | ✅ Passou |
| 32 | O botão − tira uma unidade do carrinho. | ✅ Passou |
| 33 | Erro no cadastro mostra a mensagem amigável e mantém a página. | ✅ Passou |
| 34 | Cadastro válido avisa que a conta foi criada e abre o login. | ✅ Passou |
| 35 | Sem e-mail ou senha o cadastro nem é tentado. | ✅ Passou |
| 36 | O script do olhinho (mostrar/ocultar senha) está presente nas páginas. | ✅ Passou |
| 37 | Login válido deixa o cliente logado. | ✅ Passou |
| 38 | Login inválido mostra frase simples e não deixa logado. | ✅ Passou |
| 39 | Quem não entrou é levado ao login. | ✅ Passou |
| 40 | Logado, a página mostra nome e e-mail do cliente. | ✅ Passou |
| 41 | A tela de login oferece o caminho para recuperar a senha. | ✅ Passou |
| 42 | Sair tira o cliente da sessão. | ✅ Passou |
| 43 | Senha errada: mostra o aviso e a conta continua existindo. | ✅ Passou |
| 44 | Sem login, a exclusão leva à tela de login. | ✅ Passou |
| 45 | Conta excluída: o cliente sai do site e vê o aviso. | ✅ Passou |
| 46 | Sem itens não há o que finalizar. | ✅ Passou |
| 47 | Sem endereço o pedido não é enviado. | ✅ Passou |
| 48 | Forma de pagamento inventada é recusada e nada é salvo. | ✅ Passou |
| 49 | Logado: o pedido é salvo, o carrinho esvazia e abre o WhatsApp com a mensagem. | ✅ Passou |
| 50 | Quem não está logado não consegue finalizar o pedido. | ✅ Passou |
| 51 | Outro erro (ex.: senha repetida) mostra o motivo e deixa tentar de novo. | ✅ Passou |
| 52 | Link vencido leva à tela de pedir um novo link. | ✅ Passou |
| 53 | A página para criar a nova senha abre e tem os dois campos. | ✅ Passou |
| 54 | A resposta não revela se o e-mail tem cadastro. | ✅ Passou |
| 55 | Sem o token do e-mail não dá para trocar a senha. | ✅ Passou |
| 56 | Senhas diferentes: mostra aviso e mantém o token para tentar de novo. | ✅ Passou |
| 57 | Senha trocada: avisa e abre o login. | ✅ Passou |

### Contas de clientes: login, cadastro, nova senha e exclusão (`tests/test_usuario.py`)

| Nº | O que é verificado | Resultado |
|---|---|---|
| 58 | Senha correta: a conta do próprio cliente é apagada no Supabase. | ✅ Passou |
| 59 | Se o Supabase recusar a exclusão, o cliente recebe uma mensagem simples. | ✅ Passou |
| 60 | Sem a chave service_role configurada, a exclusão avisa que não está ativa. | ✅ Passou |
| 61 | Com senha errada a conta não é apagada e o DELETE nem é chamado. | ✅ Passou |
| 62 | E-mail já cadastrado mostra uma frase clara. | ✅ Passou |
| 63 | O cadastro envia e-mail, senha e os dados extras (nome, rua...). | ✅ Passou |
| 64 | Senha errada levanta ErroUsuario com texto simples. | ✅ Passou |
| 65 | Login correto devolve nome, e-mail e dados guardados na conta. | ✅ Passou |
| 66 | Se a conta não tem nome, usa a parte do e-mail antes do @. | ✅ Passou |
| 67 | Um erro que não conhecemos mostra a mensagem padrão, sem detalhes técnicos. | ✅ Passou |
| 68 | Erros técnicos do Supabase viram frases simples em português. | ✅ Passou |
| 69 | Falha de rede vira mensagem simples. | ✅ Passou |
| 70 | Token vencido (erro 401) levanta LinkVencido. | ✅ Passou |
| 71 | O pedido ao Supabase leva o endereço do site + /redefinir. | ✅ Passou |
| 72 | Mesmo com falha de rede, o cliente não vê erro (nem descobre se o e-mail existe). | ✅ Passou |
| 73 | Com um token válido a senha é trocada sem erro. | ✅ Passou |
| 74 | Senha fraca demais é recusada com explicação. | ✅ Passou |
| 75 | Repetir a senha antiga mostra a explicação correta. | ✅ Passou |
