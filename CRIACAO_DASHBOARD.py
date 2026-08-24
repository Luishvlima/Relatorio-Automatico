# =============================================================================
# IMPORTS
# =============================================================================

from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import os

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================

RESOLUCAO_DPI = 600
matplotlib.use("Agg")

# =============================================================================
# CORES
# =============================================================================
FUNDO        = "#0a192f"
PAINEL       = "#162238"
BORDA        = "#1e3a5f"
AZUL_CLARO   = "#4069A1"
VERDE_MED    = "#3CB371"
VERDE_CLARO  = "#a5f3e0"
VERMELHO_MED = "#FF6347"
BRANCO       = "#FFFFFF"
CINZA_LIN    = "#cccccc"
VERMELHO     = "#FF0000"
AMARELO      = "#FFD700"

# =============================================================================
# HELPERS
# =============================================================================
def _caixa(ax, x, y, w, h, cor=PAINEL, borda=BORDA, espessura_linha=1):
    caixa = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="square,pad=0",
        linewidth = espessura_linha, edgecolor=borda, facecolor=cor,
        transform=ax.transAxes, clip_on=False, zorder=2,
    )
    ax.add_patch(caixa)

def _caixa_relativa(ax, px, py, pw, ph, rx, ry, rw, rh, cor=PAINEL, borda=BORDA, espessura_linha=1):
    x = px + (rx * pw)
    y = py + (ry * ph)
    w = rw * pw
    h = rh * ph
    _caixa(ax, x, y, w, h, cor=cor, borda=borda, espessura_linha=espessura_linha)

def _Texto(ax, x, y, texto, cor=PAINEL, tamanho=12, peso="normal",
           alinhamento_horizontal="center", alinhamento_vertical="center",
           fonte="Segoe UI Emoji"):
    ax.text(x, y, texto, color=cor, fontsize=tamanho, fontweight=peso,
            ha=alinhamento_horizontal, va=alinhamento_vertical,
            zorder=5, fontfamily=fonte)

def _Texto_Relativo(ax, px, py, pw, ph, rx, ry, texto, tamanho=12,
                    cor=PAINEL, peso="normal", alinhamento_horizontal="center",
                    alinhamento_vertical="center", fonte="Segoe UI Emoji"):
    x = px + (rx * pw)
    y = py + (ry * ph)
    _Texto(ax, x, y, texto, cor=cor, tamanho=tamanho, peso=peso,
           alinhamento_horizontal=alinhamento_horizontal,
           alinhamento_vertical=alinhamento_vertical, fonte=fonte)

def _Plot_relativo(ax, px, py, pw, ph, xs:list, ys:list, color=BORDA, linewidth=1, zorder=4):
    ys_global = [py + (y * ph) for y in ys]
    xs_global = [px + (x * pw) for x in xs]
    ax.plot(xs_global, ys_global, color=color, linewidth=linewidth, zorder=zorder)

Chamado = {
    "Tipo": 0.04,
    "Tecnico Atribuido": 0.385,
    "Tecnico Ofensor": 0.73,
    "Status": 0.83,
    "Unidade": 0.91,
    "Contrato": 1
}

Chamadolocal = {
    "Tipo": 0.04/2,
    "Tecnico Atribuido": 0.04+0.345/2,
    "Tecnico Ofensor": 0.385+0.345/2,
    "Status": 0.73+0.10/2,
    "Unidade": 0.83+0.08/2,
    "Contrato": 0.91+0.09/2
}

Dicionario_CHAVE = [
    "Tecnico Atribuido",
    "Tecnico Ofensor",
    "Status",
    "Unidade",
    "Contrato",
    "Tipo"
]

# =============================================================================
# Card unidade por cluster
# =============================================================================

def _Dashboard_Cluster_Titulo(ax):
    hora = pd.Timestamp.now().strftime("%H:%M")
    _Texto(ax, 0.02, 0.5, f"🔁RELATORIO DE IRR-INF | {hora}", cor=VERDE_CLARO, tamanho=14,
           peso="bold", alinhamento_horizontal="left")

