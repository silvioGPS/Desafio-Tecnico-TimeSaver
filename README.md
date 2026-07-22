# Agenda Médica

Aplicação web em Flask para autenticação de usuário, consulta de agendamentos via API HTTP e exibição dos dados em uma tabela interativa com Tabulator.

## O que a solução entrega

- Login com usuário ou e-mail e senha validado no SQLite.
- Seed inicial com o usuário de teste `admin / Agenda@123`.
- Integração HTTP com uma API mock separada no Docker Compose.
- Tabela com colunas para data, horário, paciente, CPF, médico, especialidade, convênio e status.
- Busca por paciente, CPF ou médico.
- Tratamento de login inválido, agenda vazia, API indisponível, resposta inválida e falha de banco.

## Executar localmente

1. Crie um ambiente virtual e instale as dependências.
2. Copie `.env.example` para `.env` e ajuste os valores desejados.
3. Rode o seed do banco.
4. Inicie a aplicação web e a API mock.

Exemplo:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed.py
python wsgi.py
```

Em outro terminal:

```bash
python mock_api/app.py
```

## Executar com Docker

```bash
docker compose up --build
```

Depois abra `http://localhost:5000`.

## Credenciais padrão

- Usuário: `admin`
- E-mail: `admin@timersaver.com.br`
- Senha: `Agenda@123`

## Como simular cenários da API

Use a variável `APPOINTMENTS_API_MODE` no serviço `api` do Docker Compose para testar:

- `normal`: retorna a agenda normalmente.
- `empty`: retorna lista vazia.
- `invalid`: retorna resposta com campos obrigatórios ausentes.
- `down`: retorna indisponibilidade temporária.

## Estrutura principal

- `app/`: aplicação web Flask.
- `mock_api/`: API HTTP simulada.
- `scripts/seed.py`: inicialização do SQLite e usuário de teste.
- `docker-compose.yml`: sobe web e API com um comando.
