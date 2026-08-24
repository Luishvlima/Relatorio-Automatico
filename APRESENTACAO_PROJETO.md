# Automacao de Relatorios IRR/IFI

## Contexto pessoal e profissional

Este foi meu primeiro projeto de programacao. Comecei a desenvolve-lo como um projeto pessoal para facilitar demandas recorrentes do meu trabalho, enquanto ainda atuava na area administrativa como jovem aprendiz. Ao longo do tempo, fui aperfeicoando a estrutura, corrigindo falhas, adicionando novos recursos e aprimorando a confiabilidade da automacao.

O projeto teve um papel importante na minha transicao da area de jovem aprendiz administrativo para a area de jovem aprendiz de programacao. Ele foi uma oportunidade pratica para aplicar Python na resolucao de um problema real, entender um fluxo de desenvolvimento de ponta a ponta e demonstrar que eu poderia contribuir tecnicamente com a equipe.

Depois deste projeto, desenvolvi diversas outras automacoes para apoiar processos da empresa. Essas solucoes posteriores nao estao sendo apresentadas porque pertencem a empresa e podem conter informacoes, regras de negocio e integracoes proprietarias. Essa limitacao e intencional e faz parte do compromisso de preservar a confidencialidade dos dados e ativos aos quais tive acesso profissionalmente.

## Visao geral

Este projeto foi desenvolvido como uma iniciativa pessoal para facilitar e automatizar demandas recorrentes do meu trabalho. O sistema consolida dados operacionais, gera relatorios de acompanhamento, cria dashboards visuais e distribui os resultados automaticamente.

A proposta principal foi reduzir tarefas manuais, diminuir a possibilidade de erros de consolidacao e tornar o acompanhamento dos indicadores mais rapido e padronizado.

## O que o sistema faz

- Agenda execucoes automaticas em horarios configuraveis.
- Baixa relatorios de diferentes fontes de dados.
- Reutiliza cookies de sessao quando disponiveis e solicita nova autenticacao quando necessario.
- Processa e padroniza dados tabulares com Python e pandas.
- Classifica atividades e status conforme regras de negocio.
- Calcula indicadores relacionados a IRR e IFI.
- Gera planilhas tratadas para consulta.
- Cria dashboards em formato de imagem.
- Envia os dashboards por Telegram para os destinatarios configurados.
- Organiza automaticamente arquivos brutos, arquivos tratados, imagens, configuracoes e logs.
- Possui uma etapa opcional de configuracao de exclusoes do Windows Defender para evitar interferencias na automacao local.

## Arquitetura

O projeto foi dividido por responsabilidade, mantendo o fluxo principal pequeno e facilitando a manutencao:

- `Relatorio_IRR-IFI - Repor.py`: ponto de entrada e orquestracao do processo.
- `RELATORIO_AIR.py`: comunicacao com a fonte de dados AIR.
- `RELATORIO_OFS.py`: download e tratamento inicial dos dados OFS.
- `LOGIN_AUTOMATICO.py`: automacao do fluxo de autenticacao por navegador.
- `CARREGAR_DADOS.py`: limpeza, normalizacao, cruzamento e calculo dos dados.
- `CRIACAO_DASHBOARD.py`: criacao dos dashboards visuais.
- `TELEGRAM.py`: envio de imagens e documentos.
- `CRIAR_PASTAS.py`: criacao da estrutura de diretorios.
- `LOG.py`: configuracao de logs em arquivo e no console.
- `AGENDADOR.py`: controle das execucoes programadas.
- `EXCLUSAO_DEFENDER.py`: configuracao opcional do ambiente Windows.
- `Transformado .exe.bat`: instalacao das dependencias e geracao do executavel com PyInstaller.

Na versao compartilhada, alguns nomes de arquivos foram generalizados para reduzir a exposicao de referencias internas. Os nomes acima correspondem a estrutura original e sao usados aqui apenas para explicar a organizacao e a responsabilidade de cada componente.

Essa separacao permite alterar uma fonte de dados, uma regra de negocio ou o formato do dashboard sem concentrar toda a logica em um unico arquivo.

## Tecnologias utilizadas

