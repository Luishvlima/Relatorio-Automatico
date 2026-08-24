#================================================================================
#  Importações
#================================================================================
import time
from datetime import datetime, timedelta

#==== Função para validar e processar os horários de execução fornecidos ============
def _parse_horarios_agendador(horarios_entrada) -> list[tuple[int, int]]:

    #==== Verifica se a entrada é uma lista, tupla ============
    if isinstance(horarios_entrada, (list, tuple)):
        horarios_str = ",".join(str(x).strip() for x in horarios_entrada)

    #==== Caso seja uma string, apenas remove espaços em branco ============
    else:
        horarios_str = str(horarios_entrada or "").strip()

    #==== Valida se a string de horários está vazia, else erro ============
    if not horarios_str:
        raise ValueError("Informe ao menos 1 horário em HH:MM.")

    #==== Armazena os horários válidos(horarios) e os horários já vistos(vistos) ============
    horarios, vistos    = [], set()

    #==== Loop para validar cada horário e armazenar os válidos na lista de horários ============
    for item in horarios_str.split(","): # Separa os horários por vírgula
        texto = item.strip()             # Remove espaços em branco no início e no final

        if not texto:  # Ignoar horários vazios
            continue
        
        #==== Separa a hora e o minuto e valida se estão correto ===========
        try:
            hora, minuto = [int(x) for x in texto.split(":", 1)] # Separa a hora e o minuto por ":"

            if not (0 <= hora <= 23 and 0 <= minuto <= 59):      # Verifica se a hora está entre 0 e 23 e o minuto entre 0 e 59
                raise ValueError
            
        except Exception as e:
            raise ValueError(f"Horário inválido: '{texto}'. Use HH:MM (ex.: 07:30).") from e

        #==== Adiciona o horário válido à lista de horários, evitando duplicatas ============
        chave = (hora, minuto)
        if chave not in vistos:
            vistos.add(chave)
            horarios.append(chave)

    if not horarios:
        raise ValueError("Nenhum horário válido informado.")

    #==== Retorna a lista de horários válidos, ordenada por hora e minuto ============
    return sorted(horarios) 

#==== Função para calcular o próximo disparo do agendador com base nos horários fornecidos ============
def _proximo_disparo_diario(horarios: list[tuple[int, int]]) -> datetime:
    #==== Verifica se a lista de horários está vazia, caso esteja, levanta um ValueError ============
    if not horarios:
        raise ValueError("Horários inválidos.")
    
    
    agora = datetime.now() # Pega a data e hora atual
    candidatos = [         # Lista de candidatos para o próximo disparo, com base nos horários fornecidos
        agora.replace(hour=hora, minute=minuto)
        for hora, minuto in horarios
    ]

    #==== Filtra os horários que ainda não passaram e retorna o próximo horário válido ============
    futuros = [c for c in candidatos if c > agora]
    if futuros:
        return min(futuros)

    #==== Se todos os horários já passaram, retorna o primeiro horário do próximo dia ============
    primeiro_hora, primeiro_minuto = horarios[0]
    return (# adiciona 1 dia à data atual e define a hora e minuto para o primeiro horário do próximo dia
        agora + timedelta(days=1)).replace(hour=primeiro_hora,minute=primeiro_minuto)

#==== Loga o status do agendador, incluindo os horários de execução e o próximo disparo ============
def _log_status_agendador(horarios_txt: str, proximo: datetime, LOG) -> None:
    #==== Loga o status do agendador, incluindo os horários de execução e o próximo disparo ============
    LOG     .info("=" * 60)
    LOG     .info("AGENDADOR ATIVO — execuções diárias às")
    LOG     .info(f"{horarios_txt}")
    LOG     .info(f"Próximo disparo às: {proximo.strftime('%H:%M')}")
    LOG     .info("=" * 60)

#==== Função principal do agendador, que executa a função main() nos horários especificados ============
def executar_agendador(horarios_execucao = "00:00", executar_agora: bool = False, log=None, criar_estrutura=None, tentar_setup_primeira_execucao=None, main=None, cfg_setup=None) -> bool:
    #======================Configurações globais para a função======================
    LOG = log
    criar_estrutura()
    if tentar_setup_primeira_execucao is not None:
        if cfg_setup is not None:
            tentar_setup_primeira_execucao(cfg_setup)
        else:
            tentar_setup_primeira_execucao(LOG=LOG)
    #==== Valida e processa os horários de execução fornecidos ============
    try:
        # Verfica se os horários de execução são válidos e retira duplicatas.
        horarios    = _parse_horarios_agendador(horarios_execucao)
        # Calcula o próximo disparo com base nos horários válidos.
        proximo     = _proximo_disparo_diario(horarios)
    except ValueError as e:
        LOG.error(str(e))
        return False
    
    #==== Loga o status do agendador, incluindo os horários de execução e o próximo disparo ============
    horarios_txt    = ", ".join([f"{h:02d}:{m:02d}" for h, m in horarios])
    _log_status_agendador(horarios_txt, proximo, LOG)
    print("")

    #==== Se a execução imediata foi solicitada, executa a função main() e recalcula o próximo disparo ============
    if executar_agora:
        LOG.info("=" * 60)
        LOG.info("Execução imediata solicitada (--agora).")
        LOG.info("=" * 60)
        print()
        main()
        proximo = _proximo_disparo_diario(horarios)
        _log_status_agendador(horarios_txt, proximo, LOG)

    #==== Loop principal do agendador, verificando a cada 20 segundos se é hora de executar a função main() ============
    try:
        while True:
            try:
                agora = datetime.now()
                if agora >= proximo:
                    LOG.info("=" * 60)
                    LOG.info("Disparo do agendador iniciado.")
                    main()
                    proximo = _proximo_disparo_diario(horarios)
                    _log_status_agendador(horarios_txt, proximo, LOG)
                time.sleep(30)  # Aguarda 30 segundos antes de verificar novamente
            except KeyboardInterrupt:
                LOG.info("SIGINT recebido — interrompendo agendador.")
                break
    except Exception as e:
        LOG.error(f"Erro inesperado no agendador: {e}")
        return False
    