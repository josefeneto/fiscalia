"""
Script para explorar e testar o banco de dados manualmente
Execute: python explore_db.py
"""
import sys
import os
from pathlib import Path
from datetime import date
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent))

# Configurar nível de log para modo silencioso
os.environ['LOG_LEVEL'] = 'WARNING'

from src.database.db_manager import get_db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def menu_principal():
    """Menu interativo para explorar o database"""
    print("\n" + "="*60)
    print("🗄️  FISCALIA - Explorador de Database")
    print("="*60)
    print("\nOpções:")
    print("1. Ver estatísticas gerais")
    print("2. Adicionar registro de teste")
    print("3. Adicionar documento de teste")
    print("4. Listar últimos registros")
    print("5. Listar últimos documentos")
    print("6. Buscar documento por número")
    print("7. Ver estatísticas de documentos")
    print("8. Limpar banco de dados (CUIDADO!)")
    print("9. Ajuda - Como usar")
    print("0. Sair")
    print("="*60)


def ver_estatisticas():
    """Mostra estatísticas gerais"""
    db = get_db_manager()
    
    print("\n📊 Estatísticas de Processamento:")
    stats_proc = db.obter_estatisticas_processamento()
    print(f"   Total processamentos: {stats_proc['total_processamentos']}")
    print(f"   Sucessos: {stats_proc['total_sucesso']}")
    print(f"   Insucessos: {stats_proc['total_insucesso']}")
    print(f"   Taxa de sucesso: {stats_proc['taxa_sucesso']}%")
    
    print("\n📈 Estatísticas de Documentos:")
    stats_docs = db.obter_estatisticas_documentos()
    print(f"   Total documentos: {stats_docs['total_documentos']}")
    
    if stats_docs['por_tipo']:
        print("   Por tipo:")
        for tipo, count in stats_docs['por_tipo'].items():
            print(f"      {tipo}: {count}")
    
    print(f"\n   Valores totais: R$ {stats_docs['valores']['total']:,.2f}")
    print(f"   ICMS total: R$ {stats_docs['valores']['icms']:,.2f}")
    print(f"   IPI total: R$ {stats_docs['valores']['ipi']:,.2f}")
    print(f"   PIS total: R$ {stats_docs['valores']['pis']:,.2f}")
    print(f"   COFINS total: R$ {stats_docs['valores']['cofins']:,.2f}")
    
    print(f"\n   ERP Processados: {stats_docs['erp']['processados']}")
    print(f"   ERP Pendentes: {stats_docs['erp']['pendentes']}")


def adicionar_registro_teste():
    """Adiciona um registro de teste"""
    db = get_db_manager()
    
    print("\n➕ Adicionar Registro de Teste")
    resultado = input("Resultado (Sucesso/Insucesso): ").strip() or "Sucesso"
    causa = input("Causa: ").strip() or "Teste manual"
    
    registro = db.adicionar_registro_resultado(
        path_nome_arquivo=f"teste/arquivo_manual_{date.today()}.xml",
        resultado=resultado,
        causa=causa,
        tipo_arquivo="XML",
        tamanho_bytes=1024,
        hash_arquivo=f"hash_{date.today()}"
    )
    
    print(f"✅ Registro adicionado com ID: {registro.numero_sequencial}")


