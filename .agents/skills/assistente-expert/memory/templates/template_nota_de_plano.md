# Template - Nota de plano (o "Plano do dia" de uma OP)

Formato canonico da nota que a nota do dia linka no campo **Plano do dia**.
Vive em `Operações/OP <Nome>/Planos/<Titulo do plano> DD-MM-AA.md`.

Confirmado em uso real em quatro notas de plano de operacoes diferentes. A mais completa foi
a que introduziu o campo de especificacao tecnica.

## O nome do campo

O campo dos passos numerados chama-se **`### Plano de execução:`**. O nome antigo era
`### Processos:`. Notas antigas podem ter o nome antigo; a migracao pegou nas novas.

**Ao abrir nota de plano antiga, nao renomeie o campo dela.** O nome novo vale pra nota nova.
Se precisar decidir de novo, vale a regra de sempre: o disco ganha, e a nota irma mais recente
e a referencia (`reuso_de_padrao_de_nota.md`).

## A regra que rege este template

**O plano do dia nasce da meta do dia, e a meta do dia e a decisao estrategica do dia.**
Travado pelo fundador em 24/08/2026. Nao se inventa meta aqui: ela ja existe como nota
datada em `Operações/OP <Nome>/Decisões estratégicas/`, com direcao, consequencia e o que
continua aberto. O plano so responde **como chegar la**.

## Esqueleto

```
# Meta: <a meta em uma frase, comecando por um verbo>

## Ideia:
<um paragrafo. O que e, como funciona e por que agora. Referencia de desenho, se houver.>

### Plano de execução:
> A numeração já é a ordem de execução.

1. <passo em linguagem de negocio>
2. ...
(tipicamente de 5 a 8. Cada um e um pedaco entregavel, nao uma tarefa tecnica)

### Como cada processo deve ser feito:
> <uma linha dizendo que o afirmado veio do fundador e o marcado _proposta_ e sugestao do time>

**1. <processo, igual ao plano de execucao>** (<quem faz>)
- <passo de como fazer, na linguagem dele>
- _Proposta:_ <o que o time sugere e ele ainda nao decidiu>
- Pronto quando: <o check concreto que prova que o processo fechou>

**2. ...**

**Criterio de corte:** se o dia apertar, cai primeiro o processo N. Nunca o processo N.

### Decisao estrategica: [[<decisao> - <Projeto> - DD-MM-AA]]

### Especificacao tecnica: [[<nota do dia>]]

### Relatorio da entrega:
Dia 1 - DD/MM: [[<nota do dia>]]
Dia 2 - DD/MM: [[<nota do dia>]]

```

## Regras de cada secao

**`# Meta:`** uma frase, comecando por verbo. E o titulo da nota inteira, nao um resumo.

**`## Ideia:`** paragrafo corrido, nunca lista. Vale a Regra de Ouro 13 - linguagem de
negocio, sem termo tecnico, sem caminho de arquivo, sem nome de tabela. O detalhe tecnico
vive na nota do dia, que esta linkada em Especificacao tecnica.

**`### Plano de execução:`** numerados, e **a numeracao ja e a ordem de execucao**, a mesma da
prioridade. Cada item e um pedaco que, pronto, muda alguma coisa pro cliente ou pro dono da
operacao. Nao e checklist de implementacao - sem checkbox, porque o progresso e marcado na nota
do dia, nao aqui. A ordem dos numeros ja e a ordem de prioridade.

**`### Como cada processo deve ser feito:` - criada pelo fundador.** Ela detalha como ele quer
que cada etapa dos processos seja feita, pra dar mais contexto na hora da execucao. Regras:

* **Um bloco por processo do plano de execucao**, mesma numeracao e mesmo nome. O titulo leva
  quem faz entre parenteses (skill ou fundador) e o estado quando houver (`feito`).
* **Sem estimativa de tempo.** Estimado e
  real sao dele, na linha da tarefa da rotina do dia, nunca no plano.
* **O que veio da fala dele fica afirmado; o que e sugestao do time leva `_Proposta:_`.** E o
  que ele revisa primeiro: a proposta e onde o time pode estar supondo.
* **Cada bloco fecha com `Pronto quando:`**, o check concreto e observavel (Regra de Ouro 7 §4).
* **Linguagem de negocio** (Regra de Ouro 13). O detalhe tecnico continua na nota do dia,
  linkada em Especificacao tecnica.
* **Fecha com o `Criterio de corte`**: o que cai primeiro se o dia apertar, e o que nunca cai.

**`### Prioridade critica:` - REMOVIDA pelo fundador.** Ele apagou a secao da nota de plano,
porque a ordem passou a morar na
propria numeracao do plano de execucao e o porque de cada processo mora no `Como cada processo
deve ser feito`. **Nao recolocar em nota nova.** Nota antiga que ainda tem a secao fica como
esta. O texto abaixo e o historico de como ela funcionava ate 09/09:

**(historico) `### Prioridade critica:` - travada pelo fundador em 24/08/2026.** E a secao que
responde "o que realmente importa pra fechar a meta do dia". Tres regras:

* **Ela ordena a execucao**, nao a numeracao dos processos. Processo 7 antes do 5 e
  normal se a prioridade mandar - o que nao pode e a ordem ser silenciosa.
* **Ela cresce durante o trabalho.** Ideia que o fundador joga no meio da execucao entra
  aqui e reordena o que vem depois. Foi assim que nasceu: a secao comecou como
  "Decisoes que entraram durante a execucao" e ele a promoveu, porque o valor nao era
  registrar a decisao - era lembrar do que importa.
* **Cada item diz por que SEM ELE a meta nao fecha**, e cita entre parenteses quais
  processos o atendem. Item que nao consegue justificar isso nao e prioridade critica,
  e sim um processo qualquer.

**(historico) A nota da semana puxava esta secao por embed.** Desde 07/09/2026 o fundador nao quer
embed de prioridade critica na semana nem na autopsia, e desde 10/09/2026 a secao nao existe mais.

**`### Decisao estrategica:`** o link pra nota que gerou este plano. O nome dela segue o padrao
`<decisao> - <Projeto> - DD-MM-AA` desde 10/09/2026 (ver `vault_structure.md`). Se nao existir
decisao estrategica escrita, ela vem PRIMEIRO - plano sem decisao e chute com formato.

**`### Especificacao tecnica:`** o link pra nota do dia em `Tarefas/<Mes>/<OP>/`. E a
ponte entre o plano (negocio) e o registro tecnico (Regra de Ouro 16).

**`### Relatorio da entrega:`** uma linha por dia de trabalho, acumulando. Nunca apagar
linha antiga - e o historico de quantos dias o plano custou de verdade.

**`Prazo estimado`, `Prazo entregue`, `Nota`, `Justificativa`: REMOVIDOS em 09/09/2026.**
O fundador apagou os quatro campos do fim da nota de plano, junto com outras informacoes que
deixaram de ser necessarias. **Nao recolocar.** Em 10/09/2026 eles voltaram por engano num plano
novo, copiados de uma nota irma anterior a remocao, e ele cobrou de novo. **Nota irma mais antiga que uma remocao registrada aqui nao ressuscita o campo.** Eles nasciam em branco esperando que ele
preenchesse no fechamento, e ficavam em branco. O tempo real por processo continua vivo onde
ele de fato escreve, que e a linha da tarefa na rotina do dia (`(45m -> )`).

## Quem escreve, e em que ordem

Fluxo travado pelo fundador em 24/08/2026:

1. **dodo-ia** le o vault e aponta qual e a decisao estrategica vigente e o estado real.
2. **ceo-dodo** analisa a meta pelo `strategic_os.md` e especifica exatamente o que a nota
   deve dizer.
3. **assistente-expert** escreve, neste template.

A assistente nao inventa a meta e nao pula o CEO.
