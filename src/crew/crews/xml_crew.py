# src/crew/crews/xml_crew.py - ARQUIVO COMPLETO

"""
Crews para processamento de XMLs de Notas Fiscais
"""

from crewai import Crew
from typing import Dict
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from crew.agents.xml_agents import (
    create_xml_processing_coordinator,
    create_fiscal_compliance_auditor,
    create_business_analyst
)
from crew.tasks.xml_tasks import (
    create_single_xml_processing_task,
    create_batch_xml_processing_task,
    create_compliance_audit_task,
    create_business_analysis_task
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SingleXMLCrew:
    """
    Crew para processar um único arquivo XML
    Workflow: Processamento → Resultado
    """
    
    def __init__(self):
        self.coordinator = create_xml_processing_coordinator()
        logger.info("SingleXMLCrew inicializado")
    
    def process(self, file_path: str) -> Dict:
        """
        Processa um único arquivo XML
        
        Args:
            file_path: Caminho do arquivo XML
            
        Returns:
            Resultado do processamento
        """
        try:
            logger.info(f"Iniciando processamento de {file_path}")
            
            # Criar task
            task = create_single_xml_processing_task(self.coordinator, file_path)
            
            # Criar e executar crew
            crew = Crew(
                agents=[self.coordinator],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            logger.info("Processamento concluído com sucesso")
            
            return {
                'success': True,
                'result': str(result),
                'file': file_path
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }


class BatchXMLCrew:
    """
    Crew para processar múltiplos XMLs com análise completa
    Workflow: Processamento Batch → Auditoria → Análise de Negócios
    """
    
    def __init__(self):
        self.coordinator = create_xml_processing_coordinator()
        self.auditor = create_fiscal_compliance_auditor()
        self.analyst = create_business_analyst()
        logger.info("BatchXMLCrew inicializado")
    
    def process(self, folder_path: str = "entrados", max_files: int = 100) -> Dict:
        """
        Processa múltiplos XMLs e gera análises
        
        Args:
            folder_path: Pasta com XMLs (default: 'entrados')
            max_files: Limite de arquivos (default: 100)
            
        Returns:
            Resultado completo com análises
        """
        try:
            logger.info(f"Iniciando processamento batch de {folder_path}")
            
            # Criar tasks encadeadas
            task1 = create_batch_xml_processing_task(
                self.coordinator, 
                folder_path, 
                max_files
            )
            
            task2 = create_compliance_audit_task(
                self.auditor,
                context_tasks=[task1]
            )
            
            task3 = create_business_analysis_task(
                self.analyst,
                context_tasks=[task1, task2]
            )
            
            # Criar e executar crew
            crew = Crew(
                agents=[self.coordinator, self.auditor, self.analyst],
                tasks=[task1, task2, task3],
                verbose=True
            )
            
            result = crew.kickoff()
            
            logger.info("Processamento batch completo")
            
            return {
                'success': True,
                'result': str(result),
                'folder': folder_path
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento batch: {e}")
            return {
                'success': False,
                'error': str(e),
                'folder': folder_path
            }


class AnalysisOnlyCrew:
    """
    Crew apenas para análise (sem processamento)
    Para quando documentos já estão no banco
    Workflow: Auditoria → Análise de Negócios
    """
    
    def __init__(self):
        self.auditor = create_fiscal_compliance_auditor()
        self.analyst = create_business_analyst()
        logger.info("AnalysisOnlyCrew inicializado")
    
    def analyze(self) -> Dict:
        """
        Analisa documentos já processados no banco
        
        Returns:
            Análises completas
        """
        try:
            logger.info("Iniciando análise de documentos existentes")
            
            # Criar tasks de análise
            task1 = create_compliance_audit_task(self.auditor)
            task2 = create_business_analysis_task(
                self.analyst,
                context_tasks=[task1]
            )
            
            # Criar e executar crew
            crew = Crew(
                agents=[self.auditor, self.analyst],
                tasks=[task1, task2],
                verbose=True
            )
            
            result = crew.kickoff()
            
            logger.info("Análise concluída")
            
            return {
                'success': True,
                'result': str(result)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == "__main__":
    """Teste standalone das crews"""
    print("=== Teste de Crews XML ===\n")
    
    try:
        # Teste 1: SingleXMLCrew
        print("1. Testando SingleXMLCrew...")
        single_crew = SingleXMLCrew()
        print(f"   ✅ SingleXMLCrew criado")
        print(f"   Agentes: 1 (Coordinator)\n")
        
        # Teste 2: BatchXMLCrew
        print("2. Testando BatchXMLCrew...")
        batch_crew = BatchXMLCrew()
        print(f"   ✅ BatchXMLCrew criado")
        print(f"   Agentes: 3 (Coordinator, Auditor, Analyst)\n")
        
        # Teste 3: AnalysisOnlyCrew
        print("3. Testando AnalysisOnlyCrew...")
        analysis_crew = AnalysisOnlyCrew()
        print(f"   ✅ AnalysisOnlyCrew criado")
        print(f"   Agentes: 2 (Auditor, Analyst)\n")
        
        print("✅ Todas as crews criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar crews: {e}")
        import traceback
        traceback.print_exc()
