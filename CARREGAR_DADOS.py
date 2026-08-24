def carregar_dados(log, pasta_data_arquivo_bruto: str, pasta_data_arquivo_tratado: str, unidade: list, mapas_cluster: dict, nome_arquivo: str, nome_arquivo_air: str, nome_arquivo_ofs: str) -> dict:    
    #======Configurações globais para a função======
    global LOG, PASTA_DATA_ARQUIVO_BRUTO, PASTA_DATA_ARQUIVO_TRATADO, UNIDADES, MAPAS_CLUSTER
    PASTA_DATA_ARQUIVO_TRATADO = pasta_data_arquivo_tratado
    PASTA_DATA_ARQUIVO_BRUTO = pasta_data_arquivo_bruto
    UNIDADES = [str(u).strip().lower() for u in unidade]
    MAPAS_CLUSTER = {unidade: cluster for cluster, unidades in mapas_cluster.items() for unidade in unidades}
    LOG = log

    #=============================================================================
    #IMPORTS E CONFIGURAÇÕES GLOBAIS (NÃO ALTERE)
    #=============================================================================
    from datetime import datetime
    import pandas as pd
    import unicodedata
    import numpy as np
    import warnings
    import re
    import os

    #=============================================================================
    #FUNÇÃO DE LIMPEZA DE DADOS (NÃO ALTERE)
    #=============================================================================
    def limpar(coluna):
        if pd.isna(coluna):
            return ""

        coluna = str(coluna)
        # Remove acentos, caracteres especiais e espaços, e converte para minúsculas
        coluna = (unicodedata.normalize("NFKD", coluna).encode("ascii", "ignore").decode("utf-8")
                  .strip().lower().replace(" ", "_"))
        coluna = re.sub(r"[^a-z0-9_]", "", coluna)

        return coluna

    def converter_data(valor):
        if pd.isna(valor):
            return pd.NaT

        if isinstance(valor, pd.Timestamp):
            return valor

        texto = str(valor).strip()
        if texto == "" or texto.lower() in {"nan", "none"}:
            return pd.NaT

        if re.fullmatch(r"\d+(?:\.0+)?", texto):
            parte_inteira = texto.split(".", 1)[0]

            if len(parte_inteira) <= 5:
                data_serial = pd.to_datetime(parte_inteira, unit="D", origin="1899-12-30", errors="coerce")
                if pd.notna(data_serial):
                    return data_serial

            if len(parte_inteira) == 6:
                for formato in ("%d%m%y", "%y%m%d"):
                    try:
                        return pd.to_datetime(parte_inteira, format=formato, errors="raise")
                    except Exception:
                        pass

            if len(parte_inteira) == 8:
                for formato in ("%d%m%Y", "%Y%m%d"):
                    try:
                        return pd.to_datetime(parte_inteira, format=formato, errors="raise")
                    except Exception:
                        pass

        return pd.to_datetime(texto, errors="coerce", dayfirst=True)

    #=============================================================================
    #MENSAGEM DE INÍCIO DE CARREGAMENTO (NÃO ALTERE)
    #=============================================================================

    inicio = datetime.now()
    print("")
    print("")
    LOG.info("=" * 60)
    LOG.info(f"TRATANDO DADOS — Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    LOG.info("=" * 60)
    
    #=============================================================================
    #CONFIGURAÇÕES
    #=============================================================================
    RELATORIO_IRR_IFI           = nome_arquivo
    RELATORIO_AIR               = nome_arquivo_air
    RELATORIO_OFS               = nome_arquivo_ofs
    CAMINHO_RELATORIO_IRR_IFI   = os.path.join(PASTA_DATA_ARQUIVO_TRATADO, RELATORIO_IRR_IFI)
    CAMINHO_RELATORIO_AIR       = os.path.join(PASTA_DATA_ARQUIVO_BRUTO, RELATORIO_AIR)
    CAMINHO_RELATORIO_OFS       = os.path.join(PASTA_DATA_ARQUIVO_BRUTO, RELATORIO_OFS)

    #=============================================================================
    #CARREGAR DADOS (NÃO ALTERE)
    #=============================================================================
    try:
        print("")
        LOG.info("=" * 60)
        LOG.info("ETAPA 1/6 - CARREGANDO DADOS")
        LOG.info(f"Carregando arquivo AIR")
        DADOS_AIR   = pd.read_excel(CAMINHO_RELATORIO_AIR,usecols=["CONTRATO", "FILA", "DATA_EVENTO","USUARIO_CONCLUSAO","STATUS_EVENTO"], dtype=str)
        LOG.info(f"Carregando arquivo OFS")
        DADOS_OFS   = pd.read_excel(CAMINHO_RELATORIO_OFS, dtype=str)
        LOG.info(f"Criando e carregando arquivo de saída")
        DADOS_SAIDA = pd.DataFrame()  # DataFrame vazio para armazenar os resultados finais
        LOG.info("ETAPA 1/6 - CONCLUÍDA.")
        LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 1/6 - FALHA: {e}")
        return False

    #=============================================================================
    #PADRONIZAR COLUNAS
    #=============================================================================
    
    try:
        print("")
        LOG.info("=" * 60)
        LOG.info("ETAPA 2/6 - PADRONIZANDO COLUNAS")

        LOG.info("Padronizando colunas do arquivo AIR")
        DADOS_AIR.columns = [limpar(coluna) for coluna in DADOS_AIR.columns]

        LOG.info("Padronizando colunas do arquivo OFS")
        DADOS_OFS.columns = [limpar(coluna) for coluna in DADOS_OFS.columns]

        LOG.info("ETAPA 2/6 - CONCLUÍDA.")
        LOG.info("=" * 60)
        
    except Exception as e:
        LOG.error(f"ETAPA 2/6 - FALHA: {e}")
        return False

    #=============================================================================
    #Conversão segura de dados (NÃO ALTERE)
    #=============================================================================
    print("")
    LOG.info("=" * 60)
    LOG.info("ETAPA 3/6 - CONVERSÂO DE DADOS")
    try:
        NAO_FAZER_COLUNAS = ["data", "data_evento"]

        LOG.info("Convertendo colunas do arquivo AIR")
        for col in DADOS_AIR.columns:
            if limpar(col) not in NAO_FAZER_COLUNAS:
                DADOS_AIR[col] = DADOS_AIR[col].astype(str).str.replace(".0", "", regex=False).str.strip().str.lower().apply(limpar)
        
        DADOS_AIR = DADOS_AIR[DADOS_AIR["status_evento"] == "finalizada_produtiva"]

        LOG.info("Convertendo colunas do arquivo OFS")

        for col in DADOS_OFS.columns:
            if limpar(col) not in NAO_FAZER_COLUNAS:
                DADOS_OFS[col] = DADOS_OFS[col].astype(str).str.replace(".0", "", regex=False).str.strip().str.lower().apply(limpar)

        LOG.info("ETAPA 3/6 - CONCLUÍDA.")
        LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 3/6 - FALHA: {e}")
        return False

    #=============================================================================
    #Variáveis globais (NÃO ALTERE)
    #=============================================================================

    DATA_OFS_DT     = DADOS_OFS["data"].map(converter_data)
    MAPAS_EVENTO    = dict(zip(DADOS_AIR["contrato"], DADOS_AIR["fila"]))
    MAPAS_DIA       = dict(zip(DADOS_AIR["contrato"], DADOS_AIR["data_evento"]))
    MAPAS_TEC       = dict(zip(DADOS_AIR["contrato"], DADOS_AIR["usuario_conclusao"]))
    MAPEADO         = DADOS_OFS["numero_do_contrato"].map(MAPAS_DIA).map(converter_data)
    MAPAS_ATV       = {
        "apoio": "outros",
        "ativacao": "ativacao",
        "checklist": "checklist",
        "clean_up_casa_cliente": "clean_up_casa_cliente",
        "consulta_medica": "outros",
        "manutencao_veicular": "outros",
        "materiais_devolucao": "outros",
        "mudanca_de_comodo": "mudanca_de_comodo",
        "mudanca_de_endereco": "mudanca_de_endereco",
        "reparo_corretivo": "reparo",
        "reparo_preventivo": "prevreparo",
        "reposicao_de_materiais": "reparo",
        "retirada_de_material": "outros",
        "retirada_voluntaria": "outros",
        "reuniao_de_equipe": "outros",
        "upgradedowngrade": "mudanca_de_pacote",
        "vistoria_interna": "outros"
    }
    MAPAS_STA       = {
        "cancelado": "Cancelado",
        "concluido": "Realizado",
        "em_rota": "Em aberto",
        "iniciado": "Em execução",
        "nao_concluido": "Não executado",
        "pendente": "Em aberto",
        "suspenso": "Cancelado"
    }

    #=============================================================================
    #Criação de colunas de saída (NÃO ALTERE)
    #=============================================================================
    try:
        print("")
        LOG.info("=" * 60)
        LOG.info("ETAPA 4/6 - CRIAÇÃO DE DATAFRAME DE IRR E INF")
        #========Colunas que foram criadas para fazer o relatorio de IRR e INF========
        LOG.info("Criando colunas do arquivo IRR_INF")
        DADOS_SAIDA["TIPO_ATIVIDADE"]           = (DADOS_OFS["tipo_de_atividade1"].map(MAPAS_ATV))
        DADOS_SAIDA["CLUSTER"]                  = (DADOS_OFS["unidade"].map(MAPAS_CLUSTER))

        DADOS_SAIDA["TIPO_ATV_ULTIMO_SERVIÇO"]  = np.where(DADOS_SAIDA["TIPO_ATIVIDADE"].fillna("").str.lower().isin(["reparo","ativacao"]), DADOS_OFS["numero_do_contrato"].map(MAPAS_EVENTO), None)
        
        
        DADOS_SAIDA["DIAS IRR_IFI"]             = np.where(DADOS_SAIDA["TIPO_ATV_ULTIMO_SERVIÇO"].fillna("").str.lower().isin(["reparo","ativacao"]),
                                                            (DATA_OFS_DT - MAPEADO).dt.days, None)
        
        
        DADOS_SAIDA["IRR_IFI"]                  = np.where(
            ((DADOS_SAIDA["DIAS IRR_IFI"].between(1, 15)) & (DADOS_SAIDA["TIPO_ATV_ULTIMO_SERVIÇO"] == "ativacao")),
            "IFI", np.where(
                ((DADOS_SAIDA["DIAS IRR_IFI"].between(1, 31)) & (DADOS_SAIDA["TIPO_ATV_ULTIMO_SERVIÇO"] == "reparo")), "IRR", None))
        
        
        DADOS_SAIDA["TEC_OFENSOR"]              = np.where(DADOS_SAIDA["TIPO_ATV_ULTIMO_SERVIÇO"].fillna("").str.lower().isin(["reparo","ativacao"]), DADOS_OFS["numero_do_contrato"].map(MAPAS_TEC), None)
        
        
        DADOS_SAIDA["NOVO_STATUS"]              = np.where(DADOS_SAIDA["TIPO_ATIVIDADE"].fillna("").str.lower().isin(["reparo","ativacao"]), DADOS_OFS["status_da_atividade"].map(MAPAS_STA), None)

        #====================Transforma em inteiro, tratando erros====================
        DADOS_SAIDA["DIAS IRR_IFI"]             = pd.to_numeric(DADOS_SAIDA["DIAS IRR_IFI"],errors="coerce").astype("Int64")

        #==========Junta os dois dataframes, alinhando pelas linhas (axis=1)==========
        LOG.info("Juntando dataframes de IRR_IFI e OFS")
        DADOS_SAIDA                             = pd.concat([DADOS_SAIDA, DADOS_OFS], axis=1)

        #====================Ignorar warnings de tipo FutureWarning===================
        warnings.filterwarnings("ignore",category=FutureWarning)
        
        #========================Transformação de Dados FINAL=========================
        LOG.info("Realizando padronização final dos dados")
        COLUNAS_TEXTO                           = DADOS_SAIDA.select_dtypes(include=["object", "string"]).columns
        DADOS_SAIDA[COLUNAS_TEXTO]              = (DADOS_SAIDA[COLUNAS_TEXTO].replace(["nan", "None"], np.nan).infer_objects(copy=False).fillna("-"))
        DADOS_SAIDA["DIAS IRR_IFI"]             = DADOS_SAIDA["DIAS IRR_IFI"].astype("string").fillna("-")
        LOG.info("ETAPA 4/6 - CONCLUÍDA.")
        LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 4/6 - FALHA: {e}")
        raise False
    
    #=============================================================================
    #Salvando dados tratado em uma planilha nova
    #=============================================================================
    try:
        if (datetime.now().strftime("%H") == "20"):
            print("")
            LOG.info("=" * 60)
            LOG.info("ETAPA 5/6 - SALVANDO DATAFRAME PARA CONSULTA RÁPIDA TRATADO")
            LOG.info(f"Salvando arquivo IRR_IFI")
            os.makedirs(os.path.dirname(CAMINHO_RELATORIO_IRR_IFI), exist_ok=True)
            DADOS_SAIDA.to_excel(CAMINHO_RELATORIO_IRR_IFI + f"_DIA-{datetime.now().strftime('%d')}-DO-MÊS.xlsx", index=False, engine='openpyxl')
            LOG.info(f"Arquivo Salvo: {CAMINHO_RELATORIO_IRR_IFI + f'_DIA-{datetime.now().strftime("%d")}-DO-MÊS.xlsx'}")
            LOG.info("ETAPA 5/6 - CONCLUÍDA.")
            LOG.info("=" * 60)

        else:
            print("")
            LOG.info("=" * 60)
            LOG.info("ETAPA 5/6 - SALVANDO DATAFRAME PARA CONSULTA RÁPIDA TRATADO")
            LOG.info(f"Salvando arquivo IRR_IFI")
            os.makedirs(os.path.dirname(CAMINHO_RELATORIO_IRR_IFI), exist_ok=True)
            DADOS_SAIDA.to_excel(CAMINHO_RELATORIO_IRR_IFI, index=False, engine='openpyxl')
            LOG.info(f"Arquivo Salvo:{RELATORIO_IRR_IFI}")
            LOG.info("ETAPA 5/6 - CONCLUÍDA.")
            LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 5/6 - FALHA: {e}")
        raise False
    
    #=============================================================================
    #Processo de criação do dicionário para criação do dashbord (NÃO ALTERE)
    #=============================================================================
    print("")
    LOG.info("=" * 60)
    LOG.info("ETAPA 6/6 - CRIANDO DICIONÁRIO PARA DASHBOARD")
    #=====================Criação dos dataframe e dicionarios=====================
    DADOS_CHAMADO, DADOS_QUANTIDADE, = pd.DataFrame(), pd.DataFrame()
    CHAMADO, QUANTIDADE = {}, {}

    DADOS_SAIDA1 = DADOS_SAIDA.copy()

    try:
        #=================Limpeza de dados para criação do dicionário=================
        COLUNAS = ["CLUSTER", "IRR_IFI"]
        for coluna in COLUNAS:
            DADOS_SAIDA1 = DADOS_SAIDA1[(DADOS_SAIDA1[coluna] != "-") & DADOS_SAIDA1[coluna].notnull()]
        
        #====================Criação das colunas para o dicionario====================
        DADOS_CHAMADO["CLUSTER"]                     = (DADOS_SAIDA1["CLUSTER"].fillna("-"))
        DADOS_CHAMADO["IRR_IFI"]                     = (DADOS_SAIDA1["IRR_IFI"].fillna("-"))
        DADOS_CHAMADO["UNIDADE"]                     = (DADOS_SAIDA1["unidade"].str.replace("_", " ").str.upper())
        DADOS_CHAMADO["CONTRATO"]                    = (DADOS_SAIDA1["numero_do_contrato"].fillna("-"))
        DADOS_CHAMADO["RECURSO"]                     = (DADOS_SAIDA1["recurso"].fillna("-")).str.replace("_", " ").str.title()
        DADOS_CHAMADO["TEC_OFENSOR"]                 = (DADOS_SAIDA1["TEC_OFENSOR"].fillna("-")).str.replace("_", " ").str.title()
        DADOS_CHAMADO["EM_ABERTO"]                   = (DADOS_SAIDA1["NOVO_STATUS"].map({"Em aberto": "Em aberto","Em execução": "Em execução"}).fillna("-"))
        
        DADOS_QUANTIDADE["CLUSTER"]                  = (DADOS_SAIDA1["CLUSTER"].fillna("-"))
        DADOS_QUANTIDADE["IRR_IFI"]                  = (DADOS_SAIDA1["IRR_IFI"].fillna("-")) 
        DADOS_QUANTIDADE["EM_ABERTO"]                = (DADOS_SAIDA1["NOVO_STATUS"].map({"Em aberto": 1,"Em execução": 1}).fillna(0).infer_objects().astype(int))
        DADOS_QUANTIDADE["REALIZADO"]                = (DADOS_SAIDA1["NOVO_STATUS"].map({"Realizado": 1,}).fillna(0).infer_objects().astype(int))
        DADOS_QUANTIDADE["NÃO_EXECUTADO"]            = (DADOS_SAIDA1["NOVO_STATUS"].map({"Cancelado":1,"Não executado":1}).fillna(0).infer_objects().astype(int))
        
        REALIZADO_TOTAL_CLUSTER                      = (DADOS_SAIDA[(DADOS_SAIDA["NOVO_STATUS"] == "Realizado") & (DADOS_SAIDA["TIPO_ATIVIDADE"] == "reparo")].groupby("CLUSTER").size().to_dict())
        LOG.info("Colunas criadas para os dicionários de chamado e quantidade")

        #=============Agrupamento para criação do dicionário de quantidade============
        agrupado_cluster = (
            DADOS_QUANTIDADE.groupby(["CLUSTER", "IRR_IFI"], dropna=False, as_index=False)
            [["EM_ABERTO","REALIZADO","NÃO_EXECUTADO"]].sum()
        )

        #=================Limpeza de dados para criação do dicionário=================
        for coluna in ["EM_ABERTO"]:
            DADOS_CHAMADO = DADOS_CHAMADO[(DADOS_CHAMADO[coluna] != "-") & DADOS_CHAMADO[coluna].notnull()]
        
        #======================Criação do dicionário de quantidade======================
        LOG.info("Criando dicionário de quantidade...")
        for indice_ignorar, coluna in agrupado_cluster.iterrows():
            cluster = coluna["CLUSTER"]
            irr_ifi = coluna["IRR_IFI"]

            if cluster not in QUANTIDADE:
                QUANTIDADE[cluster] = {
                    "IFI": {"EM_ABERTO": 0,"REALIZADO": 0,"NÃO_EXECUTADO": 0,"REALIZADO_TOTAL": 0},
                    "IRR": {"EM_ABERTO": 0,"REALIZADO": 0,"NÃO_EXECUTADO": 0,"REALIZADO_TOTAL": 0}
                }

            QUANTIDADE[cluster][irr_ifi] = {
                "EM_ABERTO": int(coluna["EM_ABERTO"]),
                "REALIZADO": int(coluna["REALIZADO"]),
                "NÃO_EXECUTADO": int(coluna["NÃO_EXECUTADO"]),
                "REALIZADO_TOTAL": int(REALIZADO_TOTAL_CLUSTER.get(cluster, 0))      
            }

        LOG.info("Dicionário de quantidade criado")
        #======================Criação do dicionário de chamados======================
        LOG.info("Criando dicionário de chamados...")
        for indice_ignorar, coluna in DADOS_CHAMADO.iterrows():
            cluster = coluna["CLUSTER"]
            irr_ifi = coluna["IRR_IFI"]

            if cluster not in CHAMADO:
                CHAMADO[cluster] = {"IFI": [],"IRR": []}

            CHAMADO[cluster][irr_ifi].append({
                "Tecnico Atribuido": coluna["RECURSO"],
                "Tecnico Ofensor": coluna["TEC_OFENSOR"],
                "Status": coluna["EM_ABERTO"],
                "Unidade": coluna["UNIDADE"],
                "Contrato": coluna["CONTRATO"],
                "Tipo": coluna["IRR_IFI"]
            })
        LOG.info("Dicionário de chamados criado")
        LOG.info("ETAPA 6/6 - CONCLUÍDA.")
        LOG.info("=" * 60)

    except Exception as e:
        LOG.error(f"ETAPA 6/6 - FALHA: {e}")
        LOG.info("=" * 60)
        raise False
            
    #=============================================================================
    #MENSAGEM DE CONCLUSÃO
    #=============================================================================
    fim     = datetime.now()
    duracao = (fim - inicio).seconds
    print("")
    LOG.info("=" * 60)
    LOG.info(f"CONCLUÍDO — {fim.strftime('%Y-%m-%d %H:%M:%S')} | Duração: {duracao // 60}m {duracao % 60}s")
    LOG.info("=" * 60 + "\n")

    #=============================================================================
    #RETORNO DOS DADOS TRATADOS
    #=============================================================================

    return {
        "dicionario_chamados": CHAMADO,
        "dicionario_quantidade": QUANTIDADE
    }

   