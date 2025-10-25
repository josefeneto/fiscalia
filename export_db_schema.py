"""
Script para exportar schema da base de dados SQLite
Gera ficheiro com DDL completo
"""

import sqlite3
from pathlib import Path

# Caminho para a BD
DB_PATH = Path("data/bd_fiscalia.db")  # Ajusta se necessário

def export_schema():
    """Exporta schema completo da BD"""
    
    if not DB_PATH.exists():
        print(f"❌ Base de dados não encontrada: {DB_PATH}")
        return
    
    # Conectar à BD
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*60)
    print("📊 SCHEMA DA BASE DE DADOS FISCALIA")
    print("="*60)
    print()
    
    # Obter lista de tabelas
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    tables = cursor.fetchall()
    
    print(f"📋 Tabelas encontradas: {len(tables)}")
    for (table_name,) in tables:
        print(f"  - {table_name}")
    print()
    print("="*60)
    print()
    
    # Para cada tabela, obter DDL e info
    schema_output = []
    
    for (table_name,) in tables:
        print(f"\n{'='*60}")
        print(f"📄 TABELA: {table_name}")
        print('='*60)
        
        # Obter DDL (CREATE TABLE)
        cursor.execute(f"""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        ddl = cursor.fetchone()[0]
        
        print("\n🔧 DDL (CREATE TABLE):")
        print("-"*60)
        print(ddl)
        print()
        
        schema_output.append(f"-- Tabela: {table_name}")
        schema_output.append(ddl + ";")
        schema_output.append("")
        
        # Obter informação das colunas
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("📋 Colunas:")
        print("-"*60)
        print(f"{'Nome':<30} {'Tipo':<15} {'NOT NULL':<10} {'Default':<20} {'PK'}")
        print("-"*60)
        
        for col in columns:
            cid, name, dtype, notnull, default_val, pk = col
            notnull_str = "YES" if notnull else "NO"
            default_str = str(default_val) if default_val else "-"
            pk_str = "🔑" if pk else ""
            print(f"{name:<30} {dtype:<15} {notnull_str:<10} {default_str:<20} {pk_str}")
        
        print()
        
        # Contar registos
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"📊 Número de registos: {count}")
        
        # Se houver registos, mostrar exemplo
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample = cursor.fetchone()
            
            print("\n💡 Exemplo de registo (primeiras colunas):")
            print("-"*60)
            col_names = [col[1] for col in columns]
            for i, (col_name, value) in enumerate(zip(col_names, sample)):
                if i < 10:  # Mostrar só primeiras 10 colunas
                    value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"{col_name}: {value_str}")
        
        print()
    
    # Obter índices
    print("\n" + "="*60)
    print("🔍 ÍNDICES")
    print("="*60)
    print()
    
    cursor.execute("""
        SELECT name, tbl_name, sql 
        FROM sqlite_master 
        WHERE type='index' AND sql IS NOT NULL
        ORDER BY tbl_name, name
    """)
    indexes = cursor.fetchall()
    
    if indexes:
        for idx_name, table_name, sql in indexes:
            print(f"📌 {idx_name} (tabela: {table_name})")
            print(f"   {sql}")
            print()
            schema_output.append(f"-- Índice: {idx_name}")
            schema_output.append(sql + ";")
            schema_output.append("")
    else:
        print("(Nenhum índice encontrado)")
    
    conn.close()
    
    # Salvar schema em ficheiro
    from datetime import datetime
    output_file = Path("database_schema.sql")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- ================================================\n")
        f.write("-- FISCALIA - Database Schema\n")
        f.write(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- ================================================\n\n")
        f.write("\n".join(schema_output))
    
    print("\n" + "="*60)
    print(f"✅ Schema exportado para: {output_file.absolute()}")
    print("="*60)


if __name__ == "__main__":
    export_schema()