def adicionar_documento_teste():
    """Adiciona um documento de teste"""
    db = get_db_manager()
    
    print("\n➕ Adicionar Documento de Teste")
    print("   (Pressione ENTER para usar valores padrão)")
    
    numero_nf_input = input("Número da NF [999]: ").strip()
    numero_nf = numero_nf_input if numero_nf_input else "999"
    
    valor_input = input("Valor total [1000.00]: ").strip()
    valor = valor_input if valor_input else "1000.00"
    
    # Remover aspas se usuário digitou com aspas
    numero_nf = numero_nf.strip('"\'')
    valor = valor.strip('"\'')
    
    try:
        # Converter valor para float
        valor_float = float(valor)
        
        # Gerar chave de acesso única
        import random
        chave_base = f"{numero_nf}{random.randint(1000, 9999)}"
        chave_acesso = f"chave{chave_base.zfill(40)}"
        
        documento = db.adicionar_documento({
            'path_nome_arquivo': f'teste_nfe_{numero_nf}.xml',
            'hash_arquivo': f'hash_teste_{numero_nf}_{date.today().strftime("%Y%m%d")}',
            'tipo_documento': 'NFe',
            'modelo': '55',
            'chave_acesso': chave_acesso,
            'numero_nf': numero_nf,
            'serie': '1',
            'data_emissao': date.today(),
            'tipo_operacao': '1',
            'emitente_cnpj': '12345678000190',
            'emitente_nome': 'Empresa Teste LTDA',
            'emitente_uf': 'SP',
            'destinatario_cnpj': '98765432000100',
            'destinatario_nome': 'Cliente Teste',
            'destinatario_uf': 'RJ',
            'valor_total': Decimal(str(valor_float)),
            'valor_produtos': Decimal(str(valor_float * 0.85)),
            'valor_icms': Decimal(str(valor_float * 0.15)),
            'cfop': '5102',
            'natureza_operacao': 'Venda de mercadoria',
            'items_json': [
                {
                    'numero': 1,
                    'codigo': 'PROD001',
                    'descricao': 'Produto Teste',
                    'quantidade': 10,
                    'valor_unitario': valor_float / 10,
                    'valor_total': valor_float
                }
            ]
        })
        
        print(f"\n✅ Documento adicionado com sucesso!")
        print(f"   ID: {documento.numero_sequencial}")
        print(f"   Número NF: {documento.numero_nf}")
        print(f"   Valor: R$ {float(documento.valor_total):,.2f}")
        print(f"   Chave: {documento.chave_acesso}")
        
    except ValueError as e:
        print(f"\n❌ Erro: Valor inválido. Digite apenas números (ex: 1000 ou 1000.50)")
        print(f"   Detalhe: {e}")
    except Exception as e:
        print(f"\n❌ Erro ao adicionar documento: {e}")


def listar_registros():
    """Lista últimos registros"""
    db = get_db_manager()
    
    registros = db.buscar_registros_resultados(limite=10)
    
    if not registros:
        print("\n⚠️  Nenhum registro encontrado")
        return
    
    print(f"\n📋 Últimos {len(registros)} Registros:")
    print("-" * 60)
    
    for reg in registros:
        print(f"ID: {reg.numero_sequencial} | {reg.time_stamp.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Resultado: {reg.resultado}")
        print(f"   Arquivo: {reg.path_nome_arquivo}")
        if reg.causa:
            print(f"   Causa: {reg.causa}")
        print("-" * 60)


def listar_documentos():
    """Lista últimos documentos"""
    db = get_db_manager()
    
    docs = db.buscar_documentos(limite=10)
    
    if not docs:
        print("\n⚠️  Nenhum documento encontrado")
        return
    
    print(f"\n📄 Últimos {len(docs)} Documentos:")
    print("-" * 60)
    
    for doc in docs:
        print(f"ID: {doc.numero_sequencial} | {doc.tipo_documento} | NF: {doc.numero_nf}")
        print(f"   Data: {doc.data_emissao.strftime('%d/%m/%Y')}")
        print(f"   Emitente: {doc.emitente_nome} ({doc.emitente_cnpj})")
        print(f"   Destinatário: {doc.destinatario_nome} ({doc.destinatario_cnpj})")
        print(f"   Valor: R$ {float(doc.valor_total):,.2f}")
        print(f"   ERP: {'✅ Processado' if doc.erp_processado else '⏳ Pendente'}")
        print("-" * 60)


def buscar_documento():
    """Busca documento por número"""
    db = get_db_manager()
    
    numero = input("\nNúmero da NF: ").strip()
    
    docs = db.buscar_documentos(limite=100)
    encontrados = [d for d in docs if d.numero_nf == numero]
    
    if not encontrados:
        print(f"\n⚠️  Nenhum documento encontrado com número {numero}")
        return
    
    print(f"\n📄 Documentos encontrados: {len(encontrados)}")
    
    for doc in encontrados:
        print("\n" + "="*60)
        doc_dict = doc.to_dict()
        
        print(f"ID: {doc_dict['numero_sequencial']}")
        print(f"Tipo: {doc_dict['tipo_documento']} - Modelo {doc_dict['modelo']}")
        print(f"Número: {doc_dict['numero_nf']} - Série: {doc_dict['serie']}")
        print(f"Data Emissão: {doc_dict['data_emissao']}")
        print(f"Chave: {doc_dict['chave_acesso']}")
        
        print(f"\nEmitente:")
        print(f"   Nome: {doc_dict['emitente']['nome']}")
        print(f"   CNPJ: {doc_dict['emitente']['cnpj']}")
        print(f"   UF: {doc_dict['emitente']['uf']}")
        
        print(f"\nDestinatário:")
        print(f"   Nome: {doc_dict['destinatario']['nome']}")
        print(f"   CNPJ: {doc_dict['destinatario']['cnpj']}")
        print(f"   UF: {doc_dict['destinatario']['uf']}")
        
        print(f"\nValores:")
        print(f"   Total: R$ {doc_dict['valores']['total']:,.2f}")
        print(f"   Produtos: R$ {doc_dict['valores']['produtos']:,.2f}")
        
        print(f"\nImpostos:")
        print(f"   ICMS: R$ {doc_dict['impostos']['icms']:,.2f}")
        print(f"   Total Impostos: R$ {doc.get_total_impostos():,.2f}")
        
        print(f"\nFiscal:")
        print(f"   CFOP: {doc_dict['fiscal']['cfop']}")
        print(f"   Natureza: {doc_dict['fiscal']['natureza_operacao']}")


