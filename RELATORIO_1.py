# =============================================================================
# IMPORTS
# =============================================================================

import os
import time
import requests
import pandas as pd
from datetime import date, datetime

# =============================================================================
# CONFIGURAÇÕES — Altere APENAS este bloco quando precisar mudar informações da API.
# (Altere com Cautela) 
# (Com muita cautela)
# =============================================================================
def definir_API(token_air):
    global URL_BASE_API, HEADERS_API
    URL_BASE_API = "<REMOVIDO POR SEGURANÇA>"
    HEADERS_API  = {
        "accept":       "application/json, text/plain, */*",
        "origin":       "<REMOVIDO POR SEGURANÇA>",
        "referer":      "<REMOVIDO POR SEGURANÇA>",
        "token":        token_air,
        "user-agent":   "Mozilla/5.0"
    }


# =============================================================================
# CONFIGURAÇÕES — Altere APENAS este bloco quando precisar mudar informações básicas.
# (Altere com Cautela)
# =============================================================================

FILENAME_PRAZO_REPAROS  = "<REMOVIDO POR SEGURANÇA>"
ENDPOINT_PRAZO_REPAROS  = "<REMOVIDO POR SEGURANÇA>"
TIMEOUT_CONEXAO         = 30      # Aumentado de 10 para 30s
TIMEOUT_LEITURA         = 3600    # Reduzido de 3600 (1h)
MAX_TENTATIVAS          = 5
ESPERA_TENTATIVA        = 15

# =============================================================================
# Atualizar as datas de início e fim para o momento atual
# =============================================================================

#Datas
DATA_INICIO     = pd.Timestamp(date.today()) - pd.DateOffset(months=1)
DATA_INICIO     = DATA_INICIO.strftime("%Y-%m-%d")
DATA_FIM        = date.today().strftime("%Y-%m-%d")

def atualizar_periodo_datas():
    global DATA_INICIO, DATA_FIM
    hoje = date.today()
    DATA_INICIO     = pd.Timestamp(date.today()) - pd.DateOffset(months=1)
    DATA_INICIO     = DATA_INICIO.strftime("%Y-%m-%d")
    DATA_FIM        = hoje.strftime("%Y-%m-%d")
# =============================================================================
# DOWNLOAD
# =============================================================================

def baixar_prazo_de_reparos() -> str:
    LOG.info("=== Baixando: Prazo de Reparos ===")

    payload = [
        {"id": 1575, "nome": "Inicio", "tipo": "date", "opcoes": "Inicio", "posicao": 0, "novo": False, "valor": DATA_INICIO},
        {"id": 1576, "nome": "Fim",    "tipo": "date", "opcoes": "Fim",    "posicao": 1, "novo": False, "valor": DATA_FIM}
    ]

    url      = f"{URL_BASE_API}/criar_xls/{ENDPOINT_PRAZO_REPAROS}"

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        caminho = os.path.join(PASTA_DATA_ARQUIVO_BRUTO, FILENAME_PRAZO_REPAROS)
        LOG.info(f"Tentativa {tentativa}/{MAX_TENTATIVAS}...")
        try:
            response = requests.post(
                url,
                headers=HEADERS_API,
                json=payload,
                timeout=(TIMEOUT_CONEXAO, TIMEOUT_LEITURA),
                stream=True
            )

            if response.status_code == 200:
                caminho = os.path.join(PASTA_DATA_ARQUIVO_BRUTO, FILENAME_PRAZO_REPAROS)

                if os.path.exists(caminho):
                    os.remove(caminho)

                total = 0
                with open(caminho, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
                            print(f"\r  Baixando... {total / 1024 / 1024:.1f} MB", end="")
                print()

                LOG.info(f"Download concluído: {FILENAME_PRAZO_REPAROS} ({total/1024/1024:.1f} MB)")
                return caminho

        except requests.exceptions.ConnectionError:
            LOG.warning("Sem conexão com a API.")
        except requests.exceptions.Timeout:
            LOG.warning(f"Timeout na tentativa {tentativa}.")
        except requests.exceptions.HTTPError as e:
            LOG.warning(f"Erro HTTP: {e}")
        except KeyboardInterrupt:
            LOG.warning("Sinal de interrupção recebido durante o download. Tentando novamente...")
            try:
                #Se interromper o processo, apague o arquivo que estava sendo criado para evitar erro depois.
                if os.path.exists(caminho):
                    os.remove(caminho)
            except Exception:
                pass
        except Exception as e:
            LOG.error(f"Erro inesperado: {e}")

        if tentativa < MAX_TENTATIVAS:
            LOG.info(f"Aguardando {ESPERA_TENTATIVA}s...")
            time.sleep(ESPERA_TENTATIVA)

    raise Exception(f"Falha no download após {MAX_TENTATIVAS} tentativas.")

# =============================================================================
# MAIN
# =============================================================================

def main_relatorio1(log, pasta_data_arquivo_bruto, nome_arquivo, token_air):

    #======================Configurações globais para a função======================
    global  LOG, PASTA_DATA_ARQUIVO_BRUTO, TOKEN_AIR, FILENAME_PRAZO_REPAROS
    PASTA_DATA_ARQUIVO_BRUTO = pasta_data_arquivo_bruto
    TOKEN_AIR = token_air
    FILENAME_PRAZO_REPAROS = nome_arquivo
    LOG = log
    atualizar_periodo_datas()
    definir_API(TOKEN_AIR)

	#========================MENSAGEM DE INICIO DE DOWNLOAD=========================
    inicio = datetime.now()
    LOG.info("=" * 60)
    LOG.info(f"DOWNLOAD_RELATORIO_AIR — Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    LOG.info("=" * 60)

    #=============================PROCESSO DE DOWNLOAD==============================
    try:
        print("")
        LOG.info("=" * 60)
        LOG.info("ETAPA 1/1 — Baixando relatório da API...")
        caminho_bruto = baixar_prazo_de_reparos()
        LOG.info("ETAPA 1/1 — Concluída.")
        LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 1/1 — FALHA: {e}")
        return False
    
    print("")
	#=======================MENSAGEM DE CONCLUSÃO DE DOWNLOAD=======================
    fim     = datetime.now()
    duracao = (fim - inicio).seconds
    LOG.info("=" * 60)
    LOG.info(f"CONCLUÍDO — {fim.strftime('%Y-%m-%d %H:%M:%S')} | Duração: {duracao // 60}m {duracao % 60}s")
    LOG.info("=" * 60 + "\n")


