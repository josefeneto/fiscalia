"""
Testes para o Database Manager
Execute: pytest tests/test_database.py -v
OU: python tests/test_database.py
"""
import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager, RegistroResultado, DocumentoParaERP
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestDatabaseManager:
    """Testes do DatabaseManager"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        # Usar banco de dados de teste em memória
        self.db = DatabaseManager(db_path=":memory:")
        logger.info("Database de teste inicializado")
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        self.db.fechar()
        logger.info("Database de teste fechado")
    
    def test_adicionar_registro_resultado_sucesso(self):
        """Testa adição de registro de sucesso"""
        registro = self.db.adicionar_registro_resultado(
            path_nome_arquivo="teste/arquivo.xml",
            resultado="Sucesso",
            causa="Processado com sucesso",
            tipo_arquivo="XML",
            tamanho_bytes=1024,
            hash_arquivo="abc123"
        )
        
        assert registro.numero_sequencial is not None
        assert registro.resultado == "Sucesso"
        assert registro.path_nome_arquivo == "teste/arquivo.xml"
        logger.info("✓ Teste de adição de registro - PASSOU")
    
    def test_adicionar_registro_resultado_insucesso(self):
        """Testa adição de registro de insucesso"""
        registro = self.db.adicionar_registro_resultado(
            path_nome_arquivo="teste/arquivo_erro.xml",
            resultado="Insucesso",
            causa="Arquivo corrompido",
            tipo_arquivo="XML"
        )
        
        assert registro.resultado == "Insucesso"
        assert registro.causa == "Arquivo corrompido"
        logger.info("✓ Teste de registro de insucesso - PASSOU")
    
    def test_buscar_registros_resultados(self):
        """Testa busca de registros com filtros"""
        # Adicionar alguns registros
        self.db.adicionar_registro_resultado(
            "arquivo1.xml", "Sucesso", tipo_arquivo="XML"
        )
        self.db.adicionar_registro_resultado(
            "arquivo2.xml", "Insucesso", tipo_arquivo="XML"
        )
        self.db.adicionar_registro_resultado(
            "arquivo3.xml", "Sucesso", tipo_arquivo="PDF"
        )
        
        # Buscar todos
        todos = self.db.buscar_registros_resultados()
        assert len(todos) == 3
        
        # Buscar apenas sucessos
        sucessos = self.db.buscar_registros_resultados(resultado="Sucesso")
        assert len(sucessos) == 2
        
        # Buscar apenas insucessos
        insucessos = self.db.buscar_registros_resultados(resultado="Insucesso")
        assert len(insucessos) == 1
        
        logger.info("✓ Teste de busca de registros - PASSOU")
    
    def test_estatisticas_processamento(self):
        """Testa obtenção de estatísticas"""
        # Adicionar registros
        self.db.adicionar_registro_resultado("1.xml", "Sucesso")
        self.db.adicionar_registro_resultado("2.xml", "Sucesso")
        self.db.adicionar_registro_resultado("3.xml", "Insucesso")
        
        stats = self.db.obter_estatisticas_processamento()
        
        assert stats['total_processamentos'] == 3
        assert stats['total_sucesso'] == 2
        assert stats['total_insucesso'] == 1
        assert stats['taxa_sucesso'] == 66.67
        
        logger.info("✓ Teste de estatísticas - PASSOU")
    
    def test_adicionar_documento(self):
        """Testa adição de documento fiscal"""
        dados = {
            'path_nome_arquivo': 'nfe123.xml',
            'hash_arquivo': 'hash123',
            'tipo_documento': 'NFe',
            'modelo': '55',
            'chave_acesso': '12345678901234567890123456789012345678901234',
            'numero_nf': '123',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'tipo_operacao': '1',
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa Teste LTDA',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente Teste',
            'valor_total': Decimal('1000.50'),
            'valor_produtos': Decimal('850.00'),
            'valor_icms': Decimal('150.50'),
            'cfop': '5102',
            'natureza_operacao': 'Venda de mercadoria'
        }
        
        doc = self.db.adicionar_documento(dados)
        
        assert doc.numero_sequencial is not None
        assert doc.tipo_documento == 'NFe'
        assert doc.numero_nf == '123'
        assert float(doc.valor_total) == 1000.50
        
        logger.info("✓ Teste de adição de documento - PASSOU")
    
    def test_verificar_documento_duplicado(self):
        """Testa detecção de documentos duplicados"""
        dados = {
            'path_nome_arquivo': 'nfe123.xml',
            'hash_arquivo': 'hash_unico_123',
            'tipo_documento': 'NFe',
            'chave_acesso': '12345678901234567890123456789012345678901234',
            'numero_nf': '123',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa Teste',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente Teste',
            'valor_total': Decimal('1000.00'),
            'cfop': '5102'
        }
        
        # Adicionar documento
        self.db.adicionar_documento(dados)
        
        # Verificar duplicado por hash
        duplicado = self.db.verificar_documento_duplicado(hash_arquivo='hash_unico_123')
        assert duplicado is not None
        assert duplicado.numero_nf == '123'
        
        # Verificar por chave de acesso
        duplicado2 = self.db.verificar_documento_duplicado(
            chave_acesso='12345678901234567890123456789012345678901234'
        )
        assert duplicado2 is not None
        
        # Verificar não existente
        nao_existe = self.db.verificar_documento_duplicado(hash_arquivo='nao_existe')
        assert nao_existe is None
        
        logger.info("✓ Teste de detecção de duplicados - PASSOU")
    
    def test_buscar_documentos(self):
        """Testa busca de documentos com filtros"""
        # Adicionar documentos
        for i in range(5):
            self.db.adicionar_documento({
                'path_nome_arquivo': f'nfe{i}.xml',
                'hash_arquivo': f'hash{i}',
                'tipo_documento': 'NFe' if i < 3 else 'NFCe',
                'chave_acesso': f'chave{i:044d}',
                'numero_nf': str(i),
                'serie': '1',
                'data_emissao': date(2025, 10, 14),
                'emitente_cnpj': '12345678000190',
                'emitente_nome': 'Empresa',
                'destinatario_cnpj': '98765432000100',
                'destinatario_nome': 'Cliente',
                'valor_total': Decimal('100.00'),
                'cfop': '5102'
            })
        
        # Buscar todos
        todos = self.db.buscar_documentos()
        assert len(todos) == 5
        
        # Buscar por tipo
        nfes = self.db.buscar_documentos(tipo_documento='NFe')
        assert len(nfes) == 3
        
        nfces = self.db.buscar_documentos(tipo_documento='NFCe')
        assert len(nfces) == 2
        
        logger.info("✓ Teste de busca de documentos - PASSOU")
    
    def test_marcar_como_processado_erp(self):
        """Testa marcação de documento como processado no ERP"""
        # Adicionar documento
        doc = self.db.adicionar_documento({
            'path_nome_arquivo': 'nfe_erp.xml',
            'hash_arquivo': 'hash_erp',
            'tipo_documento': 'NFe',
            'chave_acesso': 'chave' + '0' * 39,
            'numero_nf': '999',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente',
            'valor_total': Decimal('500.00'),
            'cfop': '5102',
            'erp_processado': False
        })
        
        # Marcar como processado
        sucesso = self.db.marcar_como_processado_erp(
            documento_id=doc.numero_sequencial,
            usuario='teste_usuario',
            observacoes='Processado com sucesso'
        )
        
        assert sucesso is True
        
        # Verificar que foi marcado
        docs = self.db.buscar_documentos(erp_processado=True)
        assert len(docs) == 1
        assert docs[0].erp_usuario == 'teste_usuario'
        
        logger.info("✓ Teste de marcação ERP - PASSOU")
    
    def test_estatisticas_documentos(self):
        """Testa estatísticas de documentos"""
        # Adicionar documentos variados
        self.db.adicionar_documento({
            'path_nome_arquivo': 'doc1.xml',
            'hash_arquivo': 'h1',
            'tipo_documento': 'NFe',
            'chave_acesso': 'c' + '1' * 43,
            'numero_nf': '1',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente',
            'valor_total': Decimal('1000.00'),
            'valor_icms': Decimal('180.00'),
            'cfop': '5102'
        })
        
        self.db.adicionar_documento({
            'path_nome_arquivo': 'doc2.xml',
            'hash_arquivo': 'h2',
            'tipo_documento': 'NFCe',
            'chave_acesso': 'c' + '2' * 43,
            'numero_nf': '2',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente',
            'valor_total': Decimal('500.00'),
            'valor_icms': Decimal('90.00'),
            'cfop': '5102'
        })
        
        stats = self.db.obter_estatisticas_documentos()
        
        assert stats['total_documentos'] == 2
        assert stats['por_tipo']['NFe'] == 1
        assert stats['por_tipo']['NFCe'] == 1
        assert stats['valores']['total'] == 1500.00
        assert stats['valores']['icms'] == 270.00
        
        logger.info("✓ Teste de estatísticas de documentos - PASSOU")
    
    def test_documento_to_dict(self):
        """Testa conversão de documento para dicionário"""
        doc = self.db.adicionar_documento({
            'path_nome_arquivo': 'doc_dict.xml',
            'hash_arquivo': 'hash_dict',
            'tipo_documento': 'NFe',
            'chave_acesso': 'c' + '3' * 43,
            'numero_nf': '999',
            'serie': '1',
            'data_emissao': date(2025, 10, 14),
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa Teste',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente Teste',
            'valor_total': Decimal('750.00'),
            'valor_icms': Decimal('135.00'),
            'cfop': '5102',
            'items_json': [{'item': 1, 'descricao': 'Produto A'}]
        })
        
        doc_dict = doc.to_dict()
        
        assert doc_dict['numero_nf'] == '999'
        assert doc_dict['tipo_documento'] == 'NFe'
        assert doc_dict['valores']['total'] == 750.00
        assert doc_dict['impostos']['icms'] == 135.00
        assert doc_dict['emitente']['nome'] == 'Empresa Teste'
        assert len(doc_dict['items']) == 1
        
        logger.info("✓ Teste de conversão para dict - PASSOU")


def executar_todos_testes():
    """Executa todos os testes manualmente"""
    print("\n" + "="*60)
    print("🧪 FISCALIA - Testes do Database Manager")
    print("="*60 + "\n")
    
    test = TestDatabaseManager()
    
    testes = [
        ("Adicionar Registro Sucesso", test.test_adicionar_registro_resultado_sucesso),
        ("Adicionar Registro Insucesso", test.test_adicionar_registro_resultado_insucesso),
        ("Buscar Registros", test.test_buscar_registros_resultados),
        ("Estatísticas Processamento", test.test_estatisticas_processamento),
        ("Adicionar Documento", test.test_adicionar_documento),
        ("Verificar Duplicados", test.test_verificar_documento_duplicado),
        ("Buscar Documentos", test.test_buscar_documentos),
        ("Marcar Processado ERP", test.test_marcar_como_processado_erp),
        ("Estatísticas Documentos", test.test_estatisticas_documentos),
        ("Documento to Dict", test.test_documento_to_dict)
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        print(f"📋 Executando: {nome}")
        try:
            test.setup_method()
            teste_func()
            test.teardown_method()
            resultados.append((nome, True, None))
            print(f"   ✅ PASSOU\n")
        except Exception as e:
            resultados.append((nome, False, str(e)))
            print(f"   ❌ FALHOU: {e}\n")
    
    # Resumo
    print("="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    total = len(resultados)
    passou = sum(1 for _, status, _ in resultados if status)
    falhou = total - passou
    
    print(f"\nTotal de testes: {total}")
    print(f"✅ Passou: {passou}")
    print(f"❌ Falhou: {falhou}")
    print(f"Taxa de sucesso: {passou/total*100:.1f}%\n")
    
    if falhou > 0:
        print("Testes que falharam:")
        for nome, status, erro in resultados:
            if not status:
                print(f"  ❌ {nome}: {erro}")
    
    print("="*60 + "\n")
    
    return falhou == 0


if __name__ == "__main__":
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)
