# =============================================================================
# IMPORTS
# =============================================================================
import os
import sys
import subprocess
import time
import ctypes
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Sequence

# =============================================================================
# SETUP — EXCLUSÃO NO WINDOWS DEFENDER
# =============================================================================

#====Constantes de configuração do setup============
@dataclass
class DefenderSetup:
    log: object
    base_dir: str
    script_path: str
    pastas: list
    processo: str
    arquivo_flag: str
    arquivo_status: str


def _logger_padrao():
    logger = logging.getLogger("EXCLUSAO_DEFENDER")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def criar_configuracao_defender(
    log=None,
    base_dir: Optional[str] = None,
    script_path: Optional[str] = None,
    pastas: Optional[Sequence[str]] = None,
    processo: Optional[str] = None,
    arquivo_flag: str = "",
    arquivo_status: str = "",
) -> DefenderSetup:
    logger = log or _logger_padrao()
    diretorio_base = base_dir or os.getcwd()
    caminho_script = script_path or os.path.abspath(sys.argv[0])
    lista_pastas = list(pastas or [])
    processo_execucao = processo or sys.executable

    return DefenderSetup(
        log=logger,
        base_dir=diretorio_base,
        script_path=caminho_script,
        pastas=lista_pastas,
        processo=processo_execucao,
        arquivo_flag=arquivo_flag,
        arquivo_status=arquivo_status,
    )

#====Função para configurar exclusões no Windows Defender============
def configurar_exclusoes_defender(cfg: DefenderSetup) -> bool:

    cfg.log.info("=" * 60)
    cfg.log.info("SETUP — Configurando exclusões no Windows Defender...")
    cfg.log.info("=" * 60)

    pastas   = cfg.pastas
    processo = cfg.processo
    sucesso  = True

    for pasta in pastas:
        try:
            #====Executa a exclusão da pasta no Windows Defender usando PowerShell============
            r = subprocess.run(
                ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{pasta}'"],
                capture_output=True, text=True
            )

            #====Verifica o resultado da execução(0=sucesso)============
            if r.returncode == 0:
                cfg.log.info(f"Pasta excluída: {pasta}")
            else:
                cfg.log.warning(f"Falha: {pasta} — {r.stderr.strip()}")
                sucesso = False
        except Exception as e:
            cfg.log.error(f"Erro: {e}")
            sucesso = False
    
    #====Executa a exclusão do processo(Programa) no Windows Defender usando PowerShell============
    try:
        #====Executa a exclusão do processo(Programa) no Windows Defender usando PowerShell============
        r = subprocess.run(
            ["powershell", "-Command", f"Add-MpPreference -ExclusionProcess '{processo}'"],
            capture_output=True, text=True
        )
        #====Verifica o resultado da execução(0=sucesso)============
        if r.returncode == 0:
            cfg.log.info(f"Processo excluído: {processo}")
        else:
            cfg.log.warning(f"Falha no processo — {r.stderr.strip()}")
            sucesso = False
    except Exception as e:
        cfg.log.error(f"Erro: {e}")
        sucesso = False

    #====Finaliza o setup e informa o usuário============
    cfg.log.info("=" * 60)
    if sucesso:
        cfg.log.info("SETUP CONCLUÍDO! O Defender não irá mais interferir.")
        cfg.log.info("Execute backlog.exe normalmente nas próximas vezes.")
    else:
        cfg.log.warning("SETUP com erros. Tente: clique direito → Executar como administrador")
    cfg.log.info("=" * 60)

    return sucesso

#====Função para verificar se o usuário tem privilégios de administrador============
def _tem_privilegio_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