def mostrar_ajuda():
    """Mostra ajuda sobre como usar o explorador"""
    print("\n" + "="*60)
    print("📖 AJUDA - Como Usar o Explorador de Database")
    print("="*60)
    
    print("\n🎯 CONCEITOS BÁSICOS:")
    print("   • Não use aspas ao digitar valores")
    print("   • Pressione ENTER para usar valores padrão")
    print("   • Números devem ser digitados sem formatação")
    
    print("\n📋 OPÇÃO 1: Ver Estatísticas Gerais")
    print("   Mostra resumo de processamentos e documentos")
    print("   Uso: Apenas selecione a opção")
    
    print("\n📝 OPÇÃO 2: Adicionar Registro de Teste")
    print("   Adiciona um registro de processamento")
    print("   Exemplos:")
    print("      Resultado: Sucesso  (ou Insucesso)")
    print("      Causa: Teste manual")
    
    print("\n📄 OPÇÃO 3: Adicionar Documento de Teste")
    print("   Adiciona uma Nota Fiscal de teste")
    print("   Exemplos de entrada:")
    print("      ✅ CORRETO:")
    print("         Número da NF: 1234")
    print("         Valor total: 1000.50")
    print("      ❌ ERRADO:")
    print("         Número da NF: \"1234\"  (não use aspas)")
    print("         Valor total: R$ 1.000,50  (não use formatação)")
    
    print("\n📊 OPÇÃO 4: Listar Últimos Registros")
    print("   Mostra últimos 10 registros de processamento")
    
    print("\n📑 OPÇÃO 5: Listar Últimos Documentos")
    print("   Mostra últimas 10 Notas Fiscais processadas")
    
    print("\n🔍 OPÇÃO 6: Buscar Documento por Número")
    print("   Busca uma NF específica")
    print("   Exemplo: Digite apenas o número (ex: 123)")
    
    print("\n📈 OPÇÃO 7: Ver Estatísticas de Documentos")
    print("   Mostra estatísticas detalhadas com valores totais")
    
    print("\n⚠️  OPÇÃO 8: Limpar Banco de Dados")
    print("   CUIDADO! Apaga TODOS os dados")
    print("   Requer confirmação: digite CONFIRMAR")
    
    print("\n💡 DICAS:")
    print("   • Use SQLite Studio para visualização gráfica")
    print("   • Database local: data/bd_fiscalia.db")
    print("   • Faça backups antes de limpar dados")
    print("   • Valores monetários: use ponto decimal (1000.50)")
    
    print("\n" + "="*60)


def limpar_banco():
    """Limpa o banco de dados (CUIDADO!)"""
    db = get_db_manager()
    
    print("\n⚠️  ATENÇÃO: Esta ação irá APAGAR TODOS OS DADOS!")
    confirmacao = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirmacao == "CONFIRMAR":
        db.limpar_tabelas(confirmar=True)
        print("✅ Banco de dados limpo!")
    else:
        print("❌ Operação cancelada")


def main():
    """Função principal"""
    while True:
        menu_principal()
        
        try:
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "0":
                print("\n👋 Até logo!")
                break
            elif opcao == "1":
                ver_estatisticas()
            elif opcao == "2":
                adicionar_registro_teste()
            elif opcao == "3":
                adicionar_documento_teste()
            elif opcao == "4":
                listar_registros()
            elif opcao == "5":
                listar_documentos()
            elif opcao == "6":
                buscar_documento()
            elif opcao == "7":
                ver_estatisticas()
            elif opcao == "8":
                limpar_banco()
            elif opcao == "9":
                mostrar_ajuda()
            else:
                print("❌ Opção inválida!")
            
            input("\nPressione ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            logger.error(f"Erro no menu: {e}", exc_info=True)
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
