:: === Create directory structure safely ===
IF NOT EXIST "src\crew" mkdir "src\crew"
IF NOT EXIST "src\database" mkdir "src\database"
IF NOT EXIST "src\processors" mkdir "src\processors"
IF NOT EXIST "src\utils" mkdir "src\utils"
IF NOT EXIST "streamlit_app\pages" mkdir "streamlit_app\pages"
IF NOT EXIST "streamlit_app\components" mkdir "streamlit_app\components"
IF NOT EXIST "arquivos\entrados" mkdir "arquivos\entrados"
IF NOT EXIST "arquivos\processados" mkdir "arquivos\processados"
IF NOT EXIST "arquivos\rejeitados" mkdir "arquivos\rejeitados"
IF NOT EXIST "data" mkdir "data"
IF NOT EXIST "tests" mkdir "tests"
IF NOT EXIST ".github\workflows" mkdir ".github\workflows"

:: === Create __init__.py files ===
type nul > src\__init__.py
type nul > src\crew\__init__.py
type nul > src\database\__init__.py
type nul > src\processors\__init__.py
type nul > src\utils\__init__.py
type nul > streamlit_app\__init__.py
type nul > streamlit_app\components\__init__.py
type nul > tests\__init__.py


:: === DEPOIS DE CRIADA A ESTRUTURA - Criar .gitkeep nos diretórios de arquivos
type nul > arquivos/entrados/.gitkeep
type nul > arquivos/processados/.gitkeep
type nul > arquivos/rejeitados/.gitkeep
type nul > data/.gitkeep
type nul > logs/.gitkeep


