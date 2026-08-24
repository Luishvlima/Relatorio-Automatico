# Automação de Relatórios IRR/IFI

## Contexto pessoal e profissional

Este foi meu primeiro projeto de programação. Comecei a desenvolvê-lo como um projeto pessoal para facilitar demandas recorrentes do meu trabalho, enquanto ainda atuava na área administrativa como jovem aprendiz. Ao longo do tempo, fui aperfeiçoando a estrutura, corrigindo falhas, adicionando novos recursos e aprimorando a confiabilidade da automação.

O projeto teve um papel importante na minha transição da área de jovem aprendiz administrativo para a área de jovem aprendiz de programação. Ele foi uma oportunidade prática para aplicar Python na resolução de um problema real, entender um fluxo de desenvolvimento de ponta a ponta e demonstrar que eu poderia contribuir tecnicamente com a equipe.

Depois deste projeto, desenvolvi diversas outras automações para apoiar processos da empresa. Essas soluções posteriores não estão sendo apresentadas porque pertencem à empresa e podem conter informações, regras de negócio e integrações proprietárias. Essa limitação é intencional e faz parte do compromisso de preservar a confidencialidade dos dados e ativos aos quais tive acesso profissionalmente.

## Visão geral

Este projeto foi desenvolvido como uma iniciativa pessoal para facilitar e automatizar demandas recorrentes do meu trabalho. O sistema consolida dados operacionais, gera relatórios de acompanhamento, cria dashboards visuais e distribui os resultados automaticamente.

A proposta principal foi reduzir tarefas manuais, diminuir a possibilidade de erros de consolidação e tornar o acompanhamento dos indicadores mais rápido e padronizado.

## O que o sistema faz

- Agenda execuções automáticas em horários configuráveis.
- Baixa relatórios de diferentes fontes de dados.
- Reutiliza cookies de sessão quando disponíveis e solicita nova autenticação quando necessário.
- Processa e padroniza dados tabulares com Python e pandas.
- Classifica atividades e status conforme regras de negócio.
- Calcula indicadores relacionados a IRR e IFI.
- Gera planilhas tratadas para consulta.
- Cria dashboards em formato de imagem.
- Envia os dashboards por Telegram para os destinatários configurados.
- Organiza automaticamente arquivos brutos, arquivos tratados, imagens, configurações e logs.
- Possui uma etapa opcional de configuração de exclusões do Windows Defender para evitar interferências na automação local.

## Arquitetura

O projeto foi dividido por responsabilidade, mantendo o fluxo principal pequeno e facilitando a manutenção:

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

Na versão compartilhada, alguns nomes de arquivos foram generalizados para reduzir a exposição de referências internas. Os nomes acima correspondem à estrutura original e são usados aqui apenas para explicar a organização e a responsabilidade de cada componente.

Essa separação permite alterar uma fonte de dados, uma regra de negócio ou o formato do dashboard sem concentrar toda a lógica em um único arquivo.

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

## Qualidade e decisões técnicas

### Separação de responsabilidades

Cada módulo possui uma função clara. O arquivo principal coordena o fluxo, enquanto os demais componentes executam tarefas específicas. Isso facilita a leitura, a localização de falhas e futuras extensões.

### Tratamento de erros

As operações de rede possuem timeout, novas tentativas e mensagens de log. O sistema também trata respostas vazias, sessões expiradas, respostas HTML inesperadas e falhas na leitura de arquivos.

### Padronização de dados

Os dados recebidos podem ter acentos, espaços, formatos de data diferentes e valores ausentes. Por isso, o processamento inclui normalização de nomes de colunas, limpeza de texto, conversão de datas e tratamento de valores nulos antes dos cálculos.

### Rastreabilidade

O sistema registra as principais etapas da execução, incluindo início, tentativas de download, processamento, salvamento dos arquivos e falhas. Essa rastreabilidade ajuda a investigar problemas e acompanhar o resultado de cada execução.

### Configurabilidade

Credenciais, tokens, identificadores de unidades, horários e endpoints são recebidos por configuração, permitindo adaptar o sistema sem alterar a lógica de processamento. Na versão entregue para avaliação, esses valores foram removidos ou substituídos por placeholders.

### Distribuição

O projeto possui um script de build para gerar um executável com PyInstaller, simplificando a execução em um computador Windows sem exigir que o usuário final conheça todos os detalhes da estrutura Python.

## Segurança e confidencialidade

Este foi um projeto pessoal desenvolvido para apoiar atividades profissionais. Portanto, a versão original continha credenciais, tokens, identificadores, endpoints e referências a informações internas da empresa onde o projeto era utilizado.

Por responsabilidade profissional e respeito à confidencialidade, removi da versão compartilhada:

- senhas de autenticação;
- tokens de APIs e do bot do Telegram;
- identificadores de chat;
- e-mail utilizado no login;
- endpoints e URLs internas das fontes de dados;
- identificadores de unidades e configurações específicas da operação;
- arquivos de cookies e perfis autenticados do navegador;
- planilhas, imagens, logs e quaisquer dados reais da empresa.

Os campos sensíveis foram deixados vazios ou substituídos por `<REMOVIDO POR SEGURANÇA>`. Essa anonimização reduz o risco de exposição acidental e deixa claro quais configurações precisam ser fornecidas pelo ambiente autorizado para que o sistema seja executado.

Uma evolução recomendada seria retirar completamente os segredos do código e utilizar variáveis de ambiente, um gerenciador de segredos ou o Windows Credential Manager. Também seria adequado aplicar controle de acesso aos arquivos de cookies, logs e relatórios gerados.

## Aprendizados

O desenvolvimento envolveu problemas práticos de integração entre APIs, planilhas, navegador, autenticação multifator, agendamento e distribuição de resultados. Além da implementação, foi necessário pensar em resiliência, observabilidade, organização de arquivos e proteção de informações confidenciais.

Esse projeto fortaleceu minha capacidade de:

- decompor um processo manual em etapas automatizáveis;
- identificar e separar responsabilidades no código;
- lidar com falhas de rede e sessões expiradas;
- transformar dados inconsistentes em informação utilizável;
- criar uma saída visual orientada a acompanhamento operacional;
- documentar limites e riscos de uma solução;
- proteger dados internos ao apresentar um projeto em contexto externo.

## Considerações finais

Este repositório representa a estrutura e as decisões técnicas de uma automação real, mas não inclui os dados nem as configurações proprietárias necessárias para acessar os sistemas originais. A remoção dessas informações foi intencional: demonstra que a qualidade de uma solução inclui não apenas fazer o processo funcionar, mas também preservar a segurança, a privacidade e os limites de uso dos dados envolvidos.
