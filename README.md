# Agenda Médica

Frontend em Angular para login e consulta dos agendamentos, consumindo uma API Flask no backend. O visual foi mantido próximo ao layout anterior, com hero, cards e tabela escura com Tabulator.

## O que a solução entrega

- Angular como interface única da aplicação.
- Login com usuário ou e-mail e senha validado no SQLite via API.
- Seed inicial com o usuário de teste `admin / Agenda@123`.
- Integração HTTP com uma API mock separada no Docker Compose.
- Tabela com colunas para data, horário, paciente, CPF, médico, especialidade, convênio e status.
- Busca por paciente, CPF ou médico.
- Tratamento de login inválido, agenda vazia, API indisponível, resposta inválida e falha de banco.

## Executar localmente

1. Inicie o backend Flask com `python wsgi.py`.
2. Inicie a API mock com `python mock_api/app.py`.
3. Entre na pasta `frontend` e rode `npm start`.
4. Abra `http://localhost:4200`.

## Executar com Docker

```bash
docker compose up --build
```

Depois abra `http://localhost:4200`.

Isso sobe automaticamente o frontend Angular (build de produção servido por Nginx), o backend Flask e a API mock no mesmo compose.

Para subir mais rápido em execuções seguintes (sem rebuild):

```bash
docker compose up
```

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

- `backend/`: API Flask, autenticação e banco SQLite.
  - `app/`: pacote principal da aplicação (rotas, config, banco, services).
  - `mock_api/`: API HTTP simulada para agendamentos.
  - `scripts/seed.py`: inicialização do SQLite e usuário de teste.
  - `instance/`: banco de dados SQLite (não versionado).
- `frontend/`: interface Angular 19 com Tabulator.
- `docker-compose.yml`: sobe frontend, API e mock com um comando.
