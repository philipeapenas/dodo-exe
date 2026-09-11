# Fluxos operacionais - o catalogo que faz um prompt rodar a cadeia inteira

**Versao:** 1.0 | **Data:** 28/08/2026 | **Owner:** dodo-ia

Este arquivo existe pra que o time funcione como um assistente que usa todas as skills
disponiveis a partir de fluxos operacionais registrados: quando um processo precisar ser
aplicado, **um prompt so roda o fluxo inteiro.**

**Um prompt so roda a cadeia inteira quando a cadeia tem nome.** Sem catalogo, cada fluxo
precisa ser reconstruido na conversa, e o que ele diz vira pedido em vez de gatilho.

---

## Processo e fluxo sao coisas diferentes

Essa distincao e a razao de este arquivo existir, e ela nao estava escrita em lugar nenhum.

| | **Processo** | **Fluxo** |
|---|---|---|
| Responde | Como se faz esta coisa | Quem faz o que, em que ordem |
| Escopo | Uma skill, sozinha | Varias skills em cadeia |
| Onde vive | `Vault/Processos/`, e a `memory/` da skill dona | Aqui, no catalogo |
| Exemplo | "Faceswap + Motion control", "Instalar Nginx Proxy Manager" | "Abrir bloco de operacao": dodo-ia depois ceo-dodo depois assistente-expert |

Em 28/08/2026 o vault tinha **26 processos escritos e zero fluxos catalogados**. Os fluxos
existiam espalhados: um na Regra de Ouro 18, dois na memoria da dodo-ia, um numa nota de
projeto escrita no dia anterior. Nenhum lugar listava todos.

---

## O catalogo

**Ele nasce pequeno de proposito.** So entra fluxo que ja rodou de verdade. Fluxo inventado
que nunca foi executado e chute com cara de processo.

| Gatilho (o que ele diz) | Fluxo | Cadeia | Playbook |
|---|---|---|---|
| Abre um bloco de operacao de uma OP | **Abertura de operacao** | dodo-ia levanta o estado > ceo-dodo roda o strategic_os e especifica > assistente-expert escreve a decisao estrategica, o plano e a nota do dia | Regra de Ouro 18 + `gerir_ativos_playbook.md` |
| "perfeito, aplique o plano do dia" | **Execucao do plano** | dodo-ia conduz pela ordem do plano de execucao, que ja e a ordem de prioridade, e le o "Como cada processo deve ser feito" antes de cada processo > frontend-expert faz o CSS e entrega o contrato de classes > dev-expert faz o comportamento, em repasse sequencial > publica e confere pelo endereco real > o fundador testa na tela e a reprovacao vira nova rodada, sem reabrir o plano > assistente-expert encerra | Regra de Ouro 18, secao O GATILHO DE EXECUCAO, e a nota de processo `Execucao do plano do dia` em `Vault/Processos/`, quando existir |
| Declara a hora real que acordou ou comecou | **Recalculo do dia** | dodo-ia roda `tools/recalcular_dia.py` e avisa o que deslizou e o que estourou o limite de 00h | `gerir_ativos_playbook.md`, secao 4 |
| Abre a organizacao da semana, no domingo | **Fechamento da semana** | dodo-ia levanta o estado das OPs > ceo-dodo devolve a ordem por restricao e ROI > fundador decide > assistente-expert escreve a semana | `fechamento_da_semana.md` |
| "sessao encerrada", "pode fechar", "finalizamos" | **Encerramento** | assistente-expert roda o auto-archive: relatorio de execucao, nota de entrega, documentos vivos, mensagens e registro | Regra de Ouro 14 + `auto_archive_protocol.md` da assistente |
| "monta os scripts de venda do nicho X" | **Script de vendas por nicho** | copywriter-expert escreve por bloco, o fundador aprova bloco a bloco > assistente-expert grava no vault | `script_de_vendas_playbook.md` da copywriter |
| "monta a vitrine do cliente X" | **Esteira de vitrines** | vitrine-expert conduz as 7 etapas > copywriter (copy) > frontend (HTML/CSS) > dev (JS) > vercel (deploy) | `SKILL.md` da vitrine-expert |
| "analisa esse site que baixei" | **Engenharia reversa de site** | clone-site-expert diagnostica e higieniza > copywriter > frontend > dev > vercel | `SKILL.md` da clone-site-expert |
| "roda o pipeline de motion do dia" | **Motion content** | motion-expert (faceswap e motion control) > voice-expert (voz) > lipsync-expert (sincronia) | `SKILL.md` da motion-expert |
| Qualquer skill nao sabe fazer algo | **Treinamento ou contratacao** | a skill manda `help` > skill-expert pesquisa, apresenta e so grava com aprovacao | Regra de Ouro 1 + `training_protocol.md` |

---

## Como acionar

1. **Reconheca o gatilho na fala dele**, nao espere a palavra exata da tabela. Ele fala do
   jeito dele: "vamos iniciar as decisoes estrategicas da OP X" e "bora abrir a Loja"
   disparam o mesmo fluxo.
2. **Rode a cadeia inteira no mesmo turno.** Invoque a proxima skill voce mesma, sem devolver
   a bola. Devolver a bola e o oposto do que ele pediu.
3. **Leia o playbook do fluxo antes de comecar.** Ele carrega o detalhe que a tabela nao cabe.
4. **Nao pule etapa da cadeia.** Cada uma existe porque a anterior nao pode fazer o trabalho
   dela: a dodo-ia nao escreve no vault, o ceo-dodo nao executa, a assistente nao inventa meta.

