# =============================================================================
# IMPORTS
# =============================================================================
import os
import sys
import ctypes

# =============================================================================
# DIRETÓRIO BASE
# =============================================================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ===================Estrutura de pastas padronizada ==========================
PASTA_DATA_ARQUIVO_BRUTO    = os.path.join(BASE_DIR, "data", "Bruto_Arquivos")      # Relatórios XLSX baixados da API
PASTA_DATA_IMAGENS_BRUTO    = os.path.join(BASE_DIR, "data", "Bruto_Imagens")       # Cards gerados em JPEG
PASTA_DATA_ARQUIVO_TRATADO  = os.path.join(BASE_DIR, "data", "Tratado_Arquivos")    # Relatórios XLSX filtrados
PASTA_DATA_IMAGENS_TRATADO  = os.path.join(BASE_DIR, "data", "Tratado_Imagens")     # Dashboards gerados em JPEG
PASTA_CONFIGURACOES         = os.path.join(BASE_DIR, "data", "Configuracoes")       # Arquivos de configuração do sistema
PASTA_EDGE                  = os.path.join(BASE_DIR, "data", "Edge_Profile")        # Arquivos de configuração do Edge
PASTA_LOGS                  = os.path.join(BASE_DIR, "logs")                        # Logs de execução e erros(Oculto)

ARQUIVO_FLAG_SETUP          = os.path.join(PASTA_CONFIGURACOES, ".defender_setup_primeira_execucao.flag")
ARQUIVO_STATUS_SETUP        = os.path.join(PASTA_CONFIGURACOES, ".defender_setup_status.tmp")

# =============================================================================
# CRIAR PASTAS
# =============================================================================
def criar_estrutura():
    for pasta in [PASTA_DATA_ARQUIVO_BRUTO, PASTA_DATA_IMAGENS_BRUTO, PASTA_DATA_ARQUIVO_TRATADO,PASTA_DATA_IMAGENS_TRATADO, PASTA_LOGS, PASTA_CONFIGURACOES, PASTA_EDGE]:
        os.makedirs(pasta, exist_ok=True)
    
    # Oculta a pasta de logs e configurações no Windows
    ctypes.windll.kernel32.SetFileAttributesW(PASTA_LOGS, 2)
    ctypes.windll.kernel32.SetFileAttributesW(PASTA_CONFIGURACOES, 2)

    return {
        "PASTA_DATA_ARQUIVO_BRUTO"  : PASTA_DATA_ARQUIVO_BRUTO,
        "PASTA_DATA_IMAGENS_BRUTO"  : PASTA_DATA_IMAGENS_BRUTO,
        "PASTA_DATA_ARQUIVO_TRATADO": PASTA_DATA_ARQUIVO_TRATADO,
        "PASTA_DATA_IMAGENS_TRATADO": PASTA_DATA_IMAGENS_TRATADO,
        "PASTA_CONFIGURACOES"       : PASTA_CONFIGURACOES,
        "PASTA_EDGE"                : PASTA_EDGE,
        "PASTA_LOGS"                : PASTA_LOGS,
        "PASTA_BASE"                : BASE_DIR,
        "ARQUIVO_FLAG_SETUP"        : ARQUIVO_FLAG_SETUP,
        "ARQUIVO_STATUS_SETUP"      : ARQUIVO_STATUS_SETUP,
    }