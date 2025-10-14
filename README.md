# 🧾 Fiscalia - Sistema Inteligente de Gestão Fiscal

Sistema baseado em Agentes Inteligentes para automatizar o processamento e análise de documentos fiscais brasileiros (NFe, NFCe, CTe, MDF-e).

## 🎯 Objetivo

Automatizar o processamento de notas fiscais eletrônicas (XML) com:
- ✅ Extração automática de dados
- ✅ Validação e auditoria fiscal
- ✅ Detecção de duplicados e inconsistências
- ✅ Registro em base de dados para integração ERP
- ✅ Interface web intuitiva

## 🏗️ Arquitetura

O sistema utiliza:
- **CrewAI**: Framework de orquestração de agentes
- **Streamlit**: Interface web responsiva
- **SQLite**: Base de dados (com suporte a PostgreSQL)
- **LLM**: Groq (Llama 3.3 70B) ou OpenAI (GPT-4o-mini)

### Estrutura de Agentes

```
Crew Fiscalia
├── Agente Coordenador
│   └── Distribui arquivos para agentes especializados
├── Agente XML (NFe/NFCe/CTe/MDF-e)
│   ├── Extração de dados
│   └── Validação estrutural
├── Agente Validador Fiscal
│   ├── Verifica consistência de impostos
│   ├── Valida CFOPs, CSTs, NCMs
│   └── Detecta duplicados
└── Agente Registrador
    ├── Persiste dados em BD
    └── Move arquivos processados
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.13.5+
- Git
- Conta Groq (https://groq.com) ou OpenAI (https://platform.openai.com)

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/josefeneto/fiscalia.git
cd fiscalia
```

### Passo 2: Crie Ambiente Virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### Passo 3: Instale Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configure Variáveis de Ambiente

```bash
# Copie o template
copy .env.example .env

# Edite .env e adicione suas API keys
```

**Variáveis obrigatórias:**
```env
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=groq/llama-3.3-70b-versatile

# OU

OPENAI_API_KEY=sua_chave_openai
OPENAI_MODEL=gpt-4o-mini
```

### Passo 5: Teste a Configuração

```bash
python test_setup.py
```

## 📊 Uso Local

### Executar Aplicação Streamlit

```bash
streamlit run streamlit_app/app.py
```

Acesse: http://localhost:8501

### Funcionalidades Principais

1. **📤 Upload de Arquivos**
   - Upload manual de XMLs
   - Processamento em batch da pasta `/entrados`
   - Suporte futuro para CSV

2. **📊 Visualizar Base de Dados**
   - Consulta de documentos processados
   - Filtros por data, tipo, status
   - Exportação de dados

3. **📈 Estatísticas**
   - Dashboard com KPIs
   - Análise de impostos
   - Relatórios por período

4. **💬 Consultas Livres**
   - Perguntas em linguagem natural
   - Análises customizadas
   - Insights fiscais

## 🗂️ Estrutura de Pastas

```
fiscalia/
├── src/                    # Código fonte
│   ├── crew/              # Agentes CrewAI
│   ├── database/          # Gestão de BD
│   ├── processors/        # Processadores XML
│   └── utils/             # Utilitários
├── streamlit_app/         # Interface web
│   └── pages/            # Páginas Streamlit
├── arquivos/              # Arquivos fiscais
│   ├── entrados/         # Para processar
│   ├── processados/      # Processados com sucesso
│   └── rejeitados/       # Com erros
├── data/                  # Base de dados SQLite
├── logs/                  # Arquivos de log
└── tests/                 # Testes automatizados
```

## 🗄️ Base de Dados

### Tabela: `registo_resultados`

Registro de processamento de cada arquivo:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| numero_sequencial | INTEGER | ID único auto-incremento |
| time_stamp | DATETIME | Data/hora processamento |
| path_nome_arquivo | TEXT | Caminho do arquivo |
| resultado | TEXT | Sucesso/Insucesso |
| causa | TEXT | Motivo do resultado |

### Tabela: `docs_para_ERP`

Dados extraídos para integração ERP:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| numero_sequencial | INTEGER | ID único |
| time_stamp | DATETIME | Data/hora registro |
| path_nome_arquivo | TEXT | Arquivo origem |
| tipo_documento | TEXT | NFe/NFCe/CTe/MDF-e |
| numero_nf | TEXT | Número da NF |
| serie | TEXT | Série |
| data_emissao | DATE | Data emissão |
| emitente_cnpj | TEXT | CNPJ emitente |
| emitente_nome | TEXT | Razão social |
| destinatario_cnpj | TEXT | CNPJ destinatário |
| destinatario_nome | TEXT | Razão social |
| valor_total | DECIMAL | Valor total |
| valor_icms | DECIMAL | ICMS |
| valor_ipi | DECIMAL | IPI |
| valor_pis | DECIMAL | PIS |
| valor_cofins | DECIMAL | COFINS |
| cfop | TEXT | CFOP principal |
| items_json | JSON | Itens da NF (JSON) |
| erp_processado | BOOLEAN | Processado no ERP |

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_xml_processor.py
```

## 🐳 Deploy (Railway)

### Preparação

O projeto já inclui:
- ✅ `Dockerfile`
- ✅ `railway.json`
- ✅ Configuração de volume para persistência

### Passos

1. **Criar conta no Railway** (https://railway.app)

2. **Conectar repositório GitHub**

3. **Configurar variáveis de ambiente:**
   ```
   GROQ_API_KEY=sua_chave
   GROQ_MODEL=groq/llama-3.3-70b-versatile
   ENVIRONMENT=production
   RAILWAY_VOLUME_MOUNT_PATH=/data
   ```

4. **Deploy automático** via GitHub

## 🛠️ Desenvolvimento

### Code Style

```bash
# Formatar código
black src/ streamlit_app/ tests/

# Verificar linting
flake8 src/ streamlit_app/

# Type checking
mypy src/
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/nova-funcionalidade

# Commit
git add .
git commit -m "feat: descrição da funcionalidade"

# Push
git push origin feature/nova-funcionalidade
```

### Padrão de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

## 📚 Documentação Adicional

- [Guia de Contribuição](CONTRIBUTING.md)
- [Documentação Técnica](docs/technical.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🔒 Segurança

- ✅ API keys em variáveis de ambiente
- ✅ Validação de entrada de dados
- ✅ Logs de auditoria
- ✅ Arquivos sensíveis no .gitignore

**Nunca commite:**
- Arquivos `.env`
- API keys
- Dados reais de notas fiscais
- Credenciais

## 📄 Licença

[MIT License](LICENSE)

## 👥 Autores

- José Ferreira Neto ([@josefeneto](https://github.com/josefeneto))

## 🤝 Contribuições

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 Suporte

- Issues: https://github.com/josefeneto/fiscalia/issues
- Discussões: https://github.com/josefeneto/fiscalia/discussions

## 🗺️ Roadmap

### MVP (Fase 1) ✅ Em Desenvolvimento
- [x] Configuração base
- [ ] Processamento XML NFe
- [ ] Base de dados SQLite
- [ ] Interface Streamlit
- [ ] Deploy Railway

### Fase 2 (Futuro)
- [ ] Suporte PDF e OCR
- [ ] Processamento CSV
- [ ] Classificação por ramo
- [ ] Integração ERP
- [ ] Relatórios avançados
- [ ] API REST

---

**Status:** 🚧 Em Desenvolvimento - MVP Fase 1

**Última Atualização:** Outubro 2025