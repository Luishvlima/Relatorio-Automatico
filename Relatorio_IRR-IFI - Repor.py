import sys
import os
import warnings
from datetime import datetime

#======================IMPORTS DAS FUNÇÕES DE CADA RELATÓRIO=====================
from RELATORIO_OFS import main_OFS
from RELATORIO_AIR import main_AIR
from CARREGAR_DADOS import carregar_dados
from CRIACAO_DASHBOARD import criacao_dashboard
from LOG import configurar_logger
from AGENDADOR import executar_agendador
from EXCLUSAO_DEFENDER import tentar_setup_primeira_execucao,criar_configuracao_defender,_tem_privilegio_admin,configurar_exclusoes_defender

from CRIAR_PASTAS import (criar_estrutura, 
    PASTA_DATA_ARQUIVO_BRUTO, 
    PASTA_DATA_IMAGENS_BRUTO,
    PASTA_DATA_ARQUIVO_TRATADO,
    PASTA_DATA_IMAGENS_TRATADO,
    PASTA_CONFIGURACOES,
    PASTA_EDGE,
    PASTA_LOGS, 
    ARQUIVO_FLAG_SETUP, 
    ARQUIVO_STATUS_SETUP,
)

# =============================================================================
# Configurações,constantes globais e credencias
# =============================================================================
# Horarios de execução (sem Agendador de Tarefas do Windows)
AGENDADOR_HORAS     = ("04:00", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00","11:30", "12:00","12:30", "13:00","13:30", "14:00","14:30", "15:00","15:30", "16:00","16:30", "17:00","17:30", "18:00","18:30", "19:00", "19:30", "20:00", "20:30")

# A lista de pessoas(Chat_ids) que receberão a mensagem no Telegram. 
CHAT_IDS_TELEGRAM   = []

# Unidades
UNIDADES_C16 = []
UNIDADES_C17 = []
MAPAS_CLUSTER = {
    "Cluster 16": UNIDADES_C16,
    "Cluster 17": UNIDADES_C17
}
TODAS_UNIDADES = UNIDADES_C16 + UNIDADES_C17

# Altere somente se precisar
TOKEN_AIR           = ""  # Token do air 
TOKEN_TELEGRAM      = "" # Token do bot do Telegram

# Credenciais e configurações para login automático

EMAIL               = ""
ORACLE_PASSWORD     = ""
MICROSOFT_PASSWORD  = ""

# Configurações de nomes de arquivos e pastas
REGIAO              = ""  
NOME_AIR            = f"Relatorio_AIR-{REGIAO}.xlsx"
NOME_OFS            = f"Relatorio_OFS-{REGIAO}.xlsx"
NOME_IRR_IFI        = f"Relatorio_IRR-IFI-{REGIAO}.xlsx"
NOME_LOG            = f"Relatorio_IRR-IFI-{REGIAO}"
COOKIE_FILE         = os.path.join(PASTA_CONFIGURACOES, f"cookies_{REGIAO}.json")  # Arquivo de cookies para login automático

MENSAGEM            = "Relatório de IRR e INF Atualizado! 📊✅"  # Mensagem personalizada para o Telegram

# =======================IGNORAR WARNINGS ==========================
warnings.filterwarnings("ignore",category=UserWarning,module="openpyxl")
# =============================================================================
# CONFIGURAÇÃO DO DEFENDER
# =============================================================================

def montar_cfg_defender(log_defender=None):
    return criar_configuracao_defender(
        log= log_defender or LOG,
        base_dir=os.path.dirname(PASTA_LOGS),
        script_path=os.path.abspath(__file__),
        pastas=[
            PASTA_DATA_ARQUIVO_BRUTO,
            PASTA_DATA_IMAGENS_BRUTO,
            PASTA_DATA_ARQUIVO_TRATADO,
            PASTA_DATA_IMAGENS_TRATADO,
            PASTA_CONFIGURACOES,
            PASTA_EDGE,
            PASTA_LOGS,
        ],
        processo=sys.executable,
        arquivo_flag=ARQUIVO_FLAG_SETUP,
        arquivo_status=ARQUIVO_STATUS_SETUP,
    )

#=============================================================================
# Telegram
#=============================================================================
def executar_telegram(links:list):
    print("")
    from TELEGRAM import main_telegram
    try:
        LOG.info("=" * 60)
        LOG.info("ETAPA 2/2 - ENVIO DO DASHBOARD")
        for link in links:
            main_telegram( log=LOG, caminho_da_imagem = link, mensagem = MENSAGEM, token=TOKEN_TELEGRAM, chat_ids=CHAT_IDS_TELEGRAM )
        LOG.info("ETAPA 2/2 - CONCLUÍDA. TODOS OS DASHBOARDS FORAM ENVIADOS COM SUCESSO.")
        LOG.info("=" * 60)
        print("")
    except Exception as e:
        LOG.error(f"Falha ao enviar mensagens pelo Telegram: {e}")

# ======================================================
# MAIN
# ======================================================
LOG = configurar_logger(PASTA_LOGS, NOME_LOG)

def main():
    #===========================CONFIGURAÇÃO DO LOGGER E DEFENDER===========================
    global LOG
    LOG = configurar_logger(PASTA_LOGS, NOME_LOG)
    cfg_defender = montar_cfg_defender(LOG)
    #===============================CRIAR ESTRUTURA DE PASTAS===============================
    criar_estrutura()

    #====================TENTAR CONFIGURAR DEFENDER NA PRIMEIRA EXECUÇÃO====================
    tentar_setup_primeira_execucao(cfg_defender)

    #==================================PROCESSO DE DOWNLOAD=================================
    agora = datetime.now().strftime("%H:%M")
    try:
        #==================EXECUTA O DOWNLOAD DO RELATÓRIO AIR ÀS 04:00===================
        if agora == "04:00":
            main_AIR(log=LOG, pasta_data_arquivo_bruto=PASTA_DATA_ARQUIVO_BRUTO, nome_arquivo=NOME_AIR, token_air=TOKEN_AIR)
        #=============EXECUTA O DOWNLOAD APENAS DO RELATÓRIO OFS NOS DEMAIS HORÁRIOS============
        else:    
            main_OFS(log=LOG, 
                     cookies_file=COOKIE_FILE, 
                     pasta_edge_profile=PASTA_EDGE, 
                     pasta_data_arquivo_bruto=PASTA_DATA_ARQUIVO_BRUTO, 
                     nome_arquivo=NOME_OFS, 
                     microsoft_password=MICROSOFT_PASSWORD, 
                     oracle_password=ORACLE_PASSWORD,
                     email=EMAIL,)
            dicionarios = carregar_dados(LOG, PASTA_DATA_ARQUIVO_BRUTO, PASTA_DATA_ARQUIVO_TRATADO, TODAS_UNIDADES, MAPAS_CLUSTER, NOME_IRR_IFI, NOME_AIR, NOME_OFS)
            links = criacao_dashboard(LOG, PASTA_DATA_IMAGENS_TRATADO, dicionarios)
            executar_telegram(links)
            

    except Exception as e:
        LOG.error(f"Falha na execução principal: {e}")
        return False
    
if __name__ == "__main__":
    argumentos = sys.argv[1:]

    if "--setup" in argumentos:
        criar_estrutura()
        origem_auto = "--setup-origem-auto" in argumentos
        cfg_defender = montar_cfg_defender(LOG)
        if _tem_privilegio_admin():
            ok_setup = configurar_exclusoes_defender(cfg_defender)
        else:
            LOG.warning("SETUP requer privilégios de administrador. Execute como administrador só uma vez!.")
            ok_setup = False

        if origem_auto:
            try:
                with open(ARQUIVO_STATUS_SETUP, "w", encoding="utf-8") as f:
                    f.write("OK" if ok_setup else "FAIL")
            except Exception:
                pass

        if ok_setup:
            with open(ARQUIVO_FLAG_SETUP, "w", encoding="utf-8") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
    elif "--agendador" in argumentos:
        horarios_execucao = AGENDADOR_HORAS
        for arg in argumentos:
            if arg.startswith("--horas="):
                horarios_execucao = arg.split("=", 1)[1].strip()
                break
            if arg.startswith("--hora="):
                horarios_execucao = arg.split("=", 1)[1].strip()
                break

        ok_agendador = executar_agendador(
            horarios_execucao=horarios_execucao,
            executar_agora=("--agora" in argumentos),
            cfg_setup=montar_cfg_defender(LOG),
            log= configurar_logger(PASTA_LOGS, NOME_LOG),
            criar_estrutura=criar_estrutura,
            tentar_setup_primeira_execucao=tentar_setup_primeira_execucao,
            main = main
        )
        sys.exit(0 if ok_agendador else 1)
    elif "--help" in argumentos or "-h" in argumentos:
        print("Uso:")
        print("  python Backlog.py")
        print("  python Backlog.py --setup")
        print("  python Backlog.py --uma-vez")
        print("  python Backlog.py --agendador [--horas=HH:MM,HH:MM] [--agora]")
        print("")
        print("Exemplos:")
        print("  python Backlog.py                  # roda agora e continua automático")
        print("  python Backlog.py --uma-vez")
        print("  python Backlog.py --agendador --horas=07:00,12:00,18:30")
        print("  python Backlog.py --agendador --hora=18:30 --agora")
        sys.exit(0)
    elif "--uma-vez" in argumentos:
        ok = main()
        sys.exit(0 if ok else 1)
    else:
        ok_agendador = executar_agendador(
            horarios_execucao=AGENDADOR_HORAS,
            executar_agora=True,
            cfg_setup=montar_cfg_defender(LOG),
            log= configurar_logger(PASTA_LOGS, NOME_LOG),
            criar_estrutura=criar_estrutura,
            tentar_setup_primeira_execucao=tentar_setup_primeira_execucao,
            main = main
        )
        sys.exit(0 if ok_agendador else 1)