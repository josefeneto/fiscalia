# src/crew/agents/__init__.py - ARQUIVO COMPLETO

"""
Agentes do CrewAI
"""

from crew.agents.test_agent import create_test_agent
from crew.agents.xml_agents import (
    create_xml_processing_coordinator,
    create_fiscal_compliance_auditor,
    create_business_analyst
)

__all__ = [
    'create_test_agent',
    'create_xml_processing_coordinator',
    'create_fiscal_compliance_auditor',
    'create_business_analyst'
]