def _Dashboard_Cluster_Linha(ax, cluster, dados_cluster):
    #==================================ESTRUTURA===================================
    _caixa(ax, 0.00, 0.00, 1.0, 1.0, cor="none", borda=BORDA)
    # _caixa(ax, 0.02, 0.02, 0.96, 0.96, cor="none", borda=BORDA, espessura_linha=1)

    texto = cluster.replace("Cluster_", "Cluster\n").replace("CLUSTER_", "Cluster\n").replace("-", " ").title()
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=12, peso="bold", alinhamento_horizontal="center",
                    rx=0.09, ry=0.5, texto=f"{texto}")
        
    # Quantidade EM ABERTO
    _Plot_relativo(ax, 0.0, 0.0, 1.0, 1.0,
                   [0.2,0.2], [1,0], color=BORDA, linewidth=1)
    _caixa_relativa(ax, 0.0, 0.0, 1.0, 1.0, cor=PAINEL, borda=AMARELO, espessura_linha=0.5,
                    rx=0.21, ry=0.2, rw=0.18, rh=0.4)
        
    # Quantidade REALIZADO
    _Plot_relativo(ax, 0.0, 0.0, 1.0, 1.0,
                   [0.4,0.4], [1,0], color=BORDA, linewidth=1)
    _caixa_relativa(ax, 0.0, 0.0, 1.0, 1.0, cor=PAINEL, borda=VERMELHO, espessura_linha=0.5,
                    rx=0.41, ry=0.2, rw=0.18, rh=0.4)
        
    #Quantidade NÃO EXECUTADO
    _Plot_relativo(ax, 0.0, 0.0, 1.0, 1.0,
                   [0.6,0.6], [1,0], color=BORDA, linewidth=1)
    _caixa_relativa(ax, 0.0, 0.0, 1.0, 1.0, cor=PAINEL, borda=VERDE_MED, espessura_linha=0.5,
                    rx=0.61, ry=0.2, rw=0.18, rh=0.4)
        
    #Total EXECUTADO
    _Plot_relativo(ax, 0.0, 0.0, 1.0, 1.0,
                   [0.8,0.8], [1,0], color=BORDA, linewidth=1)
    _caixa_relativa(ax, 0.0, 0.0, 1.0, 1.0, cor=PAINEL, borda=VERDE_CLARO, espessura_linha=0.5,
                    rx=0.81, ry=0.2, rw=0.18, rh=0.5)
        
    #=========================================================================
    # Quantidades
    #=========================================================================
    total_realizado_irr_ifi = dados_cluster['IRR']['REALIZADO'] + dados_cluster['IFI']['REALIZADO']
    total_realizado = dados_cluster['IRR']['REALIZADO_TOTAL']  # é igual para IRR e IFI

    # Quantidade EM ABERTO
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=AMARELO, tamanho=10, peso="bold", alinhamento_horizontal="center",
                    rx=0.3, ry=0.7, texto=f"EM ABERTO")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=AMARELO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.255, ry=0.4, texto=f"IRR\n{dados_cluster['IRR']['EM_ABERTO']}")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=AMARELO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.345, ry=0.4, texto=f"IFI\n{dados_cluster['IFI']['EM_ABERTO']}")

    # Quantidade REALIZADO
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERMELHO, tamanho=10, peso="bold", alinhamento_horizontal="center",
                    rx=0.5, ry=0.7, texto=f"REALIZADO")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERMELHO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.455, ry=0.4, texto=f"IRR\n{dados_cluster['IRR']['REALIZADO']}")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERMELHO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.545, ry=0.4, texto=f"IFI\n{dados_cluster['IFI']['REALIZADO']}")

    # Quantidade NAO EXECUTADO
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_MED, tamanho=10, peso="bold", alinhamento_horizontal="center",
                    rx=0.7, ry=0.7, texto=f"NAO EXECUTADO")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_MED, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.655, ry=0.4, texto=f"IRR\n{dados_cluster['IRR']['NÃO_EXECUTADO']}")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_MED, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.745, ry=0.4, texto=f"IFI\n{dados_cluster['IFI']['NÃO_EXECUTADO']}")

    # Quantidade TOTAL EXECUTADO
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=10, peso="bold", alinhamento_horizontal="center",
                    rx=0.9, ry=0.8, texto=f"TOTAL REALIZADO")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.855, ry=0.6, texto=f"IRR-INF:")
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.955, ry=0.6, texto=f"{total_realizado_irr_ifi}")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.855, ry=0.45, texto=f"Total:")
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.955, ry=0.45, texto=f"{total_realizado}")

    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.855, ry=0.3, texto=f"Total %:")
    _Texto_Relativo(ax, 0.0, 0.0, 1.0, 1.0, cor=VERDE_CLARO, tamanho=8, peso="bold", alinhamento_horizontal="center",
                    rx=0.955, ry=0.3, texto=f"{round(((total_realizado_irr_ifi)/(total_realizado)*100),2)}%" if total_realizado > 0 else "0%")

