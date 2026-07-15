# Assistente Acadêmico Unoesc — IA Generativa com RAG

Este repositório contém a implementação final do **Assistente Acadêmico Inteligente para a Unoesc**. O projeto consiste em uma solução de IA ponta a ponta que utiliza a arquitetura **RAG (Retrieval-Augmented Generation)** para responder a dúvidas de alunos com base exclusivamente em documentos e regras institucionais cadastradas por administradores. 

A solução foi construída utilizando práticas modernas de desenvolvimento, arquitetura de software modular, segurança via tokens JWT e interface gráfica rica para estudantes e administradores.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Orquestração de IA:** [LangChain](https://www.langchain.com/)
* **Modelo de Linguagem (LLM):** Microsoft Phi-3 (rodando localmente via [Ollama](https://ollama.com/))
* **Banco de Dados:** PostgreSQL (rodando via Docker)
* **ORM:** SQLAlchemy
* **Autenticação e Segurança:** JWT (JSON Web Tokens) com criptografia `HS256`
* **Containerização:** Docker & Docker Compose

---

## 📐 Arquitetura do Projeto

Para garantir a manutenibilidade, testabilidade e escalabilidade do software, o projeto foi refatorado de uma estrutura monolítica inicial para uma **Arquitetura Modular Multicamadas**, separando claramente as responsabilidades de negócio:

```text
desafio-2026-2-python/
│
├── src/                        # Código-fonte principal do Backend (FastAPI)
│   ├── main.py                 # Ponto de entrada do app, rotas e inicialização do servidor
│   │
│   ├── core/                   # Configurações globais e segurança
│   │   └── security.py         # Geração e validação de Tokens JWT e fluxo de segurança
│   │
│   ├── db/                     # Camada de persistência e banco de dados
│   │   ├── database.py         # Conexão com o banco de dados PostgreSQL e Session Local
│   │   ├── models.py           # Definição das tabelas SQL usando SQLAlchemy ORM
│   │   └── schemas.py          # Schemas de validação de dados usando Pydantic V2
│   │
│   └── services/               # Regras de negócio e inteligência artificial
│       └── rag_engine.py       # Integração com LangChain, Ollama (Phi-3) e motor de busca
│
├── frontend/                   # Interface gráfica (Frontend)
│   └── app_streamlit.py        # Interface unificada com Streamlit (Chat e Painel Administrativo)
│
├── .env                        # Variáveis de ambiente configuráveis (JWT_SECRET, DATABASE_URL)
├── .gitignore                  # Arquivos ignorados no controle de versão (venv, .env, __pycache__)
├── docker-compose.yml          # Definição do banco de dados PostgreSQL em container
├── requirements.txt            # Declaração das dependências do ecossistema Python
└── README.md                   # Documentação detalhada do projeto
```

---

## 🚀 Requisitos Funcionais Atendidos (RFs)

1.  **RF01 (Autenticação Administrativa):** Login seguro para administradores utilizarem o painel de gerenciamento, protegendo rotas críticas contra acessos não autorizados.
2.  **RF02 (Processamento RAG):** Integração via LangChain que recupera as regras institucionais corretas no banco de dados e as injeta no contexto do modelo local Phi-3 para formulação da resposta.
3.  **RF03 (Busca de Contexto Inteligente):** Motor de busca robusto com tolerância a acentuações e pontuações (implementado via `unicodedata` do Python). A busca por termos como "matricula" localiza documentos salvos como "matrícula".
4.  **RF04 (Bloqueio de Alucinação):** Engenharia de Prompt avançada com instruções restritas à IA. Caso o banco de dados não possua informações sobre o tema, a IA retorna obrigatoriamente: *"Desculpe, não tenho informações sobre esse assunto."*
5.  **RF05 (Banco de Dados PostgreSQL):** Persistência relacional de regras e logs em banco de dados robusto.
6.  **RF06 (Modelagem de Dados):** Tabelas bem estruturadas para a base de conhecimento (ID, categoria, título, conteúdo) e para logs de interações (ID, pergunta, resposta, carimbo de data/hora).
7.  **RF07 (Segurança com JWT):** Rotas administrativas protegidas por autenticação via Token JWT (`Bearer Token`) com tempo de expiração de 60 minutos configurável.
8.  **RF08 (Endpoints da API):** Endpoints bem documentados no padrão REST para chat, inserção de regras, listagem e obtenção de estatísticas.
9.  **RF09 (Interface Administrativa):** Dashboard em Streamlit para cadastrar novos documentos, ver a listagem em tempo real e acompanhar gráficos de estatísticas de uso (perguntas feitas por dia).
10. **RF10 (Interface do Estudante):** Chat intuitivo em formato de aplicativo de mensagens para os alunos realizarem consultas de forma ágil.

---

## 📦 Como Executar o Projeto

Siga os passos abaixo para rodar a aplicação completa no seu ambiente local.

### Pré-requisitos
* [Docker](https://www.docker.com/) instalado.
* [Ollama](https://ollama.com/) instalado localmente com o modelo `phi3` baixado:
    ```bash
    ollama run phi3
    ```

### Passo 1: Inicializar o Banco de Dados (Docker)
Na raiz do projeto, execute o comando para subir o container do PostgreSQL:
```bash
docker-compose up -d
```

### Passo 2: Configurar o Ambiente Python Virtual
Crie e ative uma `venv` para isolar as dependências do projeto:
```bash
# No Windows
python -m venv venv
.\venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar as Dependências
Com a `venv` ativa, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar as Variáveis de Ambiente (`.env`)
Crie um arquivo `.env` na raiz do projeto (se já não houver) com as seguintes configurações:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/unoesc_db
JWT_SECRET=sua_chave_secreta_super_segura_aqui_para_criptografia_do_token_jwt
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Passo 5: Iniciar a API do Backend (FastAPI)
Com o banco de dados ativo, execute o servidor FastAPI com o comando atualizado da arquitetura modular:
```bash
uvicorn src.main:app --reload
```
A API estará disponível em `http://localhost:8000`. Você pode acessar a documentação interativa automatizada (Swagger UI) em: **`http://localhost:8000/docs`**.

### Passo 6: Iniciar o Frontend (Streamlit)
Em um novo terminal (mantendo a API rodando), ative a `venv` e execute a interface gráfica:
```bash
streamlit run frontend/app_streamlit.py
```
O navegador abrirá automaticamente em `http://localhost:8501` mostrando o assistente.

---

## 🔒 Credenciais de Acesso Padrão (Admin)
Para acessar o painel de gerenciamento e alimentar a base de conhecimento no Streamlit ou testar as rotas protegidas no Swagger:
* **Usuário:** `unoesc`
* **Senha:** `senha123`

---

## 📈 Decisões de Projeto e Evoluções Futuras (Roadmap)

Durante o desenvolvimento do MVP, tomamos decisões estratégicas visando a simplicidade de execução para a banca avaliadora, prevendo também as próximas etapas de evolução do software:

1.  **Busca Avançada à Prova de Acentos via Python:** Em vez de exigir que a banca configure extensões adicionais diretamente dentro do banco de dados (como o `unaccent` do Postgres), resolvemos o problema de correspondência textual limpando acentos tanto das pesquisas do estudante quanto dos conteúdos do banco de dados usando a biblioteca nativa `unicodedata` do Python.
2.  **Roteamento Centralizado Híbrido:** Mantivemos a declaração das rotas no `src/main.py` para evitar quebras de caminhos complexos no Frontend Streamlit, dividindo em módulos as pastas de banco de dados (`db/`), segurança (`core/`) e serviços de IA (`services/`).
3.  **Roadmap de Engenharia (Futuro):**
    * **Embeddings e Banco de Dados Vetorial:** Substituir a busca baseada em palavras-chave (`ILIKE` / correspondência textual) por uma busca semântica real usando vetores e modelos de embedding (ex: *SentenceTransformers*) salvando-os no `pgvector` (extensão do PostgreSQL) ou em uma base vetorial leve como o *ChromaDB*. Isso permitirá que a IA encontre o contexto correto buscando por sinônimos (ex: buscar por "trancamento" e encontrar a regra cadastrada com a palavra "paralisação").
    * **Modularização completa de rotas:** Desmembrar as rotas do `main.py` usando `APIRouter` do FastAPI criando subpastas na camada `/api` para rotas públicas e rotas estritamente protegidas por segurança JWT.