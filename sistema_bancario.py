"""Sistema bancário com funções — desafio de projeto DIO.

Dados ficam em memória. Execute com Python 3.10 ou superior.
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

AGENCIA = "0001"
LIMITE = Decimal("500.00")
LIMITE_SAQUES = 3
CENTAVO = Decimal("0.01")


def valor_valido(valor):
    return (
        isinstance(valor, Decimal)
        and valor.is_finite()
        and valor > 0
        and valor.as_tuple().exponent >= -2
    )


def ler_valor(mensagem):
    try:
        valor = Decimal(input(mensagem).strip().replace(",", "."))
        if not valor_valido(valor):
            raise ValueError
        return valor
    except (InvalidOperation, ValueError):
        print("Valor inválido. Use um número positivo com até duas casas decimais.")
        return None


def depositar(saldo, valor, extrato, /):
    """Recebe argumentos apenas por posição e retorna saldo e histórico."""
    if not valor_valido(valor):
        print("Depósito recusado: valor inválido.")
        return saldo, extrato
    saldo += valor
    extrato += f"Depósito: R$ {valor:.2f}\n"
    print("Depósito realizado com sucesso!")
    return saldo, extrato


def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    """Recebe argumentos nomeados e devolve também o contador atualizado."""
    if not valor_valido(valor):
        print("Saque recusado: valor inválido.")
    elif numero_saques >= limite_saques:
        print("Limite de 3 saques diários atingido.")
    elif valor > limite:
        print(f"O limite por saque é R$ {limite:.2f}.")
    elif valor > saldo:
        print("Saldo insuficiente.")
    else:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        print("Saque realizado com sucesso!")
    return saldo, extrato, numero_saques


def exibir_extrato(saldo, /, *, extrato):
    """Saldo por posição; extrato como argumento nomeado."""
    print("\n================ EXTRATO ================")
    print(extrato if extrato else "Não foram realizadas movimentações.")
    print(f"Saldo: R$ {saldo:.2f}")
    print("=========================================")


def normalizar_cpf(cpf):
    cpf = cpf.strip().replace(".", "").replace("-", "")
    if len(cpf) != 11 or not cpf.isascii() or not cpf.isdigit():
        raise ValueError("CPF deve conter 11 dígitos.")
    return cpf


def filtrar_usuario(cpf, usuarios):
    cpf = normalizar_cpf(cpf)
    return next((usuario for usuario in usuarios if usuario["cpf"] == cpf), None)


def cadastrar_usuario(usuarios, *, nome, data_nascimento, cpf, endereco):
    """Valida o cadastro e impede CPFs duplicados."""
    cpf = normalizar_cpf(cpf)
    if filtrar_usuario(cpf, usuarios):
        raise ValueError("Já existe usuário com esse CPF.")
    if not nome.strip() or not endereco.strip():
        raise ValueError("Nome e endereço são obrigatórios.")
    nascimento = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
    if nascimento > date.today():
        raise ValueError("A data de nascimento não pode estar no futuro.")
    usuario = {
        "nome": nome.strip(),
        "data_nascimento": nascimento.strftime("%d/%m/%Y"),
        "cpf": cpf,
        "endereco": endereco.strip(),
    }
    usuarios.append(usuario)
    return usuario


def criar_usuario(usuarios):
    try:
        cpf = input("CPF (11 dígitos): ")
        if filtrar_usuario(cpf, usuarios):
            print("Já existe usuário com esse CPF.")
            return
        cadastrar_usuario(
            usuarios,
            cpf=cpf,
            nome=input("Nome completo: "),
            data_nascimento=input("Nascimento (dd/mm/aaaa): "),
            endereco=input("Endereço (logradouro, número - bairro - cidade/UF): "),
        )
        print("Usuário cadastrado com sucesso!")
    except ValueError as erro:
        print(f"Cadastro recusado: {erro}")


def criar_conta(agencia, numero_conta, usuarios, cpf):
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario is None:
        raise ValueError("Usuário não encontrado. Cadastre-o antes de criar uma conta.")
    return {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "usuario": usuario,
        "saldo": Decimal("0.00"),
        "extrato": "",
        "numero_saques": 0,
        "data_saques": date.today(),
    }


def listar_contas(contas):
    if not contas:
        print("Nenhuma conta cadastrada.")
    for conta in contas:
        print(
            f"Agência: {conta['agencia']} | Conta: {conta['numero_conta']} "
            f"| Titular: {conta['usuario']['nome']}"
        )


def atualizar_limite_diario(conta, hoje=None):
    hoje = date.today() if hoje is None else hoje
    if conta["data_saques"] != hoje:
        conta["numero_saques"] = 0
        conta["data_saques"] = hoje


def selecionar_conta(contas):
    listar_contas(contas)
    try:
        numero = int(input("Número da conta: "))
        conta = next((c for c in contas if c["numero_conta"] == numero), None)
        if conta is None:
            print("Conta não encontrada.")
        return conta
    except ValueError:
        print("Informe um número de conta válido.")
        return None


def menu():
    return input(
        "\n[d] Depositar\n[s] Sacar\n[e] Extrato\n"
        "[nu] Novo usuário\n[nc] Nova conta\n[lc] Listar contas\n"
        "[ac] Alterar conta ativa\n[q] Sair\n=> "
    ).strip().lower()


def main():
    usuarios, contas = [], []
    conta_ativa = None
    while True:
        opcao = menu()
        if opcao == "q":
            print("Até logo!")
            break
        if opcao == "nu":
            criar_usuario(usuarios)
        elif opcao == "nc":
            try:
                conta = criar_conta(AGENCIA, len(contas) + 1, usuarios, input("CPF do titular: "))
                contas.append(conta)
                conta_ativa = conta
                print(f"Conta {conta['numero_conta']} criada e selecionada!")
            except ValueError as erro:
                print(f"Conta não criada: {erro}")
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "ac":
            if contas:
                selecionada = selecionar_conta(contas)
                if selecionada is not None:
                    conta_ativa = selecionada
                    print(f"Conta {selecionada['numero_conta']} selecionada.")
            else:
                print("Crie uma conta primeiro.")
        elif opcao in {"d", "s", "e"}:
            if conta_ativa is None:
                print("Cadastre um usuário e crie uma conta primeiro.")
                continue
            if opcao == "e":
                exibir_extrato(conta_ativa["saldo"], extrato=conta_ativa["extrato"])
                continue
            valor = ler_valor("Valor: R$ ")
            if valor is None:
                continue
            if opcao == "d":
                conta_ativa["saldo"], conta_ativa["extrato"] = depositar(
                    conta_ativa["saldo"], valor, conta_ativa["extrato"]
                )
            else:
                atualizar_limite_diario(conta_ativa)
                conta_ativa["saldo"], conta_ativa["extrato"], conta_ativa["numero_saques"] = sacar(
                    saldo=conta_ativa["saldo"], valor=valor, extrato=conta_ativa["extrato"],
                    limite=LIMITE, numero_saques=conta_ativa["numero_saques"],
                    limite_saques=LIMITE_SAQUES,
                )
        else:
            print("Opção inválida. Escolha uma opção do menu.")


if __name__ == "__main__":
    main()
