# src/crew/tools/xml_tools.py - ARQUIVO COMPLETO

"""
Tools para processamento de XMLs de Notas Fiscais
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from pathlib import Path
import sys

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from processors.nfe_processor import NFeProcessor
from utils.config import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BatchProcessorInput(BaseModel):
    """Input schema para BatchProcessorTool"""
    folder_path: str = Field(
        description="Caminho da pasta com arquivos XML para processar. Use 'entrados' para pasta padrão."
    )
    max_files: int = Field(
        default=100,
        description="Número máximo de arquivos a processar (default: 100)"
    )


class BatchProcessorTool(BaseTool):
    """
    Tool para processar múltiplos arquivos XML em batch
    Usa o NFeProcessor existente para cada arquivo
    """
    
    name: str = "batch_xml_processor"
    description: str = (
        "Processa múltiplos arquivos XML de Notas Fiscais em batch. "
        "Recebe um caminho de pasta e processa todos os XMLs encontrados. "
        "Retorna estatísticas do processamento: sucessos, falhas, duplicatas."
    )
    args_schema: Type[BaseModel] = BatchProcessorInput
    
    def _run(self, folder_path: str, max_files: int = 100) -> str:
        """
        Processa arquivos XML em batch
        
        Args:
            folder_path: Caminho da pasta (ou 'entrados' para usar padrão)
            max_files: Limite de arquivos
            
        Returns:
            Relatório de processamento formatado
        """
        try:
            settings = get_settings()
            
            # Resolver path
            if folder_path.lower() == 'entrados':
                path = settings.pasta_entrados
            else:
                path = Path(folder_path)
            
            if not path.exists():
                return f"❌ Pasta não encontrada: {path}"
            
            # Buscar arquivos XML
            xml_files = list(path.glob("*.xml"))[:max_files]
            
            if not xml_files:
                return f"⚠️ Nenhum arquivo XML encontrado em {path}"
            
            # Processar cada arquivo
            processor = NFeProcessor()
            results = {
                'total': len(xml_files),
                'sucesso': 0,
                'falha': 0,
                'duplicado': 0,
                'detalhes': []
            }
            
            for xml_file in xml_files:
                result = processor.process_file(xml_file)
                
                if result['success']:
                    results['sucesso'] += 1
                    results['detalhes'].append({
                        'arquivo': xml_file.name,
                        'status': 'Sucesso',
                        'numero_nf': result['data'].get('numero_nf', 'N/A'),
                        'valor': result['data'].get('valor_total', 0.0)
                    })
                elif 'duplicado' in result['message'].lower():
                    results['duplicado'] += 1
                    results['detalhes'].append({
                        'arquivo': xml_file.name,
                        'status': 'Duplicado',
                        'mensagem': result['message']
                    })
                else:
                    results['falha'] += 1
                    results['detalhes'].append({
                        'arquivo': xml_file.name,
                        'status': 'Erro',
                        'mensagem': result['message']
                    })
            
            # Formatar relatório
            relatorio = f"""
📊 RELATÓRIO DE PROCESSAMENTO BATCH
{'='*50}

📁 Pasta: {path}
📄 Total de arquivos: {results['total']}

RESULTADOS:
✅ Processados com sucesso: {results['sucesso']}
❌ Falhas: {results['falha']}
⚠️  Duplicados: {results['duplicado']}

DETALHES POR ARQUIVO:
"""
            
            for detalhe in results['detalhes'][:10]:  # Primeiros 10
                if detalhe['status'] == 'Sucesso':
                    relatorio += f"\n✅ {detalhe['arquivo']}: NF {detalhe['numero_nf']} - R$ {detalhe['valor']:.2f}"
                elif detalhe['status'] == 'Duplicado':
                    relatorio += f"\n⚠️  {detalhe['arquivo']}: {detalhe['mensagem']}"
                else:
                    relatorio += f"\n❌ {detalhe['arquivo']}: {detalhe['mensagem']}"
            
            if len(results['detalhes']) > 10:
                relatorio += f"\n... e mais {len(results['detalhes']) - 10} arquivos"
            
            return relatorio.strip()
            
        except Exception as e:
            logger.error(f"Erro no processamento batch: {e}")
            return f"❌ Erro no processamento batch: {str(e)}"


class SingleXMLProcessorInput(BaseModel):
    """Input schema para SingleXMLProcessorTool"""
    file_path: str = Field(
        description="Caminho completo do arquivo XML a processar"
    )


class SingleXMLProcessorTool(BaseTool):
    """
    Tool para processar um único arquivo XML
    """
    
    name: str = "single_xml_processor"
    description: str = (
        "Processa um único arquivo XML de Nota Fiscal. "
        "Extrai dados, valida, e salva no banco de dados. "
        "Retorna informações detalhadas do processamento."
    )
    args_schema: Type[BaseModel] = SingleXMLProcessorInput
    
    def _run(self, file_path: str) -> str:
        """
        Processa um único arquivo XML
        
        Args:
            file_path: Caminho do arquivo XML
            
        Returns:
            Resultado do processamento formatado
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return f"❌ Arquivo não encontrado: {file_path}"
            
            if not path.suffix.lower() == '.xml':
                return f"❌ Arquivo não é XML: {file_path}"
            
            # Processar
            processor = NFeProcessor()
            result = processor.process_file(path)
            
            if result['success']:
                data = result['data']
                relatorio = f"""
✅ ARQUIVO PROCESSADO COM SUCESSO

📄 Arquivo: {path.name}
📋 Número NF: {data['numero_nf']}
💰 Valor Total: R$ {data['valor_total']:.2f}
🆔 ID no Banco: {data['doc_id']}

✓ Arquivo movido para /processados
"""
                return relatorio.strip()
            else:
                return f"""
❌ ERRO NO PROCESSAMENTO

📄 Arquivo: {path.name}
⚠️  Erro: {result['message']}

O arquivo foi movido para /rejeitados
"""
                
        except Exception as e:
            logger.error(f"Erro ao processar XML: {e}")
            return f"❌ Erro ao processar {file_path}: {str(e)}"


# Factory functions
def create_batch_processor_tool():
    """Factory function para BatchProcessorTool"""
    return BatchProcessorTool()


def create_single_xml_processor_tool():
    """Factory function para SingleXMLProcessorTool"""
    return SingleXMLProcessorTool()


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste XML Tools ===\n")
    
    # Teste Batch Processor
    tool = create_batch_processor_tool()
    print(f"✅ Tool criada: {tool.name}")
    print(f"   Descrição: {tool.description}\n")
    
    # Simular processamento (ajuste o path se necessário)
    # result = tool._run("entrados", max_files=5)
    # print(result)
    
    print("\n✅ XML Tools criadas com sucesso!")