def _Dashboard_Cluster(axes, dicionario_quantidade):
    _Dashboard_Cluster_Titulo(axes[0])

    for ax_cluster, (cluster, dados_cluster) in zip(axes[1:], dicionario_quantidade.items()):
        _Dashboard_Cluster_Linha(ax_cluster, cluster, dados_cluster)
            
def _Dashboard_Chamado(ax, chamados_pagina, cluster):
    agora = pd.Timestamp.now().strftime("%H:%M")
    _Texto(ax, 0.5, 0.92, f"🔁RELATORIO DE IRR-INF | CHAMADOS\n{cluster.replace('_', ' ')} | {agora}", cor=VERDE_CLARO, tamanho=14),
    _caixa(ax, 0, 0, 1, 0.8, cor="none", borda=BORDA)

    linhas = (1/11)  # 10 linhas + 1 para o título
    y = 1-linhas/2

    for i, chave in enumerate(Dicionario_CHAVE):
        _Texto_Relativo(ax, 0, 0, 1, 0.8,
                        rx=Chamadolocal.get(chave, "N/A"), ry=y, texto=chave.upper(), tamanho=10, cor=VERDE_CLARO, alinhamento_horizontal="center", peso="bold")
        _Plot_relativo(ax, 0, 0, 1, 0.8, xs=[Chamado.get(chave, "N/A"), Chamado.get(chave, "N/A")], ys=[1, 0], color=BORDA, linewidth=1)

    for i, chamado in enumerate(chamados_pagina):
        y = y - linhas
        _Plot_relativo(ax, 0, 0, 1, 0.8, xs=[0, 1], ys=[y+linhas/2, y+linhas/2], linewidth=1)
        for chave, valor in chamado.items():
            _Texto_Relativo(ax, 0, 0, 1, 0.8,
                            rx=Chamadolocal.get(chave, "N/A"), ry=y, texto=valor, tamanho=10, cor=VERDE_CLARO, alinhamento_horizontal="center")
    _Plot_relativo(ax, 0, 0, 1, 0.8, xs=[0, 1], ys=[y-linhas/2, y-linhas/2], linewidth=1)
            
# =============================================================================
# MAIN
# =============================================================================

