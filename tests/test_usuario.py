"""Testes das contas de clientes (models/usuario.py), sem acessar o Supabase de verdade."""
import unittest
from unittest.mock import patch

from configuracao import Config
from models import usuario
from models.usuario import ErroUsuario, LinkVencido
from tests.ajudantes import cliente_auth_falso, resposta_falsa


class TesteMensagensDeErro(unittest.TestCase):

    def test_traduz_erros_conhecidos(self):
        """Erros técnicos do Supabase viram frases simples em português."""
        casos = {
            "Invalid login credentials": "E-mail ou senha incorretos.",
            "Email not confirmed": "Confirme seu e-mail antes de entrar. Veja sua caixa de entrada.",
            "User already registered": "Esse e-mail já tem cadastro. Tente entrar.",
            "Password should be at least 6 characters": "A senha precisa ter pelo menos 6 caracteres.",
            "Email rate limit exceeded": "Muitas tentativas. Aguarde alguns minutos e tente de novo.",
        }
        for tecnico, amigavel in casos.items():
            self.assertEqual(usuario.traduzir_erro(Exception(tecnico)), amigavel)

    def test_erro_desconhecido_vira_mensagem_padrao(self):
        """Um erro que não conhecemos mostra a mensagem padrão, sem detalhes técnicos."""
        self.assertEqual(usuario.traduzir_erro(Exception("xyz 500")), usuario.MENSAGEM_PADRAO)


class TesteLoginECadastro(unittest.TestCase):

    def test_entrar_devolve_o_perfil_do_cliente(self):
        """Login correto devolve nome, e-mail e dados guardados na conta."""
        cliente = cliente_auth_falso(metadados={"nome": "Maria", "rua": "Rua A"})
        with patch("models.usuario.cliente_novo", return_value=cliente):
            perfil = usuario.entrar("maria@exemplo.com", "123456")
        self.assertEqual(perfil["nome"], "Maria")
        self.assertEqual(perfil["email"], "maria@exemplo.com")
        self.assertEqual(perfil["rua"], "Rua A")

    def test_entrar_sem_nome_usa_o_comeco_do_email(self):
        """Se a conta não tem nome, usa a parte do e-mail antes do @."""
        with patch("models.usuario.cliente_novo", return_value=cliente_auth_falso(metadados=None)):
            self.assertEqual(usuario.entrar("maria@exemplo.com", "123456")["nome"], "maria")

    def test_entrar_com_senha_errada_da_mensagem_amigavel(self):
        """Senha errada levanta ErroUsuario com texto simples."""
        cliente = cliente_auth_falso(erro=Exception("Invalid login credentials"))
        with patch("models.usuario.cliente_novo", return_value=cliente):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.entrar("maria@exemplo.com", "errada")
        self.assertEqual(str(ctx.exception), "E-mail ou senha incorretos.")

    def test_cadastrar_envia_os_dados_junto_com_a_conta(self):
        """O cadastro envia e-mail, senha e os dados extras (nome, rua...)."""
        cliente = cliente_auth_falso()
        with patch("models.usuario.cliente_novo", return_value=cliente):
            usuario.cadastrar("a@b.com", "123456", {"nome": "Ana"})
        recebido = cliente.auth.sign_up.recebido
        self.assertEqual(recebido["email"], "a@b.com")
        self.assertEqual(recebido["options"]["data"], {"nome": "Ana"})

    def test_cadastrar_email_repetido_da_mensagem_amigavel(self):
        """E-mail já cadastrado mostra uma frase clara."""
        cliente = cliente_auth_falso(erro=Exception("User already registered"))
        with patch("models.usuario.cliente_novo", return_value=cliente):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.cadastrar("a@b.com", "123456", {})
        self.assertIn("já tem cadastro", str(ctx.exception))


