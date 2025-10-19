# 🚂 Guia de Deploy no Railway - FISCALIA

## 📋 Pré-requisitos

- [ ] Conta no [Railway.app](https://railway.app)
- [ ] Repositório GitHub com o código
- [ ] Groq API Key (ou OpenAI)

## 🚀 Deploy em 5 Minutos

### Passo 1: Criar Projeto no Railway

1. Aceda a [railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositório **fiscalia**
5. Railway detecta automaticamente o `Dockerfile`

### Passo 2: Adicionar PostgreSQL (Recomendado)

1. No projeto, clique em **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway cria automaticamente:
   - Base de dados PostgreSQL
   - Variável `DATABASE_URL` configurada
   - Conexão segura entre serviços

### Passo 3: Configurar Variáveis de Ambiente

No serviço principal (não no PostgreSQL), adicione:

```bash
# OBRIGATÓRIO
GROQ_API_KEY=gsk_seu_token_aqui

# OPCIONAL - Railway já configura automaticamente:
# DATABASE_URL (vem do PostgreSQL Plugin)
# PORT (Railway aloca automaticamente)
# RAILWAY_ENVIRONMENT=production
```

### Passo 4: Configurar Volume Persistente

1. No serviço principal, vá a **"Settings"** → **"Volumes"**
2. Clique em **"New Volume"**
3. Configure:
   - **Mount Path**: `/data`
   - **Size**: 1GB (ajuste conforme necessidade)

### Passo 5: Deploy!

Railway faz deploy automático. Acompanhe:

1. **Build Logs**: Veja o Docker build
2. **Deploy Logs**: Veja a aplicação a iniciar
3. **Runtime Logs**: Logs da aplicação

Quando ver: ✅ **"You can now view your Streamlit app"** → Está pronto!

## 🌐 Aceder à Aplicação

1. No Railway, vá ao serviço
2. Clique em **"Settings"** → **"Networking"**
3. Clique em **"Generate Domain"**
4. Railway cria URL: `https://fiscalia-production.up.railway.app`

## ⚙️ Configurações Avançadas

### Auto-Deploy via GitHub

Railway faz deploy automático a cada push:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway detecta e faz deploy automaticamente! 🚀
```

### Variáveis de Ambiente Opcionais

```bash
# Limites de processamento
MAX_FILES_PER_BATCH=100
MAX_FILE_SIZE_MB=50
PROCESSING_TIMEOUT=600

# Forçar ambiente (Railway já detecta)
ENVIRONMENT=production
```

### Escalar Recursos

1. **Settings** → **Resources**
2. Ajuste:
   - CPU: 0.5 - 8 vCPU
   - RAM: 512MB - 32GB
   - Replicas: 1-10

### Logs em Tempo Real

```bash
# Ver logs no Railway Dashboard
# Ou use Railway CLI:
railway logs
```

## 🔍 Troubleshooting

### Build Falha

**Erro**: `Failed to build image`

**Solução**:
1. Verifique `Dockerfile` está correto
2. Confirme `requirements.txt` está completo
3. Veja logs detalhados no Railway

### Aplicação Não Inicia

**Erro**: `Application failed to respond to health check`

**Solução**:
1. Verifique variável `GROQ_API_KEY` está configurada
2. Confirme porta está correta (Railway usa `$PORT`)
3. Aumente `healthcheckTimeout` em `railway.json`

### Database Connection Failed

**Erro**: `Could not connect to database`

**Solução**:
1. Verifique PostgreSQL Plugin está ativo
2. Confirme `DATABASE_URL` está configurada
3. Se não usar PostgreSQL, app usa SQLite automaticamente

### Out of Memory

**Erro**: `Container killed due to memory`

**Solução**:
1. Aumente RAM em **Settings** → **Resources**
2. Reduza `MAX_FILES_PER_BATCH`
3. Otimize processamento em lote

## 📊 Monitorização

### Métricas Disponíveis

Railway fornece:
- ✅ CPU Usage
- ✅ Memory Usage  
- ✅ Network Traffic
- ✅ Request Rate
- ✅ Response Time

### Alertas

Configure alertas para:
- High CPU (>80%)
- High Memory (>90%)
- Deployment Failures
- Health Check Failures

## 💰 Custos

### Starter Plan (Grátis)
- $5 crédito mensal
- 500 horas de execução
- 512MB RAM
- Perfeito para testes

### Developer Plan ($5/mês)
- $5 crédito incluído
- Execução ilimitada
- Até 8GB RAM
- Ideal para produção pequena

### Team Plan ($20/mês)
- $20 crédito incluído
- Múltiplos ambientes
- Até 32GB RAM
- Ideal para produção enterprise

## 🔒 Segurança

### Variáveis de Ambiente

- ✅ Encriptadas em repouso
- ✅ Não aparecem nos logs
- ✅ Isoladas por serviço

### Networking

- ✅ HTTPS automático
- ✅ Certificados SSL geridos
- ✅ Private networking entre serviços

### Database

- ✅ Backups automáticos (PostgreSQL)
- ✅ Point-in-time recovery
- ✅ Conexões encriptadas

## 🎯 Checklist Final

Antes de ir para produção:

- [ ] PostgreSQL configurado
- [ ] Volume `/data` montado (1GB+)
- [ ] `GROQ_API_KEY` configurada
- [ ] Domain gerado e funcional
- [ ] Health check a responder
- [ ] Logs sem erros
- [ ] Teste upload e análise de ficheiro
- [ ] Teste download de relatórios
- [ ] Verifique métricas estáveis
- [ ] Configure alertas

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🆘 Suporte

- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- GitHub Issues: [seu-repo/issues](https://github.com/seu-user/fiscalia/issues)
- Email: seu-email@example.com

---

**🎉 Parabéns!** A sua aplicação FISCALIA está em produção no Railway!