def criacao_dashboard(log, PASTA_DATA_IMAGENS_TRATADO, dicionarios):
    try:
        global LOG
        LOG = log
        print("")
        LOG.info("=" * 60)
        LOG.info("ETAPA 1/2 - CRIAÇÂO DO DASHBOARD")
        LOG.info("Iniciando criação do dashboard...")
        
        #=========================CRIAÇÂO DAS VARIAVEIS========================
        LINKS, total_aberto, todos_chamados, quantidade_chamados_pagina = [], {},{}, 10
        dicionario_quantidade,dicionario_chamados = dicionarios["dicionario_quantidade"], dicionarios["dicionario_chamados"]
        quantidade_clusters = len(dicionario_quantidade)
        for cluster, tipos in dicionario_chamados.items():

            todos = tipos.get("IFI", []) + tipos.get("IRR", [])

            todos_chamados[cluster] = [
                chamado
                for chamado in todos
                if chamado["Status"] in ["Em aberto", "Em execução"]
            ]
        
        print(quantidade_clusters, "clusters encontrados.")
        #====================DEFINIÇÃO DO CAMINHO DA IMAGEM====================
        caminho_imagem_cluster  = os.path.join(PASTA_DATA_IMAGENS_TRATADO, f"DASHBOARD_IRR-ING_CLUSTERS.jpeg")
        

        #======================CRIAÇÃO DO CARD DO CLUSTER======================
        fig, axes = plt.subplots(
            nrows=quantidade_clusters + 1,
            ncols=1,
            figsize=(8, max(3, quantidade_clusters + 1)),
            gridspec_kw={"height_ratios": [0.45] + [1] * quantidade_clusters},
            facecolor=FUNDO
        )

        for ax in axes:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            ax.set_facecolor(FUNDO)

        fig.subplots_adjust(hspace=0.02)
        
        #=============CHAMADA DA FUNÇÃO DE CRIAÇÃO DO CARD_CLUSTER=============
        _Dashboard_Cluster(axes, dicionario_quantidade)
        
        #=================SALVAMENTO DA IMAGEM DO CARD_CLUSTER=================
        fig.savefig(caminho_imagem_cluster,format="jpeg",dpi=RESOLUCAO_DPI,facecolor=FUNDO,bbox_inches="tight",)
        plt.close(fig)
        LOG.info(f"DASHBOARD_IRR-ING_CLUSTERS.jpeg salvo. ")
        LINKS.append(caminho_imagem_cluster)

        #==========================CRIAÇÃO DE CHAMADOS==========================
        for cluster, dados_cluster in todos_chamados.items():

            #======================CALCULO DO TOTAL DE CHAMADOS=====================
            total_aberto[cluster] = len(dados_cluster)
            # print(total_aberto[cluster], todos_chamados[cluster])
            quantidade_de_paginas = ((total_aberto[cluster]-1)//quantidade_chamados_pagina) + 1

            #=======================INICIO DO LOOP DE PÁGINAS=======================
            for i in range(quantidade_de_paginas):

                #===================DEFINIÇÃO DO CHAMADOS POR PÁGINA===================
                inicio = i * quantidade_chamados_pagina
                fim = inicio + quantidade_chamados_pagina
                chamados_pagina = dados_cluster[inicio:fim]

                #====================DEFINIÇÃO DO CAMINHO DA IMAGEM====================
                caminho_imagem_chamados = os.path.join(PASTA_DATA_IMAGENS_TRATADO, 
                    f"DASHBOARD_CHAMADOS_{cluster}_PAG.{i+1}.jpeg")
                
                #======================CRIAÇÃO DO CARD DO CLUSTER======================
                fig, ax = plt.subplots(figsize=(12, 4), facecolor=FUNDO)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis("off")
                ax.set_facecolor(FUNDO)

                #=============CHAMADA DA FUNÇÃO DE CRIAÇÃO DO CARD_CLUSTER=============
                _Dashboard_Chamado(ax, chamados_pagina,cluster)

                #=================SALVAMENTO DA IMAGEM DO CARD_CLUSTER=================
                fig.savefig(caminho_imagem_chamados,format="jpeg",dpi=RESOLUCAO_DPI,facecolor=FUNDO,bbox_inches="tight",)
                plt.close(fig)
                LOG.info(f"DASHBOARD_CHAMADOS_{cluster}_PAG.{i+1}.jpeg salvo. ")
                LINKS.append(caminho_imagem_chamados)

        LOG.info("ETAPA 1/2 - CONCLUÍDA. TODOS OS DASHBOARDS FORAM CRIADOS E SALVOS COM SUCESSO.")
        LOG.info("=" * 60)
        return LINKS
    
    except Exception as e:

        LOG.error(f"ETAPA 1/2 - FALHA: {e}")
        raise False

    