- Python
- pandas
- NumPy
- openpyxl
- requests
- Selenium
- Matplotlib
- PyInstaller
- Windows PowerShell

## Qualidade e decisoes tecnicas

### Separacao de responsabilidades

Cada modulo possui uma funcao clara. O arquivo principal coordena o fluxo, enquanto os demais componentes executam tarefas especificas. Isso facilita a leitura, a localizacao de falhas e futuras extensoes.

### Tratamento de erros

As operacoes de rede possuem timeout, novas tentativas e mensagens de log. O sistema tambem trata respostas vazias, sessoes expiradas, respostas HTML inesperadas e falhas na leitura de arquivos.

### Padronizacao de dados

Os dados recebidos podem ter acentos, espacos, formatos de data diferentes e valores ausentes. Por isso, o processamento inclui normalizacao de nomes de colunas, limpeza de texto, conversao de datas e tratamento de valores nulos antes dos calculos.

### Rastreabilidade

O sistema registra as principais etapas da execucao, incluindo inicio, tentativas de download, processamento, salvamento dos arquivos e falhas. Essa rastreabilidade ajuda a investigar problemas e acompanhar o resultado de cada execucao.

### Configurabilidade

Credenciais, tokens, identificadores de unidades, horarios e endpoints sao recebidos por configuracao, permitindo adaptar o sistema sem alterar a logica de processamento. Na versao entregue para avaliacao, esses valores foram removidos ou substituidos por placeholders.

### Distribuicao

O projeto possui um script de build para gerar um executavel com PyInstaller, simplificando a execucao em um computador Windows sem exigir que o usuario final conheca todos os detalhes da estrutura Python.

## Seguranca e confidencialidade

Este foi um projeto pessoal desenvolvido para apoiar atividades profissionais. Portanto, a versao original continha credenciais, tokens, identificadores, endpoints e referencias a informacoes internas da empresa onde o projeto era utilizado.

Por responsabilidade profissional e respeito a confidencialidade, removi da versao compartilhada:

- senhas de autenticacao;
- tokens de APIs e do bot do Telegram;
- identificadores de chat;
- e-mail utilizado no login;
- endpoints e URLs internas das fontes de dados;
- identificadores de unidades e configuracoes especificas da operacao;
- arquivos de cookies e perfis autenticados do navegador;
- planilhas, imagens, logs e quaisquer dados reais da empresa.

Os campos sensiveis foram deixados vazios ou substituidos por `<REMOVIDO POR SEGURANCA>`. Essa anonimizacao reduz o risco de exposicao acidental e deixa claro quais configuracoes precisam ser fornecidas pelo ambiente autorizado para que o sistema seja executado.

Uma evolucao recomendada seria retirar completamente os segredos do codigo e utilizar variaveis de ambiente, um gerenciador de segredos ou o Windows Credential Manager. Tambem seria adequado aplicar controle de acesso aos arquivos de cookies, logs e relatorios gerados.

## Aprendizados

O desenvolvimento envolveu problemas praticos de integracao entre APIs, planilhas, navegador, autenticacao multifator, agendamento e distribuicao de resultados. Alem da implementacao, foi necessario pensar em resiliencia, observabilidade, organizacao de arquivos e protecao de informacoes confidenciais.

Esse projeto fortaleceu minha capacidade de:

- decompor um processo manual em etapas automatizaveis;
- identificar e separar responsabilidades no codigo;
- lidar com falhas de rede e sessoes expiradas;
- transformar dados inconsistentes em informacao utilizavel;
- criar uma saida visual orientada a acompanhamento operacional;
- documentar limites e riscos de uma solucao;
- proteger dados internos ao apresentar um projeto em contexto externo.

## Consideracoes finais

Este repositorio representa a estrutura e as decisoes tecnicas de uma automacao real, mas nao inclui os dados nem as configuracoes proprietarias necessarias para acessar os sistemas originais. A remocao dessas informacoes foi intencional: demonstra que a qualidade de uma solucao inclui nao apenas fazer o processo funcionar, mas tambem preservar a seguranca, a privacidade e os limites de uso dos dados envolvidos.
