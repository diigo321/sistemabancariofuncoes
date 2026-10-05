# Sistema bancário com funções Python

Projeto para o desafio **Otimizando o Sistema Bancário com Funções Python**, do bootcamp Vivo - Python AI Backend Developer da DIO.

A aplicação refatora as operações bancárias em funções e adiciona cadastro de usuários e contas correntes. A implementação foi preparada com auxílio de IA.

## Funcionalidades

- Depósitos positivos e extrato com saldo atualizado.
- Saques de até R$ 500,00, limitados a três por dia e por conta.
- Bloqueio de saques sem saldo e de valores inválidos.
- Cadastro com nome, data de nascimento, CPF e endereço; CPFs duplicados são recusados.
- Agência fixa `0001`, contas numeradas sequencialmente e vinculadas a um usuário.
- Um usuário pode ter várias contas, com saldo e histórico independentes.
- Seleção da conta ativa e listagem de contas.
- Valores monetários representados por `Decimal`, evitando imprecisão de ponto flutuante.

## Como executar

Requer **Python 3.10 ou superior**. Não precisa instalar bibliotecas externas.

```bash
python sistema_bancario.py
```

No Windows, também pode usar `py sistema_bancario.py`.

1. Escolha `nu` para cadastrar um usuário.
2. Escolha `nc` e informe o CPF cadastrado para criar uma conta.
3. Use `d`, `s` e `e` para depositar, sacar e consultar o extrato.
4. Use `ac` para trocar a conta ativa, `lc` para listar contas e `q` para sair.

Valores aceitam ponto ou vírgula: `100.50` ou `100,50`.
O CPF aceita apenas dígitos ou o formato `123.456.789-00`. A validação é de formato e unicidade; não verifica os dígitos de controle da Receita Federal. Use dados fictícios para experimentar.

## Organização das funções

| Função | Responsabilidade |
| --- | --- |
| `depositar(saldo, valor, extrato, /)` | Argumentos somente por posição; retorna saldo e extrato |
| `sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques)` | Argumentos nomeados; retorna saldo, extrato e contador de saques |
| `exibir_extrato(saldo, /, *, extrato)` | Saldo por posição e extrato nomeado |
| `criar_usuario` / `cadastrar_usuario` | Entrada interativa e validação do cadastro |
| `filtrar_usuario` | Localiza usuário pelo CPF |
| `criar_conta` / `listar_contas` | Criação e consulta das contas |
| `atualizar_limite_diario` | Reinicia o contador quando a data muda |

O retorno do contador de saques permite que o limite seja preservado entre as chamadas. O programa principal concentra a interação com o menu.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem depósitos, saldo insuficiente, limites de saque, virada do dia, precisão monetária, extrato, cadastros duplicados e contas independentes. Também verificam as regras de passagem de argumentos do desafio.

## Limitações

Este é um exercício de terminal: os dados ficam somente em memória e são apagados ao encerrar o programa. Não há autenticação, persistência, juros ou integração bancária.

## Referência

- [Trilha Python da DIO](https://github.com/digitalinnovationone/trilha-python-dio)

## Descrição para entrega na DIO

Sistema bancário em Python refatorado em funções de depósito, saque e extrato, com parâmetros posicionais e nomeados. Inclui cadastro de usuários e contas, validação de CPF duplicado, limites de saque, histórico individual por conta e testes automatizados. Valores monetários utilizam Decimal. Projeto desenvolvido com auxílio de IA.
