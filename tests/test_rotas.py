"""Testes de ponta a ponta das páginas (controllers + templates), com banco de mentira."""
import unittest
from unittest.mock import patch

from models.usuario import ErroUsuario, LinkVencido
from tests.ajudantes import (PERFIL_EXEMPLO, BancoFalso, novo_navegador,
                             preparar_sessao)


class TesteBase(unittest.TestCase):
    def setUp(self):
        self.app, self.site = novo_navegador()
        self.banco = BancoFalso()
        for alvo in ("models.produto.cliente_compartilhado", "models.pedido.cliente_compartilhado"):
            patcher = patch(alvo, return_value=self.banco)
            patcher.start()
            self.addCleanup(patcher.stop)

    def pagina(self, endereco, **opcoes):
        resposta = self.site.get(endereco, follow_redirects=True, **opcoes)
        return resposta, resposta.get_data(as_text=True)

    def sessao(self):
        with self.site.session_transaction() as sessao:
            return dict(sessao)


class TesteCardapioECarrinho(TesteBase):

    def test_cardapio_lista_os_produtos(self):
        """O cardápio abre e mostra os produtos cadastrados."""
        resposta, html = self.pagina("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Cupcake de Baunilha", html)
        self.assertIn("R$ 8.00", html)

    def test_cardapio_mostra_a_foto_do_sabor(self):
        """Cada sabor aparece com a sua foto."""
        _, html = self.pagina("/")
        self.assertIn("/static/img/baunilha.jpg", html)
        self.assertIn("/static/img/ninho.jpg", html)

    def test_adicionar_ao_carrinho_guarda_na_sessao(self):
        """Clicar em Adicionar coloca o produto no carrinho."""
        self.site.post("/add/1")
        self.assertEqual(self.sessao()["carrinho"], {"1": 1})

    def test_contador_do_carrinho_aparece_no_menu(self):
        """O menu mostra quantos itens há no carrinho."""
        preparar_sessao(self.site, carrinho={"1": 2})
        _, html = self.pagina("/")
        self.assertIn("Carrinho (2)", html)

    def test_carrinho_mostra_o_total(self):
        """A página do carrinho soma o valor dos itens."""
        preparar_sessao(self.site, carrinho={"1": 2})
        _, html = self.pagina("/carrinho")
        self.assertIn("Total: R$ 16.00", html)

    def test_carrinho_vazio_mostra_aviso(self):
        """Sem itens, aparece a mensagem de carrinho vazio."""
        _, html = self.pagina("/carrinho")
        self.assertIn("Seu carrinho está vazio", html)

    def test_remover_tira_uma_unidade(self):
        """O botão − tira uma unidade do carrinho."""
        preparar_sessao(self.site, carrinho={"1": 2})
        self.site.post("/remover/1")
        self.assertEqual(self.sessao()["carrinho"], {"1": 1})

    def test_carrinho_sem_login_pede_para_entrar(self):
        """Sem login, o carrinho avisa que é preciso entrar para finalizar."""
        preparar_sessao(self.site, carrinho={"1": 1})
        _, html = self.pagina("/carrinho")
        self.assertIn("você precisa entrar na sua conta", html)


class TesteFinalizarPedido(TesteBase):

    DADOS = {"endereco": "Rua A, 10", "pagamento": "Pix"}

    def test_sem_login_vai_para_a_tela_de_login(self):
        """Quem não está logado não consegue finalizar o pedido."""
        preparar_sessao(self.site, carrinho={"1": 1})
        resposta = self.site.post("/finalizar", data=self.DADOS)
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].endswith("/login"))

    def test_pedido_vai_para_o_whatsapp_e_e_salvo(self):
        """Logado: o pedido é salvo, o carrinho esvazia e abre o WhatsApp com a mensagem."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO, carrinho={"1": 2})
        resposta = self.site.post("/finalizar", data=self.DADOS)
        self.assertTrue(resposta.headers["Location"].startswith("https://wa.me/"))
        self.assertIn("Cupcake%20de%20Baunilha", resposta.headers["Location"])
        self.assertEqual(len(self.banco.tabelas["pedidos"].inseridos), 1)
        self.assertEqual(self.sessao()["carrinho"], {})

    def test_carrinho_vazio_volta_para_o_carrinho(self):
        """Sem itens não há o que finalizar."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO)
        resposta = self.site.post("/finalizar", data=self.DADOS)
        self.assertTrue(resposta.headers["Location"].endswith("/carrinho"))

    def test_pagamento_invalido_nao_salva(self):
        """Forma de pagamento inventada é recusada e nada é salvo."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO, carrinho={"1": 1})
        resposta = self.site.post("/finalizar", data={"endereco": "Rua A", "pagamento": "Fiado"},
                                  follow_redirects=True)
        self.assertIn("forma de pagamento válida", resposta.get_data(as_text=True))
        self.assertEqual(self.banco.tabelas["pedidos"].inseridos, [])

    def test_endereco_vazio_nao_salva(self):
        """Sem endereço o pedido não é enviado."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO, carrinho={"1": 1})
        resposta = self.site.post("/finalizar", data={"endereco": "  ", "pagamento": "Pix"},
                                  follow_redirects=True)
        self.assertIn("Informe o endereço", resposta.get_data(as_text=True))
        self.assertEqual(self.banco.tabelas["pedidos"].inseridos, [])


