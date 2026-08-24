#===================================
#  Imports
#===================================
import logging
import os
from datetime import date

MESES = ["01-Janeiro", "02-Fevereiro", "03-Março", "04-Abril","05-Maio", "06-Junho", "07-Julho", "08-Agosto","09-Setembro", "10-Outubro", "11-Novembro", "12-Dezembro"]
#=====================================================================================
def configurar_logger(PASTA_LOGS, NOME_ARQUIVO) -> logging.Logger:
    #==== Verifica se a pasta de logs existe, caso contrário cria===========
    pasta_logs = os.path.join(PASTA_LOGS, NOME_ARQUIVO, MESES[date.today().month - 1])
    
    os.makedirs(pasta_logs, exist_ok=True)

    #==== Define o caminho do arquivo de log ===========
    arquivo_log = os.path.join(pasta_logs, f"{date.today().strftime('%d-%m-%Y')}-{NOME_ARQUIVO}.log")

    #==== Define o formato do log ===========
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)-7s] %(message)s", datefmt="%H:%M:%S")

    #==== Cria o logger ===========
    logger = logging.getLogger(f"{NOME_ARQUIVO}_logger")
    logger.setLevel(logging.DEBUG)

    #==== Remove handlers existentes ===========
    while logger.handlers:
        handler = logger.handlers.pop()
        handler.close()

    #==== Cria o FileHandler ===========
    fh = logging.FileHandler(arquivo_log, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    #==== Cria o StreamHandler ===========
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    #==== Adiciona os handlers ao logger ===========
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger