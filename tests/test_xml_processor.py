"""
Testes para processadores de Notas Fiscais
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.processors.xml_processor import XMLProcessor
from src.processors.validator import NFValidator
from src.processors.file_handler import FileHandler
from src.processors.nfe_processor import NFeProcessor


class TestXMLProcessor:
    """Testes do processador XML"""
    
    def test_initialization(self):
        """Testa inicialização do processador"""
        processor = XMLProcessor()
        assert processor.current_file is None
        assert processor.xml_root is None
        assert processor.doc_type is None
    
    def test_detect_doc_type(self):
        """Testa detecção de tipo de documento"""
        # Este teste precisará de XMLs de exemplo
        # Por enquanto, apenas estrutura
        processor = XMLProcessor()
        assert hasattr(processor, '_detect_doc_type')


class TestNFValidator:
    """Testes do validador"""
    
    def test_initialization(self):
        """Testa inicialização"""
        validator = NFValidator()
        assert validator.errors == []
        assert validator.warnings == []
    
    def test_validate_cnpj_valid(self):
        """Testa validação de CNPJ válido"""
        # CNPJ válido de exemplo
        assert NFValidator.validate_cnpj('00000000000191')  # CNPJ válido
    
    def test_validate_cnpj_invalid(self):
        """Testa validação de CNPJ inválido"""
        assert not NFValidator.validate_cnpj('12345678901234')
        assert not NFValidator.validate_cnpj('111111111111')
        assert not NFValidator.validate_cnpj('')
    
    def test_validate_cpf_valid(self):
        """Testa validação de CPF válido"""
        assert NFValidator.validate_cpf('00000000191')  # CPF válido
    
    def test_validate_cpf_invalid(self):
        """Testa validação de CPF inválido"""
        assert not NFValidator.validate_cpf('12345678901')
        assert not NFValidator.validate_cpf('11111111111')
        assert not NFValidator.validate_cpf('')
    
    def test_validate_empty_data(self):
        """Testa validação com dados vazios"""
        validator = NFValidator()
        result = validator.validate({})
        assert not result
        assert len(validator.errors) > 0
    
    def test_validation_report(self):
        """Testa geração de relatório"""
        validator = NFValidator()
        validator.errors.append("Erro teste")
        validator.warnings.append("Aviso teste")
        
        report = validator.get_validation_report()
        
        assert report['is_valid'] == False
        assert report['has_warnings'] == True
        assert report['error_count'] == 1
        assert report['warning_count'] == 1


class TestFileHandler:
    """Testes do gerenciador de arquivos"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)
    
    def test_initialization(self, temp_dir):
        """Testa inicialização"""
        handler = FileHandler(temp_dir)
        assert handler.base_path == temp_dir
        assert handler.entrados_path.exists()
        assert handler.processados_path.exists()
        assert handler.rejeitados_path.exists()
    
    def test_ensure_folders(self, temp_dir):
        """Testa criação de estrutura de pastas"""
        handler = FileHandler(temp_dir)
        
        # Verifica se pastas foram criadas
        assert (temp_dir / 'entrados').exists()
        assert (temp_dir / 'processados').exists()
        assert (temp_dir / 'rejeitados').exists()
    
    def test_is_supported_file(self, temp_dir):
        """Testa verificação de arquivo suportado"""
        handler = FileHandler(temp_dir)
        
        assert handler.is_supported_file(Path('test.xml'))
        assert handler.is_supported_file(Path('test.pdf'))
        assert handler.is_supported_file(Path('test.png'))
        assert not handler.is_supported_file(Path('test.txt'))
        assert not handler.is_supported_file(Path('test.doc'))
    
    def test_get_file_type(self, temp_dir):
        """Testa identificação de tipo de arquivo"""
        handler = FileHandler(temp_dir)
        
        assert handler.get_file_type(Path('nota.xml')) == 'xml'
        assert handler.get_file_type(Path('nota.pdf')) == 'pdf'
        assert handler.get_file_type(Path('nota.png')) == 'imagem'
        assert handler.get_file_type(Path('nota.jpg')) == 'imagem'
        assert handler.get_file_type(Path('nota.txt')) == 'desconhecido'
    
    def test_calculate_hash(self, temp_dir):
        """Testa cálculo de hash"""
        handler = FileHandler(temp_dir)
        
        # Cria arquivo de teste
        test_file = temp_dir / 'test.xml'
        test_file.write_text('<?xml version="1.0"?><test>data</test>')
        
        hash1 = handler.calculate_hash(test_file)
        assert hash1 != ""
        assert len(hash1) == 32  # MD5 tem 32 caracteres
        
        # Hash do mesmo arquivo deve ser igual
        hash2 = handler.calculate_hash(test_file)
        assert hash1 == hash2
    
    def test_get_pending_files(self, temp_dir):
        """Testa listagem de arquivos pendentes"""
        handler = FileHandler(temp_dir)
        
        # Cria alguns arquivos de teste
        (handler.entrados_path / 'test1.xml').write_text('test')
        (handler.entrados_path / 'test2.xml').write_text('test')
        (handler.entrados_path / 'test.txt').write_text('test')  # Não suportado
        
        pending = handler.get_pending_files()
        
        assert len(pending) == 2  # Apenas .xml
        assert all(f.suffix == '.xml' for f in pending)
    
    def test_move_to_processed(self, temp_dir):
        """Testa movimentação para processados"""
        handler = FileHandler(temp_dir)
        
        # Cria arquivo de teste
        test_file = handler.entrados_path / 'test.xml'
        test_file.write_text('test')
        
        success, new_path = handler.move_to_processed(test_file)
        
        assert success
        assert new_path is not None
        assert new_path.parent == handler.processados_path
        assert not test_file.exists()
        assert new_path.exists()
    
    def test_move_to_rejected(self, temp_dir):
        """Testa movimentação para rejeitados"""
        handler = FileHandler(temp_dir)
        
        test_file = handler.entrados_path / 'test.xml'
        test_file.write_text('test')
        
        success, new_path = handler.move_to_rejected(test_file)
        
        assert success
        assert new_path is not None
        assert new_path.parent == handler.rejeitados_path
        assert not test_file.exists()
    
    def test_get_stats(self, temp_dir):
        """Testa estatísticas"""
        handler = FileHandler(temp_dir)
        
        # Cria alguns arquivos
        (handler.entrados_path / 'test1.xml').write_text('test')
        (handler.processados_path / 'test2.xml').write_text('test')
        (handler.processados_path / 'test3.xml').write_text('test')
        (handler.rejeitados_path / 'test4.xml').write_text('test')
        
        stats = handler.get_stats()
        
        assert stats['entrados'] == 1
        assert stats['processados'] == 2
        assert stats['rejeitados'] == 1
        assert 'base_path' in stats
    
    def test_validate_file_structure(self, temp_dir):
        """Testa validação de estrutura de arquivo"""
        handler = FileHandler(temp_dir)
        
        # Arquivo não existe
        is_valid, msg = handler.validate_file_structure(temp_dir / 'nao_existe.xml')
        assert not is_valid
        assert "não encontrado" in msg.lower()
        
        # Arquivo vazio
        empty_file = temp_dir / 'empty.xml'
        empty_file.write_text('')
        is_valid, msg = handler.validate_file_structure(empty_file)
        assert not is_valid
        assert "vazio" in msg.lower()
        
        # Arquivo válido
        valid_file = temp_dir / 'valid.xml'
        valid_file.write_text('<?xml version="1.0"?><test/>')
        is_valid, msg = handler.validate_file_structure(valid_file)
        assert is_valid


class TestNFeProcessor:
    """Testes do processador principal"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)
    
    def test_initialization(self, temp_dir):
        """Testa inicialização do processador principal"""
        processor = NFeProcessor(temp_dir)
        
        assert processor.file_handler is not None
        assert processor.xml_processor is not None
        assert processor.validator is not None
        assert processor.db_manager is not None
    
    def test_get_statistics(self, temp_dir):
        """Testa obtenção de estatísticas"""
        processor = NFeProcessor(temp_dir)
        stats = processor.get_statistics()
        
        assert 'arquivos' in stats
        assert 'banco_dados' in stats
        assert 'timestamp' in stats
    
    def test_set_base_path(self, temp_dir):
        """Testa alteração de caminho base"""
        processor = NFeProcessor(temp_dir)
        
        new_path = temp_dir / 'novo_caminho'
        processor.set_base_path(new_path)
        
        assert processor.file_handler.base_path == new_path


def run_tests():
    """Executa todos os testes"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()