class TesteContas(TesteBase):

    def test_login_correto_guarda_o_perfil_e_vai_para_o_cardapio(self):
        """Login válido deixa o cliente logado."""
        with patch("models.usuario.entrar", return_value=PERFIL_EXEMPLO):
            resposta = self.site.post("/login", data={"email": "maria@exemplo.com", "senha": "123456"})
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.sessao()["perfil"]["nome"], "Maria")

    def test_login_errado_mostra_mensagem_amigavel(self):
        """Login inválido mostra frase simples e não deixa logado."""
        with patch("models.usuario.entrar", side_effect=ErroUsuario("E-mail ou senha incorretos.")):
            resposta = self.site.post("/login", data={"email": "a@b.com", "senha": "x"})
        self.assertIn("E-mail ou senha incorretos.", resposta.get_data(as_text=True))
        self.assertNotIn("perfil", self.sessao())

    def test_pagina_de_login_tem_link_esqueci_minha_senha(self):
        """A tela de login oferece o caminho para recuperar a senha."""
        _, html = self.pagina("/login")
        self.assertIn("Esqueci minha senha", html)

    def test_campos_de_senha_recebem_o_olhinho(self):
        """O script do olhinho (mostrar/ocultar senha) está presente nas páginas."""
        for endereco in ("/login", "/cadastro"):
            _, html = self.pagina(endereco)
            self.assertIn("senha-wrap", html)

    def test_cadastro_com_sucesso_vai_para_o_login(self):
        """Cadastro válido avisa que a conta foi criada e abre o login."""
        with patch("models.usuario.cadastrar"):
            resposta = self.site.post("/cadastro", data={"email": "a@b.com", "senha": "123456", "nome": "Ana"},
                                      follow_redirects=True)
        self.assertIn("Conta criada!", resposta.get_data(as_text=True))

    def test_cadastro_com_erro_mostra_mensagem(self):
        """Erro no cadastro mostra a mensagem amigável e mantém a página."""
        with patch("models.usuario.cadastrar", side_effect=ErroUsuario("Esse e-mail já tem cadastro. Tente entrar.")):
            resposta = self.site.post("/cadastro", data={"email": "a@b.com", "senha": "123456"})
        self.assertIn("já tem cadastro", resposta.get_data(as_text=True))

    def test_cadastro_sem_email_ou_senha(self):
        """Sem e-mail ou senha o cadastro nem é tentado."""
        with patch("models.usuario.cadastrar") as cadastrar:
            resposta = self.site.post("/cadastro", data={"email": "", "senha": ""})
        self.assertIn("Preencha o e-mail e a senha", resposta.get_data(as_text=True))
        cadastrar.assert_not_called()

    def test_sair_remove_o_login(self):
        """Sair tira o cliente da sessão."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO)
        self.site.get("/sair")
        self.assertNotIn("perfil", self.sessao())

    def test_minha_conta_exige_login(self):
        """Quem não entrou é levado ao login."""
        resposta = self.site.get("/conta")
        self.assertTrue(resposta.headers["Location"].endswith("/login"))

    def test_minha_conta_mostra_os_dados(self):
        """Logado, a página mostra nome e e-mail do cliente."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO)
        _, html = self.pagina("/conta")
        self.assertIn("maria@exemplo.com", html)
        self.assertIn("Excluir minha conta", html)


