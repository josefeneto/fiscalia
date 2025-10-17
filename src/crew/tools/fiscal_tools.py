# src/crew/tools/fiscal_tools.py - ARQUIVO COMPLETO CORRIGIDO

"""
Tools para análise fiscal e compliance
"""

from crewai.tools import BaseTool
from typing import Type, Dict, List
from pydantic import BaseModel, Field
from pathlib import Path
import sys

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FiscalAnalysisInput(BaseModel):
    """Input schema para FiscalAnalysisTool"""
    analysis_type: str = Field(
        description="Tipo de análise: 'summary', 'by_state', 'by_emitter', 'anomalies', 'tax_summary'"
    )
    limit: int = Field(
        default=20,
        description="Limite de resultados para análises que retornam lista"
    )


class FiscalAnalysisTool(BaseTool):
    """
    Tool para análise fiscal avançada dos documentos processados
    """
    
    name: str = "fiscal_analysis"
    description: str = (
        "Analisa documentos fiscais processados no banco de dados. "
        "Tipos de análise disponíveis:\n"
        "- 'summary': Resumo geral de todos documentos\n"
        "- 'by_state': Análise por UF (estado)\n"
        "- 'by_emitter': Análise por emitente\n"
        "- 'anomalies': Detecta valores atípicos e anomalias\n"
        "- 'tax_summary': Sumário de impostos (ICMS, IPI, PIS, COFINS)"
    )
    args_schema: Type[BaseModel] = FiscalAnalysisInput
    
    def _run(self, analysis_type: str, limit: int = 20) -> str:
        """
        Executa análise fiscal
        
        Args:
            analysis_type: Tipo de análise
            limit: Limite de resultados
            
        Returns:
            Relatório de análise formatado
        """
        try:
            db = DatabaseManager()
            session = db.get_session()
            
            if analysis_type == 'summary':
                return self._summary_analysis(session)
            
            elif analysis_type == 'by_state':
                return self._by_state_analysis(session, limit)
            
            elif analysis_type == 'by_emitter':
                return self._by_emitter_analysis(session, limit)
            
            elif analysis_type == 'anomalies':
                return self._anomalies_analysis(session)
            
            elif analysis_type == 'tax_summary':
                return self._tax_summary_analysis(session)
            
            else:
                return f"❌ Tipo de análise inválido: {analysis_type}"
                
        except Exception as e:
            logger.error(f"Erro na análise fiscal: {e}")
            return f"❌ Erro na análise fiscal: {str(e)}"
        finally:
            session.close()
    
    def _summary_analysis(self, session) -> str:
        """Análise resumida geral"""
        from database.models import DocParaERP
        from sqlalchemy import func
        
        stats = session.query(
            func.count(DocParaERP.id).label('total'),
            func.sum(DocParaERP.valor_total).label('valor_total'),
            func.avg(DocParaERP.valor_total).label('valor_medio'),
            func.max(DocParaERP.valor_total).label('valor_maximo'),
            func.min(DocParaERP.valor_total).label('valor_minimo'),
            func.sum(DocParaERP.valor_icms).label('total_icms'),
            func.sum(DocParaERP.valor_ipi).label('total_ipi'),
            func.sum(DocParaERP.valor_pis).label('total_pis'),
            func.sum(DocParaERP.valor_cofins).label('total_cofins'),
        ).first()
        
        return f"""
📊 RESUMO GERAL DE DOCUMENTOS FISCAIS
==================================================

📈 ESTATÍSTICAS GERAIS:
- Total de documentos: {stats.total or 0}
- Valor total: R$ {stats.valor_total or 0:,.2f}
- Valor médio: R$ {stats.valor_medio or 0:,.2f}
- Valor máximo: R$ {stats.valor_maximo or 0:,.2f}
- Valor mínimo: R$ {stats.valor_minimo or 0:,.2f}

💰 IMPOSTOS TOTAIS:
- ICMS: R$ {stats.total_icms or 0:,.2f}
- IPI: R$ {stats.total_ipi or 0:,.2f}
- PIS: R$ {stats.total_pis or 0:,.2f}
- COFINS: R$ {stats.total_cofins or 0:,.2f}
- Total Impostos: R$ {(stats.total_icms or 0) + (stats.total_ipi or 0) + (stats.total_pis or 0) + (stats.total_cofins or 0):,.2f}
""".strip()
    
    def _by_state_analysis(self, session, limit) -> str:
        """Análise por estado"""
        from database.models import DocParaERP
        from sqlalchemy import func
        
        results = session.query(
            DocParaERP.uf_emitente,
            func.count(DocParaERP.id).label('quantidade'),
            func.sum(DocParaERP.valor_total).label('valor_total')
        ).group_by(
            DocParaERP.uf_emitente
        ).order_by(
            func.sum(DocParaERP.valor_total).desc()
        ).limit(limit).all()
        
        if not results:
            return "⚠️ Nenhum dado encontrado para análise por estado"
        
        relatorio = f"""
📍 ANÁLISE POR ESTADO (UF)
==================================================

"""
        for uf, qtd, valor in results:
            uf_nome = uf or 'N/A'
            relatorio += f"• {uf_nome}: {qtd} documentos - R$ {valor or 0:,.2f}\n"
        
        return relatorio.strip()
    
    def _by_emitter_analysis(self, session, limit) -> str:
        """Análise por emitente"""
        from database.models import DocParaERP
        from sqlalchemy import func
        
        results = session.query(
            DocParaERP.razao_social_emitente,
            DocParaERP.cnpj_emitente,
            func.count(DocParaERP.id).label('quantidade'),
            func.sum(DocParaERP.valor_total).label('valor_total')
        ).group_by(
            DocParaERP.razao_social_emitente,
            DocParaERP.cnpj_emitente
        ).order_by(
            func.sum(DocParaERP.valor_total).desc()
        ).limit(limit).all()
        
        if not results:
            return "⚠️ Nenhum dado encontrado para análise por emitente"
        
        relatorio = f"""
🏢 TOP {limit} EMITENTES POR VALOR
==================================================

"""
        for razao, cnpj, qtd, valor in results:
            razao_nome = razao or 'N/A'
            cnpj_fmt = cnpj or 'N/A'
            relatorio += f"• {razao_nome[:40]}\n  CNPJ: {cnpj_fmt} | {qtd} NFs | R$ {valor or 0:,.2f}\n\n"
        
        return relatorio.strip()
    
    def _anomalies_analysis(self, session) -> str:
        """Detecta anomalias - SEM STDDEV (SQLite não suporta)"""
        from database.models import DocParaERP
        from sqlalchemy import func
        
        # Calcular média
        media_result = session.query(
            func.avg(DocParaERP.valor_total).label('media')
        ).first()
        
        media = media_result.media or 0
        
        # Buscar total de docs
        total_docs = session.query(func.count(DocParaERP.id)).scalar() or 0
        
        if total_docs == 0:
            return """
🔍 DETECÇÃO DE ANOMALIAS
==================================================

⚠️  Nenhum documento para analisar
"""
        
        # Valores muito acima da média (> 3x média)
        limite_superior = media * 3 if media > 0 else 0
        
        outliers_altos = session.query(DocParaERP).filter(
            DocParaERP.valor_total > limite_superior
        ).order_by(DocParaERP.valor_total.desc()).limit(10).all()
        
        # Valores muito baixos (< 10% da média)
        limite_inferior = media * 0.1 if media > 0 else 0
        
        outliers_baixos = session.query(DocParaERP).filter(
            DocParaERP.valor_total < limite_inferior,
            DocParaERP.valor_total > 0
        ).order_by(DocParaERP.valor_total.asc()).limit(5).all()
        
        relatorio = f"""
🔍 DETECÇÃO DE ANOMALIAS
==================================================

📊 ESTATÍSTICAS BASE:
- Total de documentos: {total_docs}
- Valor médio: R$ {media:,.2f}
- Limite superior (3x média): R$ {limite_superior:,.2f}
- Limite inferior (10% média): R$ {limite_inferior:,.2f}

⚠️  VALORES ATÍPICOS ENCONTRADOS: {len(outliers_altos) + len(outliers_baixos)}

"""
        
        if outliers_altos:
            relatorio += "🔴 VALORES MUITO ACIMA DA MÉDIA:\n\n"
            for doc in outliers_altos:
                relatorio += f"• NF {doc.numero_nf}: R$ {doc.valor_total:,.2f}\n"
                relatorio += f"  Emitente: {doc.razao_social_emitente or 'N/A'}\n"
                relatorio += f"  Diferença da média: +R$ {doc.valor_total - media:,.2f}\n\n"
        
        if outliers_baixos:
            relatorio += "🟡 VALORES MUITO ABAIXO DA MÉDIA:\n\n"
            for doc in outliers_baixos:
                relatorio += f"• NF {doc.numero_nf}: R$ {doc.valor_total:,.2f}\n"
                relatorio += f"  Emitente: {doc.razao_social_emitente or 'N/A'}\n\n"
        
        if not outliers_altos and not outliers_baixos:
            relatorio += "✓ Nenhum valor atípico detectado\n"
        
        return relatorio.strip()
    
    def _tax_summary_analysis(self, session) -> str:
        """Sumário de impostos"""
        from database.models import DocParaERP
        from sqlalchemy import func
        
        stats = session.query(
            func.count(DocParaERP.id).label('total_docs'),
            func.sum(DocParaERP.valor_produtos).label('total_produtos'),
            func.sum(DocParaERP.base_calculo_icms).label('base_icms'),
            func.sum(DocParaERP.valor_icms).label('total_icms'),
            func.sum(DocParaERP.valor_ipi).label('total_ipi'),
            func.sum(DocParaERP.valor_pis).label('total_pis'),
            func.sum(DocParaERP.valor_cofins).label('total_cofins'),
        ).first()
        
        valor_produtos = stats.total_produtos or 0
        total_impostos = (stats.total_icms or 0) + (stats.total_ipi or 0) + (stats.total_pis or 0) + (stats.total_cofins or 0)
        
        carga_tributaria = (total_impostos / valor_produtos * 100) if valor_produtos > 0 else 0
        
        return f"""
💰 ANÁLISE TRIBUTÁRIA DETALHADA
==================================================

📋 BASE DE CÁLCULO:
- Total de documentos: {stats.total_docs or 0}
- Valor de produtos: R$ {valor_produtos:,.2f}
- Base de cálculo ICMS: R$ {stats.base_icms or 0:,.2f}

📊 IMPOSTOS POR TIPO:
- ICMS: R$ {stats.total_icms or 0:,.2f}
- IPI: R$ {stats.total_ipi or 0:,.2f}
- PIS: R$ {stats.total_pis or 0:,.2f}
- COFINS: R$ {stats.total_cofins or 0:,.2f}

💼 RESUMO TRIBUTÁRIO:
- Total de impostos: R$ {total_impostos:,.2f}
- Carga tributária efetiva: {carga_tributaria:.2f}%

📈 ALÍQUOTAS MÉDIAS:
- ICMS: {(stats.total_icms / stats.base_icms * 100) if stats.base_icms else 0:.2f}%
- IPI: {(stats.total_ipi / valor_produtos * 100) if valor_produtos else 0:.2f}%
- PIS: {(stats.total_pis / valor_produtos * 100) if valor_produtos else 0:.2f}%
- COFINS: {(stats.total_cofins / valor_produtos * 100) if valor_produtos else 0:.2f}%
""".strip()


# Factory function
def create_fiscal_analysis_tool():
    """Factory function para FiscalAnalysisTool"""
    return FiscalAnalysisTool()


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste Fiscal Analysis Tool ===\n")
    
    tool = create_fiscal_analysis_tool()
    print(f"✅ Tool criada: {tool.name}\n")
    
    # Teste summary
    result = tool._run("summary")
    print(result)
    
    print("\n✅ Fiscal Analysis Tool funcionando!")