class TesteNovaSenha(unittest.TestCase):

    def test_pedir_link_envia_o_endereco_de_volta_correto(self):
        """O pedido ao Supabase leva o endereço do site + /redefinir."""
        with patch("models.usuario.requests.post") as envio:
            usuario.pedir_link_nova_senha("a@b.com", "https://meusite.com/")
        argumentos = envio.call_args.kwargs
        self.assertEqual(argumentos["params"], {"redirect_to": "https://meusite.com/redefinir"})
        self.assertEqual(argumentos["json"], {"email": "a@b.com"})

    def test_pedir_link_nao_levanta_erro_se_a_internet_falhar(self):
        """Mesmo com falha de rede, o cliente não vê erro (nem descobre se o e-mail existe)."""
        with patch("models.usuario.requests.post", side_effect=RuntimeError("sem rede")):
            usuario.pedir_link_nova_senha("a@b.com", "https://meusite.com")

    def test_trocar_senha_com_sucesso(self):
        """Com um token válido a senha é trocada sem erro."""
        with patch("models.usuario.requests.put", return_value=resposta_falsa(ok=True)) as troca:
            usuario.trocar_senha("TOKEN", "nova123")
        self.assertEqual(troca.call_args.kwargs["json"], {"password": "nova123"})
        self.assertEqual(troca.call_args.kwargs["headers"]["Authorization"], "Bearer TOKEN")

    def test_trocar_senha_igual_a_anterior(self):
        """Repetir a senha antiga mostra a explicação correta."""
        resposta = resposta_falsa(ok=False, status=422, json={"error_code": "same_password"})
        with patch("models.usuario.requests.put", return_value=resposta):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.trocar_senha("TOKEN", "antiga")
        self.assertIn("diferente da senha anterior", str(ctx.exception))

    def test_trocar_senha_fraca(self):
        """Senha fraca demais é recusada com explicação."""
        resposta = resposta_falsa(ok=False, status=422, json={"error_code": "weak_password"})
        with patch("models.usuario.requests.put", return_value=resposta):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.trocar_senha("TOKEN", "123456")
        self.assertIn("fraca", str(ctx.exception))

    def test_link_vencido(self):
        """Token vencido (erro 401) levanta LinkVencido."""
        with patch("models.usuario.requests.put", return_value=resposta_falsa(ok=False, status=401)):
            with self.assertRaises(LinkVencido):
                usuario.trocar_senha("VELHO", "nova123")

    def test_falha_de_rede_ao_trocar_senha(self):
        """Falha de rede vira mensagem simples."""
        with patch("models.usuario.requests.put", side_effect=RuntimeError("sem rede")):
            with self.assertRaises(ErroUsuario):
                usuario.trocar_senha("TOKEN", "nova123")


class TesteExclusaoDeConta(unittest.TestCase):

    def test_sem_chave_de_servico_nao_exclui(self):
        """Sem a chave service_role configurada, a exclusão avisa que não está ativa."""
        with patch.object(Config, "SUPABASE_SERVICE_KEY", ""):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.excluir_conta("a@b.com", "123456")
        self.assertIn("não foi configurada", str(ctx.exception))

    def test_senha_incorreta_nao_exclui(self):
        """Com senha errada a conta não é apagada e o DELETE nem é chamado."""
        cliente = cliente_auth_falso(erro=Exception("Invalid login credentials"))
        with patch.object(Config, "SUPABASE_SERVICE_KEY", "chave"), \
                patch("models.usuario.cliente_novo", return_value=cliente), \
                patch("models.usuario.requests.delete") as apagar:
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.excluir_conta("a@b.com", "errada")
        self.assertIn("Senha incorreta", str(ctx.exception))
        apagar.assert_not_called()

    def test_exclusao_com_sucesso_apaga_o_usuario_certo(self):
        """Senha correta: a conta do próprio cliente é apagada no Supabase."""
        with patch.object(Config, "SUPABASE_SERVICE_KEY", "chave"), \
                patch.object(Config, "SUPABASE_URL", "https://x.supabase.co"), \
                patch("models.usuario.cliente_novo", return_value=cliente_auth_falso(id_usuario="u-1")), \
                patch("models.usuario.requests.delete", return_value=resposta_falsa(ok=True)) as apagar:
            usuario.excluir_conta("a@b.com", "123456")
        self.assertEqual(apagar.call_args.args[0], "https://x.supabase.co/auth/v1/admin/users/u-1")

    def test_falha_ao_apagar_mostra_mensagem(self):
        """Se o Supabase recusar a exclusão, o cliente recebe uma mensagem simples."""
        with patch.object(Config, "SUPABASE_SERVICE_KEY", "chave"), \
                patch("models.usuario.cliente_novo", return_value=cliente_auth_falso()), \
                patch("models.usuario.requests.delete", return_value=resposta_falsa(ok=False, status=500)):
            with self.assertRaises(ErroUsuario) as ctx:
                usuario.excluir_conta("a@b.com", "123456")
        self.assertIn("Não foi possível excluir", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