class TesteRecuperarSenha(TesteBase):

    def test_pedido_de_link_sempre_mostra_a_mesma_mensagem(self):
        """A resposta não revela se o e-mail tem cadastro."""
        with patch("models.usuario.pedir_link_nova_senha") as pedir:
            resposta = self.site.post("/esqueci-senha", data={"email": "qualquer@exemplo.com"},
                                      follow_redirects=True)
        pedir.assert_called_once()
        self.assertIn("Se esse e-mail tiver cadastro", resposta.get_data(as_text=True))

    def test_pagina_de_nova_senha_abre(self):
        """A página para criar a nova senha abre e tem os dois campos."""
        _, html = self.pagina("/redefinir")
        self.assertIn('name="senha"', html)
        self.assertIn('name="senha2"', html)

    def test_senhas_diferentes_mantem_a_pagina_e_o_link(self):
        """Senhas diferentes: mostra aviso e mantém o token para tentar de novo."""
        resposta = self.site.post("/redefinir", data={"token": "T0K", "senha": "123456", "senha2": "654321"})
        html = resposta.get_data(as_text=True)
        self.assertIn("precisam ser iguais", html)
        self.assertIn('value="T0K"', html)

    def test_troca_com_sucesso_vai_para_o_login(self):
        """Senha trocada: avisa e abre o login."""
        with patch("models.usuario.trocar_senha"):
            resposta = self.site.post("/redefinir", data={"token": "T", "senha": "nova123", "senha2": "nova123"},
                                      follow_redirects=True)
        self.assertIn("Senha alterada!", resposta.get_data(as_text=True))

    def test_link_vencido_pede_novo_link(self):
        """Link vencido leva à tela de pedir um novo link."""
        with patch("models.usuario.trocar_senha", side_effect=LinkVencido("Esse link venceu ou já foi usado. Peça um novo.")):
            resposta = self.site.post("/redefinir", data={"token": "T", "senha": "nova123", "senha2": "nova123"})
        self.assertTrue(resposta.headers["Location"].endswith("/esqueci-senha"))

    def test_erro_ao_trocar_mostra_motivo_e_mantem_o_formulario(self):
        """Outro erro (ex.: senha repetida) mostra o motivo e deixa tentar de novo."""
        with patch("models.usuario.trocar_senha", side_effect=ErroUsuario("A nova senha precisa ser diferente da senha anterior.")):
            resposta = self.site.post("/redefinir", data={"token": "T0K", "senha": "antiga1", "senha2": "antiga1"})
        html = resposta.get_data(as_text=True)
        self.assertIn("diferente da senha anterior", html)
        self.assertIn('value="T0K"', html)

    def test_sem_token_pede_novo_link(self):
        """Sem o token do e-mail não dá para trocar a senha."""
        resposta = self.site.post("/redefinir", data={"senha": "nova123", "senha2": "nova123"})
        self.assertTrue(resposta.headers["Location"].endswith("/esqueci-senha"))


class TesteExcluirConta(TesteBase):

    def test_exige_login(self):
        """Sem login, a exclusão leva à tela de login."""
        resposta = self.site.post("/conta/excluir", data={"senha": "123456"})
        self.assertTrue(resposta.headers["Location"].endswith("/login"))

    def test_sucesso_limpa_a_sessao(self):
        """Conta excluída: o cliente sai do site e vê o aviso."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO)
        with patch("models.usuario.excluir_conta") as excluir:
            resposta = self.site.post("/conta/excluir", data={"senha": "123456"}, follow_redirects=True)
        excluir.assert_called_once_with("maria@exemplo.com", "123456")
        self.assertIn("Sua conta foi excluída", resposta.get_data(as_text=True))
        self.assertNotIn("perfil", self.sessao())

    def test_erro_mantem_o_cliente_logado(self):
        """Senha errada: mostra o aviso e a conta continua existindo."""
        preparar_sessao(self.site, perfil=PERFIL_EXEMPLO)
        with patch("models.usuario.excluir_conta", side_effect=ErroUsuario("Senha incorreta. Sua conta não foi excluída.")):
            resposta = self.site.post("/conta/excluir", data={"senha": "errada"}, follow_redirects=True)
        self.assertIn("Senha incorreta", resposta.get_data(as_text=True))
        self.assertIn("perfil", self.sessao())


class TesteAppInstalavel(TesteBase):

    def test_manifesto_e_service_worker_tem_o_tipo_certo(self):
        """Os arquivos do app instalável são entregues com o tipo correto."""
        with self.site.get("/manifest.json") as manifesto:
            self.assertEqual(manifesto.status_code, 200)
            self.assertIn("application/manifest+json", manifesto.headers["Content-Type"])
        with self.site.get("/sw.js") as sw:
            self.assertIn("application/javascript", sw.headers["Content-Type"])
            self.assertEqual(sw.headers["Service-Worker-Allowed"], "/")


if __name__ == "__main__":
    unittest.main()
