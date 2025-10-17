# src/crew/tools/__init__.py - ARQUIVO COMPLETO

"""
Tools customizadas para CrewAI
"""

from crew.tools.db_tools import DatabaseQueryTool, create_database_query_tool
from crew.tools.xml_tools import (
    BatchProcessorTool,
    SingleXMLProcessorTool,
    create_batch_processor_tool,
    create_single_xml_processor_tool
)
from crew.tools.fiscal_tools import FiscalAnalysisTool, create_fiscal_analysis_tool

__all__ = [
    'DatabaseQueryTool',
    'create_database_query_tool',
    'BatchProcessorTool',
    'SingleXMLProcessorTool',
    'create_batch_processor_tool',
    'create_single_xml_processor_tool',
    'FiscalAnalysisTool',
    'create_fiscal_analysis_tool'
]