#====Função para executar o setup elevado (UAC)============
def _executar_setup_elevado(cfg: DefenderSetup) -> bool:

    if os.name != "nt":
        return False

    try:
        cfg.log.info("Solicitando elevação de privilégio (UAC) para configurar o Defender...")

        if os.path.exists(cfg.arquivo_status):
            os.remove(cfg.arquivo_status)

        #====Verifica o caminho do executável ou do arquivo e os parâmetros para a execução elevada============
        if getattr(sys, 'frozen', False):
            executavel = sys.executable
            parametros = "--setup --setup-origem-auto"
        else:
            executavel = sys.executable
            parametros = f'"{cfg.script_path}" --setup --setup-origem-auto'

        #====Solicita a execução elevada (UAC) do script ou executável============
        retorno = ctypes.windll.shell32.ShellExecuteW(None, "runas", executavel, parametros, cfg.base_dir, 1)
        if int(retorno) <= 32:
            cfg.log.warning("Não foi possível solicitar elevação UAC (cancelado ou bloqueado pelo sistema).")
            return False

        #====Aguarda a conclusão do setup elevado, verificando a criação do arquivo de flag ou status============
        prazo_limite = time.time() + 120
        while time.time() < prazo_limite:
            #====Verifica se o arquivo de flag foi criado============
            if os.path.exists(cfg.arquivo_flag):
                cfg.log.info("Setup elevado concluído com sucesso.")
                return True
            
            #====Verifica se o arquivo de status foi criado e lê o conteúdo para determinar sucesso ou falha============
            if os.path.exists(cfg.arquivo_status):
                with open(cfg.arquivo_status, "r", encoding="utf-8") as f:
                    status = f.read().strip().upper()
                
                #====Se o status for OK, o setup foi concluído com sucesso else, retorna falha ============
                if status == "OK":
                    cfg.log.info("Setup elevado concluído com sucesso.")
                    return True
                else:
                    cfg.log.warning("Setup elevado retornou falha. Verifique o LOG para detalhes de permissões.")
                    return False
            #====Aguarda 1 segundo antes de verificar novamente============    
            time.sleep(1)

        cfg.log.warning("Tempo excedido aguardando conclusão do setup elevado. Tentaremos novamente na próxima execução.")
        return False
    
    #====Tratamento de interrupção do usuário (Ctrl+C) e outras exceções============
    except KeyboardInterrupt:
        '''
        Em alguns ambientes, a espera pode ser interrompida, mas o setup elevado
        continua em paralelo. Faz uma checagem curta antes de concluir falha.
        '''
        #====Em vez de aguardar o tempo limite completo, aguarda apenas 20 segundos para verificar se o setup elevado concluiu============
        prazo_graca = time.time() + 20
        while time.time() < prazo_graca:
            #====Verifica se o arquivo de flag foi criado
            if os.path.exists(cfg.arquivo_flag):
                cfg.log.info("Setup elevado concluído com sucesso.")
                return True
            
            #====Verifica se o arquivo de status foi criado e lê o conteúdo para determinar sucesso ou falha============
            if os.path.exists(cfg.arquivo_status):
                try:
                    with open(cfg.arquivo_status, "r", encoding="utf-8") as f:
                        status = f.read().strip().upper()

                    #====Se o status for OK, o setup foi concluído com sucesso else, retorna falha ============
                    if status == "OK":
                        cfg.log.info("Setup elevado concluído com sucesso.")
                        return True
                    else:
                        cfg.log.warning("Setup elevado retornou falha. Verifique o LOG para detalhes de permissões.")
                        return False
                except Exception:
                    pass
            #====Aguarda 1 segundo antes de verificar novamente============    
            time.sleep(1)

        cfg.log.warning("Acompanhamento do UAC foi interrompido. Setup pode ter seguido em paralelo; verifique os logs.")
        return False
    except Exception as e:
        cfg.log.warning(f"Falha ao solicitar elevação do setup: {e}")
        return False

#====Função principal para tentar o setup na primeira execução do script============
def tentar_setup_primeira_execucao(cfg: DefenderSetup):
    
    #====Verifica se o arquivo de flag de primeira execução existe. Se existir, não faz nada============
    if os.path.exists(cfg.arquivo_flag):
        return

    #====Caso não exista, tenta configurar o Windows Defender, seja com privilégios de administrador ou solicitando UAC============
    cfg.log.info("Primeira execução detectada: tentando auto-configuração do Windows Defender...")
    ok = False

    try:
        #====Verifica se o usuário tem privilégios de administrador. Se sim, executa o setup diretamente============
        if _tem_privilegio_admin():
            ok = configurar_exclusoes_defender(cfg)
        
        #====Se não tiver privilégios de administrador, solicita UAC para executar o setup elevado============
        else:
            ok = _executar_setup_elevado(cfg)

        #====Informa o resultado da tentativa de setup(Ok==TRUE; sucesso; falha)============
        if ok:
            cfg.log.info("Auto-configuração concluída com sucesso.")
        else:
            cfg.log.warning("Auto-configuração não concluída. Se necessário, execute manualmente com --setup como administrador.")
        
    #====Tratamento de interrupção do usuário (Ctrl+C) e outras exceções============
    except KeyboardInterrupt:
        cfg.log.warning("Auto-configuração interrompida pelo usuário. Seguindo execução normal do relatório.")
    except Exception as e:
        cfg.log.warning(f"Auto-configuração interrompida: {e}")


    finally:
        #====Só marca como concluído quando setup finalizar com sucesso============
        if ok:
            with open(cfg.arquivo_flag, "w", encoding="utf-8") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    