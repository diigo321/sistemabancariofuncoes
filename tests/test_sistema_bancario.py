import io
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import sistema_bancario as banco


class SistemaBancarioTests(unittest.TestCase):
    def setUp(self):
        self.saida = io.StringIO()
        self.redirecionamento = redirect_stdout(self.saida)
        self.redirecionamento.__enter__()
        self.addCleanup(self.redirecionamento.__exit__, None, None, None)

    def sacar(self, valor, saldo="1000.00", numero_saques=0):
        return banco.sacar(
            saldo=Decimal(saldo), valor=Decimal(valor), extrato="",
            limite=banco.LIMITE, numero_saques=numero_saques,
            limite_saques=banco.LIMITE_SAQUES,
        )

    def usuario(self, usuarios):
        return banco.cadastrar_usuario(
            usuarios, nome="Pessoa de Teste", data_nascimento="01/01/2000",
            cpf="123.456.789-00", endereco="Rua Exemplo, 1 - Centro - Cidade/UF",
        )

    def test_deposito_com_precisao_de_centavos(self):
        saldo, extrato = banco.depositar(Decimal("0.10"), Decimal("0.20"), "")
        self.assertEqual(saldo, Decimal("0.30"))
        self.assertIn("Depósito: R$ 0.20", extrato)

    def test_depositos_invalidos_nao_alteram_estado(self):
        for valor in ["0", "-1", "NaN", "Infinity", "0.001"]:
            with self.subTest(valor=valor):
                self.assertEqual(banco.depositar(Decimal("10"), Decimal(valor), "antes"),
                                 (Decimal("10"), "antes"))

    def test_saque_no_limite(self):
        saldo, extrato, contador = self.sacar("500")
        self.assertEqual(saldo, Decimal("500"))
        self.assertIn("Saque: R$ 500.00", extrato)
        self.assertEqual(contador, 1)

    def test_saldo_insuficiente(self):
        self.assertEqual(self.sacar("100", saldo="50"), (Decimal("50"), "", 0))

    def test_saque_acima_do_limite(self):
        self.assertEqual(self.sacar("500.01"), (Decimal("1000"), "", 0))

    def test_tres_saques_e_quarto_bloqueado(self):
        saldo, extrato, contador = Decimal("1000"), "", 0
        for _ in range(4):
            saldo, extrato, contador = banco.sacar(
                saldo=saldo, valor=Decimal("100"), extrato=extrato,
                limite=banco.LIMITE, numero_saques=contador, limite_saques=3,
            )
        self.assertEqual((saldo, contador), (Decimal("700"), 3))
        self.assertEqual(extrato.count("Saque:"), 3)

    def test_saque_invalido_nao_incrementa_contador(self):
        for valor in ["0", "-1", "NaN", "Infinity", "0.001"]:
            with self.subTest(valor=valor):
                self.assertEqual(self.sacar(valor), (Decimal("1000"), "", 0))

    def test_extrato_vazio(self):
        banco.exibir_extrato(Decimal("0"), extrato="")
        self.assertIn("Não foram realizadas movimentações.", self.saida.getvalue())
        self.assertIn("Saldo: R$ 0.00", self.saida.getvalue())

    def test_cpf_formatado_e_duplicado(self):
        usuarios = []
        usuario = self.usuario(usuarios)
        self.assertEqual(usuario["cpf"], "12345678900")
        self.assertIs(banco.filtrar_usuario("12345678900", usuarios), usuario)
        with self.assertRaises(ValueError):
            self.usuario(usuarios)
        self.assertEqual(len(usuarios), 1)

    def test_cpf_e_data_invalidos(self):
        for cpf in ["123", "abcdefghijk", "１２３４５６７８９００"]:
            with self.subTest(cpf=cpf), self.assertRaises(ValueError):
                banco.normalizar_cpf(cpf)
        usuarios = []
        with self.assertRaises(ValueError):
            banco.cadastrar_usuario(usuarios, nome="Teste", cpf="12345678900",
                                    data_nascimento="31/02/2000", endereco="Rua")
        self.assertEqual(usuarios, [])

    def test_conta_exige_usuario(self):
        with self.assertRaises(ValueError):
            banco.criar_conta("0001", 1, [], "12345678900")

    def test_duas_contas_independentes(self):
        usuarios = []
        usuario = self.usuario(usuarios)
        primeira = banco.criar_conta("0001", 1, usuarios, usuario["cpf"])
        segunda = banco.criar_conta("0001", 2, usuarios, usuario["cpf"])
        primeira["saldo"], primeira["extrato"] = banco.depositar(
            primeira["saldo"], Decimal("50"), primeira["extrato"]
        )
        self.assertEqual(segunda["saldo"], Decimal("0"))
        self.assertEqual(segunda["extrato"], "")
        self.assertEqual(segunda["numero_saques"], 0)
        self.assertIs(primeira["usuario"], segunda["usuario"])

    def test_limite_diario_reinicia_so_no_proximo_dia(self):
        hoje = date(2026, 10, 5)
        conta = {"data_saques": hoje, "numero_saques": 3}
        banco.atualizar_limite_diario(conta, hoje)
        self.assertEqual(conta["numero_saques"], 3)
        banco.atualizar_limite_diario(conta, hoje + timedelta(days=1))
        self.assertEqual(conta["numero_saques"], 0)

    def test_regras_de_passagem_de_argumentos(self):
        with self.assertRaises(TypeError):
            banco.depositar(saldo=Decimal("0"), valor=Decimal("1"), extrato="")
        with self.assertRaises(TypeError):
            banco.sacar(Decimal("10"), Decimal("1"), "", Decimal("500"), 0, 3)
        with self.assertRaises(TypeError):
            banco.exibir_extrato(Decimal("0"), "")

    def test_menu_com_cadastro_deposito_saque_e_extrato(self):
        entradas = ["nu", "12345678900", "Pessoa Teste", "01/01/2000", "Rua Exemplo",
                    "nc", "12345678900", "d", "100,50", "s", "25", "e", "q"]
        with patch("builtins.input", side_effect=entradas):
            banco.main()
        saida = self.saida.getvalue()
        self.assertIn("Usuário cadastrado com sucesso!", saida)
        self.assertIn("Conta 1 criada e selecionada!", saida)
        self.assertIn("Saldo: R$ 75.50", saida)

    def test_menu_resiste_a_entrada_invalida(self):
        with patch("builtins.input", side_effect=["d", "invalido", "q"]):
            banco.main()
        self.assertIn("Cadastre um usuário", self.saida.getvalue())
        self.assertIn("Opção inválida", self.saida.getvalue())


if __name__ == "__main__":
    unittest.main()
