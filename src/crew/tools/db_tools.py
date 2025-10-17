# src/crew/tools/db_tools.py - ARQUIVO COMPLETO

"""
Tools para interagir com banco de dados bd_fiscalia
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager


class DatabaseQueryInput(BaseModel):
    """Input schema para DatabaseQueryTool"""
    query_type: str = Field(
        description="Tipo de consulta: 'count_docs', 'count_results', 'recent_docs', 'stats'"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Limite de resultados para consultas que retornam lista"
    )


class DatabaseQueryTool(BaseTool):
    """
    Tool para consultar banco de dados bd_fiscalia.db
    Permite verificar estatísticas e dados processados
    """
    
    name: str = "database_query"
    description: str = (
        "Consulta banco de dados bd_fiscalia para obter estatísticas e informações "
        "sobre notas fiscais processadas. "
        "Tipos de consulta disponíveis:\n"
        "- 'count_docs': conta documentos em docs_para_erp\n"
        "- 'count_results': conta registros de processamento\n"
        "- 'recent_docs': lista documentos recentes\n"
        "- 'stats': estatísticas gerais"
    )
    args_schema: Type[BaseModel] = DatabaseQueryInput
    
    def _run(self, query_type: str, limit: int = 10) -> str:
        """
        Executa consulta no banco de dados
        
        Args:
            query_type: Tipo de consulta
            limit: Limite de resultados
            
        Returns:
            Resultado formatado como string
        """
        try:
            db = DatabaseManager()
            
            if query_type == 'count_docs':
                count = db.count_documents()
                return f"Total de documentos processados: {count}"
            
            elif query_type == 'count_results':
                count = db.count_results()
                return f"Total de registros de processamento: {count}"
            
            elif query_type == 'recent_docs':
                docs = db.get_recent_documents(limit=limit)
                if not docs:
                    return "Nenhum documento encontrado no banco de dados"
                
                result = f"Últimos {len(docs)} documentos processados:\n\n"
                for doc in docs:
                    result += (
                        f"- Número: {doc.numero_nf}, "
                        f"Valor: R$ {doc.valor_total:.2f}, "
                        f"Emitente: {doc.razao_social_emitente}\n"
                    )
                return result
            
            elif query_type == 'stats':
                # Estatísticas consolidadas
                count_docs = db.count_documents()
                count_results = db.count_results()
                
                stats = f"""
Estatísticas do Sistema Fiscalia:
================================
- Documentos processados: {count_docs}
- Registros de processamento: {count_results}
- Status do banco: Operacional ✓
"""
                return stats.strip()
            
            else:
                return f"Tipo de consulta inválido: {query_type}"
                
        except Exception as e:
            return f"Erro ao consultar banco de dados: {str(e)}"


# Função helper para criar a tool
def create_database_query_tool():
    """Factory function para criar DatabaseQueryTool"""
    return DatabaseQueryTool()


if __name__ == "__main__":
    """Teste standalone da tool"""
    print("=== Teste DatabaseQueryTool ===\n")
    
    tool = create_database_query_tool()
    
    # Teste 1: Contar documentos
    print("1. Contando documentos:")
    result = tool._run("count_docs")
    print(f"   {result}\n")
    
    # Teste 2: Estatísticas
    print("2. Estatísticas gerais:")
    result = tool._run("stats")
    print(f"   {result}\n")
    
    # Teste 3: Documentos recentes
    print("3. Documentos recentes:")
    result = tool._run("recent_docs", limit=5)
    print(f"   {result}\n")
    
    print("✅ Teste da tool concluído!")
