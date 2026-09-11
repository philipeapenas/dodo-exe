# Fechamento da semana - o ritual de domingo

**Versao:** 1.0 | **Data:** 28/08/2026 | **Owner:** dodo-ia

Playbook do bloco **"Auto gestao: fechamento da semana"**, o bloco extra de domingo a tarde que
existe alem da Auto gestao de 1h da manha. E nele que a semana seguinte nasce.

Nao confundir com o `gerir_ativos_playbook.md`, que rege o bloco de operacao de um DIA. Este
tem escopo de SEMANA.

---

## A regra que o fundador travou

> No domingo, quando o fundador fizer a organizacao da semana com a dodo-ia, ela fala com o
> `ceo-dodo` pra revisar as operacoes e projetos antes de organizar as prioridades.

**A dodo-ia nao prioriza a semana sozinha.** Ela levanta o estado e aciona o `ceo-dodo` no
mesmo turno, antes de qualquer ordem ser proposta.

---

## O que o bloco cobre, na nota da semana

O checklist que ele escreve no proprio bloco de domingo:

1. Ler o estimado x real dos 6 dias e corrigir as estimativas
2. Re-ler estados das operacoes e projetos
3. Criar as metas da semana seguinte por prioridades
4. Ler a resolucao de problemas da semana e montar plano de melhoria
5. Fechar o placar do mes nas 7 areas

**Confira o checklist no disco antes de operar.** Ele mexe nesta lista, do mesmo jeito que
mexeu no checklist do bloco de operacao (`reuso_de_padrao_de_nota.md`).

O item 2 e o que esta regra transforma: ele deixa de ser leitura solitaria e vira a analise do
`ceo-dodo`.

---

## A cadeia, e por que ela e a mesma da Regra de Ouro 18

```
dodo-ia      le o vault e levanta o estado. Entrega CRITERIO, nao a ordem.
   |         - Identidade e Ativos: proposito vigente e quais operacoes existem
   |         - Semana que fecha: o estimado x real dos 6 dias, e o que nao foi feito
   |         - Cada OP: as pendencias abertas, lidas na nota do dia mais recente dela
   |         - Placar das 7 areas + tools/equilibrio_das_areas.py: area fraca sem tarefa
   v
ceo-dodo     roda o strategic_os sobre TODAS as operacoes, nao sobre uma:
   |         qual e a restricao de cada uma, qual tem o maior ROI agora, o que esta a
   |         jusante de cano vazio, e o que sai da semana. Devolve a ORDEM.
   v
fundador     decide. A ordem final e dele.
   v
assistente-expert   escreve a nota da semana nova, no padrao da anterior.
```

E a mesma cadeia da Regra de Ouro 18, com escopo de semana em vez de dia. **A dodo-ia invoca o
ceo-dodo no mesmo turno**, sem devolver a bola pro fundador: ele pediu a revisao, nao pediu
pra ser lembrado de pedi-la.

---

## O que a dodo-ia leva pro ceo-dodo

Nao mande a conversa. Mande o levantamento, nesta forma:

| O que | De onde sai |
|---|---|
| Proposito e meta vigentes | `Vida Pessoal/Identidade.md` |
| Operacoes que existem hoje | `Vida Pessoal/Ativos.md` |
| O que a semana prometeu e o que entregou | A nota da semana que fecha, secao `#### Semana - por prioridade` |
| Estimado x real dos 6 dias | Os blocos `#### <Dia>`, campo `(estimado → real)` |
| Pendencias abertas por OP | A nota do dia mais recente de cada uma, secao `## Pendencias abertas` |
| Placar das 7 areas | A autopsia mais recente, e `tools/equilibrio_das_areas.py` |

---

## Por que esta regra existe

**Pendencia que escorrega de uma semana pra outra chega na segunda sem ninguem ter reavaliado
se ainda e prioridade.** Priorizar olhando so a lista da semana anterior repete a ordem antiga
por inercia, e a ordem antiga foi montada com o estado de sete dias atras.

O caso que gerou a regra: quatro pendencias de uma operacao passaram inteiras pra semana
seguinte. Sem revisao, elas voltariam na mesma posicao, sem ninguem perguntar se aquela
operacao ainda era a prioridade 3 da semana depois de nao ter entregue nada em duas semanas.

---

## Onde isso se conecta

- **Regra de Ouro 18** - o ritual de abertura do bloco de operacao. Esta e a versao semanal.
- `gerir_ativos_playbook.md` - o fluxo irmao de "Otimizar documentos da operacao", com a mesma
  cadeia de tres skills e a hierarquia decisao estrategica -> plano -> nota do dia -> entrega.
- `leitura_do_vault.md` - de onde sai cada campo do levantamento.
- `tools/equilibrio_das_areas.py` - cruza o placar das areas com as tarefas da semana e mostra
  area fraca sem tarefa. E a unica parte do levantamento que ja e automatica.
