# 🧾 FISCALIA

**Sistema Inteligente de Processamento de Notas Fiscais Eletrónicas (NFe) com IA**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-red.svg)](https://streamlit.io)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.140+-green.svg)](https://www.crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

> 🚀 **[Ver Demo Online](https://fiscalia.up.railway.app/)** | 📖 [Documentação](#-documentação) | 🐛 [Reportar Bug](https://github.com/josefeneto/fiscalia/issues)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Demo Online](#-demo-online)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Deploy](#-deploy)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Roadmap](#-roadmap)
- [Contribuir](#-contribuir)
- [Licença](#-licença)
- [Suporte](#-suporte)

---

## 🎯 Sobre o Projeto

**FISCALIA** é um sistema automatizado de processamento de Notas Fiscais Eletrónicas (NFe) que utiliza Inteligência Artificial (CrewAI) para extrair, validar e analisar dados fiscais de forma inteligente e eficiente.

### Problema Resolvido

- ⏱️ **Manual e Demorado**: Processar NFes manualmente consome horas
- ❌ **Propenso a Erros**: Transcrição manual gera inconsistências
- 📊 **Difícil de Analisar**: Extrair insights de múltiplas faturas é complexo
- 🗄️ **Desorganizado**: Gestão de ficheiros XML dispersos

### Solução

✅ **Automação Inteligente**: IA processa ficheiros XML em segundos  
✅ **Validação Rigorosa**: Deteta erros e inconsistências automaticamente  
✅ **Análise Avançada**: Gera relatórios e insights financeiros  
✅ **Gestão Centralizada**: Base de dados organizada e pesquisável  

---

## ✨ Funcionalidades

### 🔄 Processamento Automatizado
- Upload de ficheiros XML individuais ou em lote
- Extração automática de dados fiscais
- Validação de NIF, valores e datas
- Detecção de duplicados

### 🤖 Agentes IA Especializados
- **Validador**: Verifica conformidade fiscal
- **Extrator**: Extrai dados estruturados
- **Analista**: Gera insights financeiros
- **Organizador**: Categoriza e arquiva

### 📊 Relatórios e Analytics
- Dashboards interativos
- Gráficos de tendências
- Análise de fornecedores
- Exportação para Excel/PDF

### 🗄️ Gestão de Dados
- Base de dados SQLite/PostgreSQL
- Histórico completo de processamentos
- Pesquisa avançada
- Backup automático

### 🔐 Segurança
- Validação de ficheiros
- Logs de auditoria
- Controlo de acesso (opcional)
- Encriptação de dados sensíveis

---

## 🌐 Demo Online

**Aceda à aplicação em produção:**

🔗 **https://fiscalia.up.railway.app/**

> ⚠️ **Nota**: Demo pública - não carregue dados sensíveis reais!

### Credenciais de Teste
- **Ambiente**: Produção (Railway)
- **Base de Dados**: SQLite
- **API**: Groq (Llama 3.3 70B) / OpenAI

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+**
- **Git**
- **API Key**: [Groq](https://console.groq.com) (grátis) ou [OpenAI](https://platform.openai.com)

### Instalação Local

```bash
# 1. Clonar repositório
git clone https://github.com/josefeneto/fiscalia.git
cd fiscalia

# 2. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e adicionar sua API key

# 5. Executar aplicação
python run_streamlit.py
```

A aplicação abre automaticamente em `http://localhost:8501` 🎉

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um ficheiro `.env` na raiz do projeto:

```bash
# ==================== OBRIGATÓRIO ====================
# Escolha UMA das opções:

# Opção 1: Groq (recomendado - gratuito)
GROQ_API_KEY=gsk_sua_chave_aqui
GROQ_MODEL=groq/llama-3.3-70b-versatile  # opcional

# Opção 2: OpenAI
OPENAI_API_KEY=sk-sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini  # opcional


# ==================== OPCIONAL ====================

# Base de Dados (deixar vazio usa SQLite)
# DATABASE_URL=postgresql://user:pass@host:port/db

# Limites de Processamento
MAX_FILES_PER_BATCH=100
MAX_FILE_SIZE_MB=50
PROCESSING_TIMEOUT=600

# Ambiente
ENVIRONMENT=development  # ou production
```

### Obter API Keys

#### Groq (Grátis) ⭐ Recomendado
1. Aceder [console.groq.com](https://console.groq.com)
2. Criar conta (grátis)
3. Ir para API Keys
4. Criar nova chave
5. Copiar para `.env`

#### OpenAI (Pago)
1. Aceder [platform.openai.com](https://platform.openai.com)
2. Criar conta
3. Adicionar créditos ($5 mínimo)
4. Criar API key
5. Copiar para `.env`

---

## 💻 Uso

### Interface Web

1. **Upload de Ficheiros**
   - Arraste ficheiros XML para a área de upload
   - Ou clique para selecionar
   - Suporta múltiplos ficheiros

2. **Processamento**
   - Sistema valida e processa automaticamente
   - Progresso visível em tempo real
   - Notificações de sucesso/erro

3. **Visualização**
   - Consulte faturas processadas
   - Filtre por data, fornecedor, valor
   - Exporte relatórios

4. **Analytics**
   - Dashboards interativos
   - Gráficos de tendências
   - KPIs financeiros

### Exemplos de Ficheiros

O sistema aceita ficheiros XML no formato NFe padrão português/brasileiro:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="...">
  <NFe>
    <infNFe>
      <emit>...</emit>
      <dest>...</dest>
      <det>...</det>
      <total>...</total>
    </infNFe>
  </NFe>
</nfeProc>
```

---

## 🚂 Deploy

### Railway (Recomendado)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

**Deploy em 3 minutos:**

1. Clique no botão acima
2. Conecte seu GitHub
3. Configure variáveis:
   - `GROQ_API_KEY` ou `OPENAI_API_KEY`
4. Deploy automático! 🚀

### Outras Plataformas

<details>
<summary><b>Render.com</b></summary>

```yaml
# render.yaml
services:
  - type: web
    name: fiscalia
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run streamlit_app/app.py --server.port=$PORT
```
</details>

<details>
<summary><b>Heroku</b></summary>

```bash
heroku create fiscalia-app
heroku config:set GROQ_API_KEY=sua_chave
git push heroku main
```
</details>

<details>
<summary><b>Docker</b></summary>

```bash
docker build -t fiscalia .
docker run -p 8501:8501 -e GROQ_API_KEY=sua_chave fiscalia
```
</details>

---

## 🛠️ Tecnologias

### Core
- **[Python 3.11+](https://www.python.org/)** - Linguagem principal
- **[Streamlit](https://streamlit.io)** - Interface web interativa
- **[CrewAI](https://www.crewai.com)** - Framework de agentes IA
- **[LangChain](https://www.langchain.com)** - Orquestração de LLMs

### LLM Providers
- **[Groq](https://groq.com)** - Llama 3.3 70B (rápido e gratuito)
- **[OpenAI](https://openai.com)** - GPT-4o Mini (alternativa)

### Base de Dados
- **[SQLite](https://www.sqlite.org/)** - Desenvolvimento/pequena escala
- **[PostgreSQL](https://www.postgresql.org/)** - Produção (opcional)
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM

### Processamento
- **[lxml](https://lxml.de/)** - Parsing XML
- **[pandas](https://pandas.pydata.org/)** - Análise de dados
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel export

### Deploy
- **[Railway](https://railway.app)** - Hosting (recomendado)
- **[Docker](https://www.docker.com/)** - Containerização
- **[Gunicorn](https://gunicorn.org/)** - WSGI server

---

## 📁 Estrutura do Projeto

```
fiscalia/
├── streamlit_app/           # Interface Streamlit
│   ├── app.py              # Aplicação principal
│   ├── pages/              # Páginas multi-page
│   └── components/         # Componentes reutilizáveis
├── src/                    # Código fonte
│   ├── agents/            # Agentes CrewAI
│   ├── crews/             # Crews e tarefas
│   ├── models/            # Modelos de dados
│   ├── services/          # Serviços de negócio
│   └── utils/             # Utilidades
├── arquivos/              # Ficheiros processados
│   ├── entrados/         # Upload
│   ├── processados/      # Sucesso
│   └── rejeitados/       # Erros
├── data/                  # Base de dados e temp
├── tests/                 # Testes automatizados
├── requirements.txt       # Dependências Python
├── Dockerfile            # Container Docker
├── railway.toml          # Config Railway
├── .env.example          # Template variáveis
└── README.md             # Este ficheiro
```

---

## 🗺️ Roadmap

### ✅ v1.0 - MVP (Concluído)
- [x] Processamento básico de NFe
- [x] Interface Streamlit
- [x] Agentes IA com CrewAI
- [x] Deploy Railway

### 🚧 v1.1 - Melhorias (Em Progresso)
- [ ] Dashboard analytics avançado
- [ ] Exportação PDF de relatórios
- [ ] API REST
- [ ] Autenticação de utilizadores

### 📅 v1.2 - Futuro
- [ ] Suporte multi-empresa
- [ ] Integração com sistemas contabilísticos
- [ ] OCR para faturas digitalizadas
- [ ] App mobile

### 💡 Ideias
- Detecção de anomalias com ML
- Previsão de despesas
- Chatbot para consultas
- Integrações (Sage, PHC, etc.)

**Tem uma ideia?** [Abra uma Issue](https://github.com/josefeneto/fiscalia/issues) ou [Discussão](https://github.com/discussions)!

---

## 🤝 Contribuir

Contribuições são muito bem-vindas! 🎉

### Como Contribuir

1. **Fork** o projeto
2. **Crie** um branch (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. **Push** para o branch (`git push origin feature/MinhaFeature`)
5. **Abra** um Pull Request

### Guidelines

- ✅ Escreva código limpo e documentado
- ✅ Adicione testes para novas funcionalidades
- ✅ Siga o estilo de código existente
- ✅ Atualize a documentação se necessário
- ✅ Teste localmente antes de submeter

### Reportar Bugs

Encontrou um bug? [Abra uma Issue](https://github.com/josefeneto/fiscalia/issues/new) com:

- ✅ Descrição clara do problema
- ✅ Passos para reproduzir
- ✅ Comportamento esperado vs atual
- ✅ Screenshots (se aplicável)
- ✅ Versão do Python e SO

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

**Resumo:**
- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido

**Condições:**
- ⚠️ Incluir aviso de licença e copyright
- ⚠️ Sem garantia

Ver [LICENSE](https://opensource.org/licenses/MIT) para detalhes completos.

---

## 📞 Suporte

### Canais de Suporte

- 🐛 **Bugs & Issues**: [GitHub Issues](https://github.com/josefeneto/fiscalia/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/discussions)
- 📧 **Email**: jose.fe.neto@gmx.com
- 🌐 **Demo**: [fiscalia.up.railway.app](https://fiscalia.up.railway.app)

### FAQ

<details>
<summary><b>Qual LLM devo usar?</b></summary>

**Groq (Llama 3.3 70B)** é recomendado:
- ✅ Gratuito
- ✅ Muito rápido
- ✅ Excelente qualidade
- ✅ Sem necessidade de cartão de crédito

**OpenAI** é alternativa se preferir GPT-4.
</details>

<details>
<summary><b>Posso usar em produção?</b></summary>

Sim! O sistema está pronto para produção. Recomendações:
- Use PostgreSQL em vez de SQLite
- Configure backups automáticos
- Adicione autenticação se necessário
- Monitore logs e recursos
</details>

<details>
<summary><b>É seguro?</b></summary>

Sim, com boas práticas:
- ✅ API keys via variáveis de ambiente
- ✅ Validação de ficheiros
- ✅ Logs de auditoria
- ✅ Sem armazenamento de dados sensíveis em plain text

Para ambiente corporativo, considere adicionar:
- Autenticação de utilizadores
- Encriptação de BD
- HTTPS obrigatório
</details>

<details>
<summary><b>Quanto custa?</b></summary>

**Desenvolvimento**: Grátis (com Groq)

**Produção Railway**:
- Starter: $5/mês (suficiente para pequenas empresas)
- Developer: $20/mês (médias empresas)

**Custos de API** (se usar OpenAI):
- ~$0.10 por 1000 faturas processadas
</details>

---

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io) - Framework web incrível
- [CrewAI](https://www.crewai.com) - Framework de agentes IA
- [Groq](https://groq.com) - LLM rápido e gratuito
- [Railway](https://railway.app) - Deploy simplificado
- Comunidade Python - Por todas as ferramentas

---

## 📊 Status do Projeto

![GitHub stars](https://img.shields.io/github/stars/josefeneto/fiscalia?style=social)
![GitHub forks](https://img.shields.io/github/forks/josefeneto/fiscalia?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/josefeneto/fiscalia?style=social)

**Última atualização**: Outubro 2024  
**Status**: 🟢 Ativo e em desenvolvimento  
**Versão**: 1.0.0

---

## 🌟 Star History

Se este projeto foi útil, considere dar uma ⭐ no GitHub!

---

<p align="center">
  Feito com ❤️ por <a href="https://github.com/josefeneto">José Neto</a>
</p>

<p align="center">
  <a href="#-fiscalia">Voltar ao topo ⬆️</a>
</p>025