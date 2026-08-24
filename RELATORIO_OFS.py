#======================================================
# Imports
#======================================================

from datetime import datetime
from io import BytesIO
import pandas as pd
from pandas.errors import EmptyDataError
import requests
import random
import string
import time
import json
import os

# =============================================================================
# CONFIGURAÇÕES — Altere APENAS este bloco quando precisar mudar informações básicas.
# (Altere com Cautela)
# =============================================================================
URL	 				= "<REMOVIDO POR SEGURANÇA>"  # URL do endpoint de download 
FILENAME_PADRAO 	= f"Relatório_OFS.xlsx"
MAX_TENTATIVAS 		= 5
UNIDADE_ID 			= "<REMOVIDO POR SEGURANÇA>"
TIMEOUT				= 60
DATA 				= datetime.now().strftime("%Y-%m-%d")
DATA_END    		= str(int(datetime.now().timestamp() * 1000))


#======================================================
# Parâmetros fixos para o endpoint de download
#======================================================

ENDPOINT_PARAMS = {
	"m": "gridexport",
	"a": "download",
	"itype": "manage",
}

HEADERS = {
	"accept": "*/*",
	"accept-language": "pt-BR,pt;q=0.9,en;q=0.8",
	"origin": URL.rstrip("/"),
	"referer": URL,
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
	"x-ofs-csrf-secure": "<REMOVIDO POR SEGURANÇA>",
}
def autualizar_datas():
	global DATA, DATA_END
	DATA = datetime.now().strftime("%Y-%m-%d")
	DATA_END = str(int(datetime.now().timestamp() * 1000))
#======================================================
# Gerar downloadId automático
#======================================================

def para_base36(valor):
	#Converte um número inteiro para uma string em base 36 (0-9, a-z)
	alfabeto = string.digits + string.ascii_lowercase
	if valor == 0:
		return "0"
	resultado = []
	while valor > 0:
		valor, resto = divmod(valor, 36)
		resultado.append(alfabeto[resto])
	return ''.join(reversed(resultado))

def gerar_download_id():
	#Gera downloadId automático igual ao JavaScript frontend
	#Fórmula: Date.now().toString(36) + Math.random().toString(36).substr(2)
	
	#=================== Timestamp em base 36============================
	timestamp_ms = int(time.time() * 1000)
	timestamp_base36 = para_base36(timestamp_ms)
	
	#================Parte aleatória em base 36==========================
	random_part = para_base36(random.getrandbits(64)).rjust(13, '0')
	
	download_id = timestamp_base36 + random_part
	return download_id

#======================================================
# Carregar cookies para poder fazer login 
#======================================================

def carregar_cookies():
    LOG.info("Carregando cookies do arquivo")
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r", encoding="utf-8") as arquivo:
            cookies = json.load(arquivo)
        # Verifica se existem cookies válidos
        if cookies:
            # Caso o arquivo contenha um dicionário
            if isinstance(cookies, dict):
                return cookies
            # Caso contenha uma lista de cookies
            if isinstance(cookies, list):
                return cookies
       
    # =========================================================
    # Se chegou aqui, precisa fazer login novamente
    # =========================================================

    LOG.info("Cookies não encontrados ou inválidos. Fazendo login automático.")
    LOG.info("ETAPA 1/3 FALHA - COOKIES NÃO ENCONTRADOS OU INVÁLIDOS. FAZENDO LOGIN AUTOMÁTICO.")
    LOG.info("=" * 60)
    print("")

    return criar_cookies()
	
def criar_cookies():
	#=========================Imports=========================
	from LOGIN_AUTOMATICO import FazerLoginOracle
	#=========================Faz login automático=========================
	FazerLoginOracle(
		pasta_edge=PASTA_EDGE_PROFILE,
		email=EMAIL,
		password_oracle=ORACLE_PASSWORD,
		password=MICROSOFT_PASSWORD,
		log=LOG,
		cookie_file=COOKIES_FILE,
	)
	#===Após o login, tentar carregar os cookies novamente====
	return carregar_cookies()

#======================================================
# Criar sessão autenticada e parametros para download
#======================================================	

def criar_sessao(cookies):
	session = requests.Session()
	session.headers.update(HEADERS)
	session.cookies.update(cookies)
	return session

def criar_parametros(unidade_id=UNIDADE_ID):
	download_id = gerar_download_id()
	LOG.info(f"Download_Id gerado: {download_id}")

	#=================Endpoint de download=================
	return {
		**ENDPOINT_PARAMS,
		"providerId": str(unidade_id),
		"date": DATA,
		"panel": "top",
		"view": "time",
		"downloadId" : download_id,
		"dates": DATA,
		"recursively": "1",
		"_": DATA_END,
	}

#======================================================
# Função principal para baixar o CSV
#======================================================

