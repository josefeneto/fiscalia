# src/crew/tasks/xml_tasks.py - ARQUIVO COMPLETO

"""
Tasks para processamento e análise de XMLs de Notas Fiscais
"""

from crewai import Task
from typing import List


def create_single_xml_processing_task(agent, file_path: str) -> Task:
    """
    Task para processar um único arquivo XML
    
    Args:
        agent: Agente que executará a task
        file_path: Caminho do arquivo XML
    """
    
    task = Task(
        description=f"""
Processe o arquivo XML de Nota Fiscal localizado em:
{file_path}

INSTRUÇÕES:
1. Use a tool 'single_xml_processor' para processar o arquivo
2. Extraia e valide todos os dados da nota fiscal
3. Verifique se o arquivo foi salvo corretamente no banco de dados
4. Informe o status do processamento de forma clara

IMPORTANTE: Seja objetivo e informe apenas o resultado essencial.
""",
        expected_output=(
            "Confirmação do processamento com número da NF, valor total e status "
            "(sucesso, duplicado ou erro). Máximo 5 linhas."
        ),
        agent=agent
    )
    
    return task


def create_batch_xml_processing_task(agent, folder_path: str = "entrados", max_files: int = 100) -> Task:
    """
    Task para processar múltiplos XMLs em batch
    
    Args:
        agent: Agente que executará a task
        folder_path: Caminho da pasta (default: 'entrados')
        max_files: Limite de arquivos (default: 100)
    """
    
    task = Task(
        description=f"""
Processe em BATCH todos os arquivos XML de Notas Fiscais da pasta: {folder_path}

INSTRUÇÕES:
1. Use a tool 'batch_xml_processor' para processar todos os XMLs
2. Limite: {max_files} arquivos
3. Analise o relatório de processamento retornado
4. Resuma os principais resultados

IMPORTANTE: Seja conciso. Foque em números e status geral.
""",
        expected_output=(
            "Resumo executivo do processamento batch: total processado, sucessos, "
            "falhas, duplicatas. Máximo 10 linhas."
        ),
        agent=agent
    )
    
    return task


def create_compliance_audit_task(agent, context_tasks: List[Task] = None) -> Task:
    """
    Task para auditoria de conformidade fiscal
    
    Args:
        agent: Agente auditor
        context_tasks: Tasks anteriores para contexto
    """
    
    task = Task(
        description="""
Realize uma AUDITORIA FISCAL completa dos documentos processados.

ANÁLISES OBRIGATÓRIAS:
1. Use 'fiscal_analysis' com type='summary' para visão geral
2. Use 'fiscal_analysis' com type='anomalies' para detectar valores atípicos
3. Use 'fiscal_analysis' com type='tax_summary' para análise tributária

FOCO:
- Identifique valores suspeitos ou atípicos
- Verifique carga tributária
- Aponte possíveis inconsistências

IMPORTANTE: Seja crítico mas objetivo. Destaque apenas anomalias relevantes.
""",
        expected_output=(
            "Relatório de auditoria fiscal com: resumo geral, anomalias detectadas "
            "(se houver), análise da carga tributária. Máximo 15 linhas."
        ),
        agent=agent,
        context=context_tasks or []
    )
    
    return task


def create_business_analysis_task(agent, context_tasks: List[Task] = None) -> Task:
    """
    Task para análise de negócios e geração de insights
    
    Args:
        agent: Agente analista
        context_tasks: Tasks anteriores para contexto
    """
    
    task = Task(
        description="""
Gere um RELATÓRIO EXECUTIVO com insights acionáveis sobre os documentos fiscais.

ANÁLISES OBRIGATÓRIAS:
1. Use 'fiscal_analysis' com type='by_state' para análise geográfica
2. Use 'fiscal_analysis' com type='by_emitter' para top emitentes
3. Use 'database_query' para estatísticas complementares

INSIGHTS ESPERADOS:
- Principais tendências nos dados
- Concentração geográfica de operações
- Top fornecedores/clientes
- Oportunidades ou riscos identificados

IMPORTANTE: Seja estratégico. Foco em insights que ajudem decisões de negócio.
""",
        expected_output=(
            "Relatório executivo com: principais KPIs, análise geográfica, "
            "top emitentes e 2-3 insights estratégicos acionáveis. Máximo 20 linhas."
        ),
        agent=agent,
        context=context_tasks or []
    )
    
    return task


if __name__ == "__main__":
    """Teste standalone - apenas verificar criação"""
    print("=== Teste de Tasks XML ===\n")
    
    # Mock agent
    class MockAgent:
        role = "Test Agent"
    
    agent = MockAgent()
    
    # Teste criação de tasks
    task1 = create_single_xml_processing_task(agent, "/path/to/file.xml")
    print(f"✅ Task 1 criada: Single XML Processing")
    
    task2 = create_batch_xml_processing_task(agent)
    print(f"✅ Task 2 criada: Batch XML Processing")
    
    task3 = create_compliance_audit_task(agent)
    print(f"✅ Task 3 criada: Compliance Audit")
    
    task4 = create_business_analysis_task(agent)
    print(f"✅ Task 4 criada: Business Analysis")
    
    print("\n✅ Todas as tasks criadas com sucesso!")