**A unica coisa que interrompe um fluxo em execucao** e achado que ameace dado, dinheiro ou o
ar de uma operacao. Qualquer outro achado vira ajuste registrado, e o fluxo segue.

---

## Como registrar um fluxo novo

Pela Regra de Ouro 20, processo repetivel ganha dono. **Fluxo repetivel ganha linha aqui.**

O gatilho pra registrar e a **segunda vez**: na primeira, ele foi conduzido na conversa; se
vai acontecer de novo, vira linha do catalogo antes de a terceira chegar.

O que a linha precisa ter:

1. **O gatilho na fala dele**, nao no vocabulario tecnico.
2. **A cadeia, em ordem, com quem faz o que.**
3. **O ponteiro pro playbook.** Regra de Ouro 17: aponta, nunca copia. Se o playbook nao
   existir, ele nasce na `memory/` da skill que conduz, escrito pela `skill-expert`.
4. **O que entra e o que sai**, quando nao for obvio.

Precedente: em 27/08/2026 o fluxo de montar script de vendas por nicho foi conduzido inteiro
na conversa, e no mesmo dia virou processo escrito e playbook da copywriter. Foi isso que fez
os treze nichos seguintes custarem minutos em vez de repetir as oito correcoes dele.

---

## Quando ele reprova algo que o time entregou

**Quando o time faz algo que o fundador nao aprova, o responsavel pela tarefa e aperfeicoado.**

A Regra de Ouro 12 ja manda a skill que errou pedir treinamento. O buraco: **skill que nao
sabe que errou nunca dispara.** A reprovacao dele e o sinal que fecha esse buraco, e quem
roteia e a dodo-ia.

O caminho, quando ele reprovar:

1. **Ache o responsavel, nao o culpado.** O `mensagens.json` do projeto registra cada handoff
   com quem fez o que. E ali que se descobre de quem foi a entrega, sem chutar.
2. **Separe erro de preferencia.** Erro e o que quebrou uma regra que ja existia. Preferencia
   e ele querer diferente do que estava escrito. **Os dois viram treinamento**, mas o texto
   muda: erro vira "isto quebrou a regra X"; preferencia vira "a partir de agora e assim, e o
   motivo e este".
3. **Capture o porque, com a palavra dele.** Regra sem porque nao generaliza pro caso novo.
   Citacao literal vale mais que parafrase.
4. **Mande `help` pra `skill-expert`** com o responsavel, o que aconteceu, a correcao e a
   palavra dele. A skill-expert pesquisa, apresenta e so grava com aprovacao dele.
5. **Se a mesma correcao aparecer numa segunda skill**, ela deixou de ser da skill e virou do
   ecossistema. Ai a proposta e Regra de Ouro, e nao memoria de uma skill so. O criterio de
   corte esta no `SKILL.md` desta skill.

Precedente: em 27/08/2026 o fundador corrigiu oito pontos durante a escrita dos roteiros de
venda. As oito viraram regra na memoria da `copywriter-expert` no mesmo dia, e uma delas, a
proibicao de travessao, subiu pra Regra de Ouro 21 porque valia pra todo mundo.

---

## ANTES de conduzir: veja se o processo ja foi feito

**Obrigatorio quando ele pedir um processo no chat.** Leia `Vault/Processos/` procurando
processo com o mesmo proposito, nas pastas de area que existirem.

O que voce ganha ao achar:

- **O fluxo que ja funcionou**, em passos, na linguagem dele. Nao reconstrua na conversa o que
  ja esta escrito.
- **O tempo que levou** (`Qnt tempo p fazer`). E o que transforma o pedido em orcamento na hora
  de montar o dia.
- **A ordem que ele considerou certa**, que costuma diferir da ordem obvia.

O que voce NAO vai achar la, e nao deve procurar: como cada passo e executado por dentro. Isso
e treinamento da skill que executa. Se a tecnica faltar, o caminho e `help` pra `skill-expert`,
nao improviso.

**Se nao achar processo escrito**, conduza pelo catalogo acima e avise que e a primeira vez.
Ao encerrar, a `assistente-expert` escreve a nota (Regra de Ouro 22), e da proxima vez ela
existe.

**Se achar mas o fluxo tiver mudado**, diga a ele o que mudou antes de rodar. Nota de processo
desatualizada e pior que nota inexistente: ela parece verdade.

---

## O que este catalogo ainda nao cobre

Honestidade sobre o estado, pra ninguem contar com o que nao existe:

- **Quase nenhum dos processos escritos em `Vault/Processos/` tem gatilho de disparo.**
  Eles sao CONSULTADOS antes de conduzir (secao acima). A excecao e o par de abertura e
  execucao do plano do dia, que virou playbook de duas linhas da tabela em 09/09/2026. Cada
  processo que virar rotina de verdade merece o mesmo tratamento.
- **As notas de processo antigas foram escritas a mao pelo fundador**, e uma delas estava
  vazia ha semanas. A partir de 28/08/2026 quem escreve e o time, no encerramento. Espere a
  pasta ficar mais confiavel com o tempo, nao de imediato.
- **A maioria dos fluxos da tabela tem uma skill maestro** (vitrine-expert, clone-site-expert,
  motion-expert) que ja conduz sozinha. O ganho da dodo-ia neles e saber que existem e
  disparar o certo, nao refazer o trabalho deles.
- **Fluxo que atravessa skills sem maestro e o que mais custa hoje**, porque precisa ser
  conduzido na conversa. E onde catalogar rende mais.
