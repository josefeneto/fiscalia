-- ================================================
-- FISCALIA - Database Schema
-- Gerado em: 2025-10-24 18:13:31
-- ================================================

-- Tabela: docs_para_erp
CREATE TABLE docs_para_erp (
	id INTEGER NOT NULL, 
	time_stamp DATETIME NOT NULL, 
	path_nome_arquivo VARCHAR(500) NOT NULL, 
	erp_processado VARCHAR(3) NOT NULL, 
	chave_acesso VARCHAR(44) NOT NULL, 
	numero_nf VARCHAR(20) NOT NULL, 
	serie VARCHAR(10), 
	modelo VARCHAR(10), 
	natureza_operacao VARCHAR(100), 
	tipo_operacao VARCHAR(1), 
	data_emissao DATETIME, 
	data_saida_entrada DATETIME, 
	cnpj_emitente VARCHAR(14), 
	cpf_emitente VARCHAR(11), 
	razao_social_emitente VARCHAR(200), 
	nome_fantasia_emitente VARCHAR(200), 
	ie_emitente VARCHAR(20), 
	uf_emitente VARCHAR(2), 
	municipio_emitente VARCHAR(100), 
	cnpj_destinatario VARCHAR(14), 
	cpf_destinatario VARCHAR(11), 
	razao_social_destinatario VARCHAR(200), 
	ie_destinatario VARCHAR(20), 
	uf_destinatario VARCHAR(2), 
	municipio_destinatario VARCHAR(100), 
	valor_total FLOAT, 
	valor_produtos FLOAT, 
	valor_frete FLOAT, 
	valor_seguro FLOAT, 
	valor_desconto FLOAT, 
	valor_outras_despesas FLOAT, 
	base_calculo_icms FLOAT, 
	valor_icms FLOAT, 
	valor_ipi FLOAT, 
	valor_pis FLOAT, 
	valor_cofins FLOAT, 
	cfop VARCHAR(10), 
	info_complementar TEXT, 
	info_fisco TEXT, 
	PRIMARY KEY (id)
);

-- Tabela: registo_resultados
CREATE TABLE registo_resultados (
	id INTEGER NOT NULL, 
	time_stamp DATETIME NOT NULL, 
	path_nome_arquivo VARCHAR(500) NOT NULL, 
	resultado VARCHAR(50) NOT NULL, 
	causa VARCHAR(500), 
	PRIMARY KEY (id)
);

-- Índice: ix_docs_para_erp_chave_acesso
CREATE UNIQUE INDEX ix_docs_para_erp_chave_acesso ON docs_para_erp (chave_acesso);

-- Índice: ix_registo_resultados_time_stamp
CREATE INDEX ix_registo_resultados_time_stamp ON registo_resultados (time_stamp);