def baixar_csv(unidade_id, pasta_saida=".", tentativas=5):
	#========================Carregar cookies=========================
	LOG.info("="*60)
	LOG.info("ETAPA 1/3 - CARREGANDO COOKIES")
	cookies = carregar_cookies()
	LOG.info("ETAPA 1/3 CONCLUÍDA - COOKIES CARREGADOS")
	LOG.info("="*60)
	print()

	for tentativa in range(1, tentativas + 1):
		try:
			#===================Base requisição de download====================
			LOG.info("="*60)
			LOG.info(f"ETAPA 2/3 - TENTANDO DOWNLOAD (Tentativa {tentativa}/{tentativas})")
			session = criar_sessao(cookies)
			parametros  = criar_parametros(unidade_id)
			

			#========================Enviar requisição=========================
			response = session.get(URL, params=parametros, timeout=TIMEOUT)

			#========================Verificar resposta========================
			if response.status_code == 200:
				LOG.info("ETAPA 2/3 CONCLUÍDA - DOWNLOAD REALIZADO COM SUCESSO")
				LOG.info("="*60)
				print()
				conteudo = response.content or b""

				if not conteudo.strip():
					LOG.warning("Resposta do OFS veio vazia. Tentando novamente...")
					if tentativa < tentativas:
						cookies = criar_cookies()
						continue
					LOG.error("Falha: OFS retornou arquivo vazio em todas as tentativas.")
					return False

				amostra = conteudo[:300].lower()
				if b"<html" in amostra or b"<!doctype" in amostra:
					LOG.warning("OFS retornou HTML em vez de CSV (sessão pode ter expirado).")
					if tentativa < tentativas:
						cookies = criar_cookies()
						continue
					LOG.error("Falha: OFS não retornou CSV válido após várias tentativas.")
					return False
				
				#========================Extrair nome do arquivo e salva como XLSX========================
				LOG.info("="*60)
				LOG.info("ETAPA 3/3 - PROCESSANDO E SALVANDO ARQUIVO")
				os.makedirs(pasta_saida, exist_ok=True)
				try:
					df = pd.read_csv(BytesIO(conteudo), encoding="utf-8")
				except EmptyDataError:
					LOG.warning("CSV veio sem colunas. Tentando novamente...")
					if tentativa < tentativas:
						cookies = criar_cookies()
						continue
					LOG.error("Falha: CSV do OFS sem colunas em todas as tentativas.")
					return False
				caminho_saida = os.path.join(pasta_saida, FILENAME_PADRAO)
				df.to_excel(caminho_saida, index=False, engine='openpyxl')
				LOG.info(f"Arquivo salvo: {FILENAME_PADRAO}")
				LOG.info("ETAPA 3/3 CONCLUÍDA - ARQUIVO PROCESSADO E SALVO")
				LOG.info("="*60)
				print()
				return caminho_saida

			#=====================Tratar erros de autenticação=================
			elif response.status_code in (401, 403):
				LOG.warning(f"Sessão inválida/expirada (HTTP {response.status_code})")
				if tentativa < tentativas:
					LOG.info("Renovando sessão com login automático.")
					cookies = criar_cookies()
					continue
				else:
					LOG.error("Não foi possível autenticar após várias tentativas.")
					return False

			#======================Tratar outros erros HTTP====================
			else:
				if tentativa < tentativas:
					LOG.warning(f"Falha no download (HTTP {response.status_code}), tentando novamente...")
					time.sleep(random.uniform(1, 10))  # Pequena pausa antes de tentar novamente
					continue
				else:
					LOG.error(f"Falha no download após {tentativas} tentativas (HTTP {response.status_code}).")
					return False

		except requests.exceptions.RequestException as e:
			LOG.error(f"Erro na tentativa {tentativa}: {e}")
			if tentativa == tentativas:
				return False

	return False

#======================================================
# MAIN
#======================================================
def main_OFS(log, cookies_file, pasta_edge_profile, pasta_data_arquivo_bruto, nome_arquivo, microsoft_password, oracle_password, email):

	global  LOG, COOKIES_FILE, PASTA_EDGE_PROFILE, PASTA_DATA_ARQUIVO_BRUTO, EMAIL, ORACLE_PASSWORD, MICROSOFT_PASSWORD, FILENAME_PADRAO
	PASTA_DATA_ARQUIVO_BRUTO = pasta_data_arquivo_bruto
	FILENAME_PADRAO = nome_arquivo
	PASTA_EDGE_PROFILE = pasta_edge_profile
	MICROSOFT_PASSWORD = microsoft_password
	ORACLE_PASSWORD = oracle_password
	COOKIES_FILE = cookies_file
	EMAIL = email
	LOG = log

	#===================VERFICIAR SE EXISTE O ARQUIVO DE COOKIES===================
	if not os.path.exists(COOKIES_FILE):
		with open(COOKIES_FILE, "w", encoding="utf-8") as arquivo:
			json.dump([], arquivo)

	#========================Atualizar datas para o endpoint========================
	autualizar_datas()

	#========================MENSAGEM DE INICIO DE DOWNLOAD=========================
	inicio = datetime.now()
	LOG.info("=" * 60)
	LOG.info(f"DOWNLOAD_RELATORIO_OFS — Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
	LOG.info("=" * 60)
	print("")

	#=============================PROCESSO DE DOWNLOAD==============================
	baixar_csv(UNIDADE_ID, PASTA_DATA_ARQUIVO_BRUTO,MAX_TENTATIVAS,)

	#=======================MENSAGEM DE CONCLUSÃO DE DOWNLOAD=======================
	fim     = datetime.now()
	duracao = (fim - inicio).seconds
	LOG.info("=" * 60)
	LOG.info(f"CONCLUÍDO — {fim.strftime('%Y-%m-%d %H:%M:%S')} | Duração: {duracao // 60}m {duracao % 60}s")
	LOG.info("=" * 60 + "\n")