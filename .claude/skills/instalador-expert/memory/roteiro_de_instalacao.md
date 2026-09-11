# Roteiro de instalacao - a conversa que transforma o modelo no workspace da pessoa

**Owner:** instalador-expert

O script `tools/instalar.py` monta as pastas. Este roteiro monta o que o script nao sabe: quem e a pessoa, o que ela gere e o que ela persegue. E isso que faz a `dodo-ia` decidir como ELA decidiria, e nao pela media da internet.

---

## As tres leis da conversa

1. **Uma pergunta por vez, na ordem abaixo.** Pessoa nova nao sabe ainda o que cada campo alimenta; despejar dez perguntas de uma vez gera resposta rasa em todas.
2. **Palavra dela, literal.** O que ela disser vai para a nota do jeito que ela disse. Nao melhore a frase, nao complete o que ela nao disse. Principio inventado vira criterio falso na `dodo-ia`.
3. **"Depois" e resposta valida.** Campo pulado recebe `(preencher)` e entra na lista de pendencias do fim. Nunca travar a instalacao esperando proposito de vida.

---

## A ordem das perguntas e onde cada resposta vai

| # | Pergunta | Vai para |
|---|---|---|
| 1 | Quais negocios ou operacoes voce toca hoje? Nome e uma frase de cada: o que vende e pra quem | `instalar.py --op "<Nome>"` para cada uma, depois a frase na linha de descricao da secao dela em `Vida Pessoal/Ativos.md` |
| 2 | Como voce se define em uma frase? | `## Quem sou:`, na linha `>` |
| 3 | O que voce quer conquistar? (proposito definido) | `> Propósito Definido:` |
| 4 | Qual o numero que prova que voce chegou? | `> Meta do propósito definido:` |
| 5 | Qual a recompensa que voce vai se dar quando chegar? | `> Medalha da conquista:`, um item `> - ` por recompensa |
| 6 | Por que isso importa alem de voce? | `> Propósito Maior:` |
| 7 | Tres a cinco principios que guiam suas decisoes, cada um com o porque | `### Princípios:`, um item por principio no formato `- Nome: o porque` |
| 8 | Que horas voce costuma acordar? | Usada no passo de gerar a semana (abaixo). Nao vai para a Identidade |
| 9 | Quer ajustar a rotina agora ou comecar com a de exemplo? | Se ajustar: reescreva os itens de cada janela em `#### Rotina mestre (com horário)` no formato `- Nome (duracao) #area`. Se nao: fica a de exemplo, e isso vira pendencia |

**Dons, Talentos, Principios de conduta e Recursos/Habilidades** nao entram na conversa de instalacao: sao coisas que a pessoa descobre com o tempo. Ficam com o texto de exemplo e entram na lista de pendencias.

---

## Como escrever na Identidade sem quebrar os scripts

Os scripts da `dodo-ia` leem a Identidade pelo TITULO da secao. Mude o conteudo, nunca o titulo.

- **Titulos que nao podem mudar:** `### Propósito`, `### Princípios:`, `### Hábitos:`, `#### Rotina mestre (com horário)`, `##### Todo dia - Hora X-Y (Nome da janela) - Foco: ...:`, `##### Por dia da semana ...:`, `#### Princípios de conduta (sem horário)`, `### Recursos/Habilidades`. Os acentos fazem parte do titulo.
- **Item de rotina:** `- Nome (duracao) #area`. Duracao em `5m`, `1h`, `1h30`. Item sem duracao e valido: ele aparece no dia sem horario.
- **As 7 areas:** `#espiritual #emocional #físico #intelectual #relacionamento #lazer #financeiro`. Item sem area fica fora da conta do equilibrio das areas.
- **Por ultimo, apague o aviso `> [!modelo]`** (as tres linhas do bloco no topo). E ele que diz ao workspace que a instalacao nao terminou. Confira com `python instalar.py --verificar`: tem que sair com codigo 0.

---

## Gerar a semana

Depois da Identidade escrita, a primeira nota da semana ja existe (o `instalar.py` criou, com os dias vazios). Gere o bloco de cada dia de HOJE ate domingo, com a hora da pergunta 8:

```
python .agents/skills/dodo-ia/tools/montar_esqueleto_dia.py --dia <Dia> --acordar HH:MM --forcar
```

O `--forcar` e necessario porque o titulo `#### <Dia>` ja existe vazio na nota. Rode primeiro com `--dry-run` no dia de hoje e mostre o bloco a pessoa: e a primeira vez que ela ve a rotina virar horario.

---

## Automacoes do Windows (opcionais, desligadas)

A `dodo-ia` tem tarefas que podem rodar sozinhas no Windows: criar a autopsia do dia de manha, vigiar a rotina e empurrar o horario quando uma tarefa e marcada, e fechar o dia a noite. **O instalador nao registra nenhuma.** Mexer no agendador do computador de alguem sem pedir e invasivo.

Explique que existem, aponte `.agents/skills/dodo-ia/tools/comandos_da_rotina.md` e so registre se a pessoa pedir, uma de cada vez, dizendo o que cada uma faz antes.

---

## O fechamento da instalacao

Entregue, nesta ordem:

1. **O que foi criado:** as operacoes, a Identidade preenchida, a semana gerada.
2. **As pendencias:** cada campo que ficou `(preencher)` ou com exemplo.
3. **Como abrir:** no Obsidian, "Abrir pasta como vault" e escolher `Vault/`.
4. **Como o time funciona, em quatro frases:** diga a hora que acordou e a `dodo-ia` recalcula o dia; abra um bloco de operacao e ela conduz o ritual; no domingo ela organiza a semana com o `ceo-dodo`; quando nenhuma skill souber fazer algo, a `skill-expert` treina ou contrata.
