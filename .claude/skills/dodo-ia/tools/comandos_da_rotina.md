# Comandos da rotina - copiar e colar

Os comandos prontos dos scripts desta pasta, com o que cada um faz e quando
usar. Existe pro fundador achar e rodar na mao sem precisar pedir. Fica junto dos scripts de proposito: um lugar so.

**Todo comando roda a partir da raiz do workspace:**

```
cd <pasta do workspace>
```

**Todo comando aceita `--dry-run`**, que mostra o resultado sem escrever nada.
Use sempre antes de valer.

---

## Onde mora o bloco do dia (mudou em 07/09/2026)

Antes, o bloco do dia e as listas vivas moravam sempre na nota da semana, e a
autopsia so mostrava por embed - que e somente leitura. Voce editava na semana.

Agora a secao **muda de casa**: de manha ela sai da semana e entra na autopsia
do dia; a noite ela volta. Voce edita o dia inteiro dentro da autopsia, num
arquivo so, e a semana volta inteira pra revisao de domingo.

Sete secoes entram nesse regime: a rotina do dia, Pendencias, Perguntas,
Desejos, Ideias e Resolucao de Problemas. Os Insights nao voltam pra semana:
sao arquivados no `Insights Geral` no fechamento.

Proposito, Ano, Mes e Semana por prioridade continuam embed de proposito. Sao
coisas que voce le, nao edita no dia - materializar a meta do mes criaria uma
copia por dia, e marcar numa deixaria as outras mentindo.

Enquanto a secao esta fora, a semana mostra `> Em posse da autopsia do dia:`
com o link. Nao apague essa linha na mao: e ela que marca o lugar de volta.

As ferramentas PERGUNTAM onde o bloco esta antes de escrever, entao rodar
`recalcular_dia.py` com o dia aberto ja escreve na autopsia. Elas imprimem
`bloco em: <arquivo> > <secao>` na primeira linha - confira se e o que voce
espera.

---

## 1. Acordei fora da hora, quero o dia deslizado

Edite **so** a linha `> Acordar:` no bloco do dia, dentro da nota da semana.
Depois:

```
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --pelo-acordar --dry-run
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --pelo-acordar
```

Desliza as tarefas preservando o espacamento que voce escreveu. Tarefa com
`> Hora marcada` embaixo nao desliza, porque o mundo nao remarca compromisso por
causa do seu sono.

**Os cabecalhos de janela nao deslizam: eles sao RECONSTRUIDOS** da Rotina mestre
mais o `> Acordar:`, em todos os quatro modos (desde 07/09/2026). A faixa de uma
janela e dado derivado, nao escolha. Deslizar por delta so funcionava quando a
nota inteira estava na mesma grade - e naquele dia metade dos cabecalhos tinha
sido movida a mao e metade nao, e nenhum delta unico consertava os dois lados.

Se preferir informar a hora no comando em vez de editar a nota:

```
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --acordar 08:30
```

---

## 2. Comecei um bloco fora da hora, quero so o resto do dia empurrado

```
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --apartir-de "Gerir ativos - parte criativa" --inicio 15:45 --dry-run
```

Soma a duracao declarada da tarefa em andamento e empurra dai pra frente
**apenas o que ainda esta `- [ ]`**. O que ja foi feito fica na hora em que foi
feito: mexer nisso apagaria o dado de cumprimento.

`--inicio` e opcional; sem ele, usa a hora ja escrita na tarefa.

---

## 3. Quero o dia inteiro recalculado pelas duracoes

```
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --realinhar --dry-run
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Quarta --realinhar
```

Anda pela nota na ordem em que as tarefas aparecem e recalcula cada horario:
duracao REAL de quem ja esta `- [x]`, duracao ESTIMADA de quem esta `- [ ]`.
Arredonda pro multiplo de 5 minutos.

**A janela e a ancora.** Ao cruzar um cabecalho `##### HHhMM-HHhMM`, o cursor
volta pro inicio daquela janela: atraso de uma janela nao contamina a seguinte.
Janela cujos itens nao cabem nela imprime `ESTOUROU ... passou N min`. Esse
aviso e informacao, nao erro: ele diz que a Rotina mestre declara mais tempo do
que a janela comporta, e quem conserta e a **Identidade**, nao a nota da semana.

---

## 4. Montar o bloco de um dia do zero

```
python ".agents\skills\dodo-ia\tools\montar_esqueleto_dia.py" --dia Quinta --acordar 05:30 ^
    --meta-operacional "Loja: publicar a pagina nova" ^
    --meta-operacional "Consultoria: apresentacao do projeto" ^
    --meta-pessoal "Dormir cedo." --dry-run
```

Le a Rotina mestre da `Identidade.md` e gera o bloco `#### <Dia>` com todos os
itens dela, agrupados por janela, com a hora contada do acordar.

`--meta-operacional` repete uma vez por operacao que o dia toca.
Sem `--forcar`, **nao sobrescreve** um bloco que ja existe.

Detalhe especifico do dia (o alvo da operacao, o grupo muscular do treino, o
link `[[Ativos#...]]`) entra a mao embaixo da tarefa, depois de gerar.

---

## 5. Criar a autopsia do dia

```
python ".agents\skills\dodo-ia\tools\criar_autopsia.py" --dia 2026-09-03 --dry-run
```

Roda sozinho todo dia as 05:00 pela tarefa do Windows "Dodo.IA - Criar autopsia
do dia". So rode na mao se a tarefa nao tiver rodado.

**E idempotente:** se a nota do dia ja existe, nao encosta nela. E isso que
impede sobrescrever o que voce escreveu no celular e ainda nao sincronizou.

Alem de criar a nota, ele **traz as secoes do dia** da semana pra dentro dela, e
**fecha o dia anterior** se o fechamento da madrugada nao tiver rodado.

Numa autopsia antiga, que nao tem `Ideias` nem `Resolucao de Problemas`, ele
acrescenta as secoes que faltam antes de trazer o conteudo.

`--sem-transporte` cria a nota e deixa as secoes na semana.

---

## 5b. Fechar o dia (devolver as secoes e arquivar os insights)

```
python ".agents\skills\dodo-ia\tools\fechar_dia.py" --dia 2026-09-07 --dry-run
```

Roda sozinho pela tarefa do Windows "Dodo.IA - Fechar o dia", 30 minutos depois
do fim da cascata. So rode na mao se quiser fechar antes da hora.

Devolve as sete secoes pra nota da semana e arquiva os insights no
`Insights Geral`, embaixo do tema e na data do dia.

**Se a semana ganhou conteudo enquanto a secao estava fora**, ele NAO escreve
por cima: acusa CONFLITO, aborta aquela secao e deixa os dois textos de pe, pra
voce juntar. Nada se perde em silencio.

Tema de insight que nao existe no `Insights Geral` nao e arquivado nem apagado:
ele para, lista os temas validos e deixa o texto na autopsia.

Deixa rastro em `.backups/autopsia/fechar_dia.log` (na raiz do workspace), uma
linha por execucao - porque as 03h ninguem esta olhando a tela.

---

## 5c. Reagendar o horario do fechamento

```
python ".agents\skills\dodo-ia\tools\agendar_fechamento.py" --mostrar
```

Le o ultimo horario do bloco do dia, soma 30 minutos e reescreve a tarefa do
Windows. `--mostrar` so calcula, sem agendar.

**Voce quase nunca precisa rodar isso na mao:** o `criar_autopsia.py` e o
`recalcular_dia.py` ja chamam ele sozinhos, porque mexer na cascata move o fim
do dia. Rode se desconfiar que a tarefa ficou no horario velho.

Se o PC estiver desligado na hora, a tarefa roda quando voce ligar. E se nem
isso acontecer, o `criar_autopsia.py` da manha seguinte fecha o dia anterior.

---

## 5d. Conferir que o transporte nao perde nada

```
python ".agents\skills\dodo-ia\tools\testar_posse.py"
```

Roda 21 conferencias sobre uma COPIA temporaria do cofre, nunca no cofre real.
A mais importante: a nota da semana tem que voltar byte a byte identica depois
de tomar e devolver a posse.

Rode depois de qualquer mudanca no `cofre.py`, no `criar_autopsia.py` ou no
`fechar_dia.py`. Um transporte que nao e exatamente reversivel so aparece dias
depois, ja sincronizado no celular, e sem como saber qual linha sumiu.

---

## 6. Ver onde as areas da vida estao fracas

```
python ".agents\skills\dodo-ia\tools\equilibrio_das_areas.py" --dia 2026-09-02 --notas 14
```

Cruza o placar das 7 areas com as tarefas da semana. Responde o que o placar
sozinho nao responde: a area esta fraca porque voce nao cumpriu, ou porque a
semana nao reservou nenhuma tarefa pra ela? Aponta tambem tarefa sem tag de
area, que fica fora da conta.

---

## 7. Nao quero rodar nada: o vigia faz sozinho

```
python ".agents\skills\dodo-ia\tools\vigia_rotina.py" --uma-vez --dry-run
```

Ele fica ligado o dia todo pela tarefa do Windows **"Dodo.IA - Vigia da rotina"**,
sem janela nenhuma na tela (roda em `pythonw.exe`). Toda vez que voce marca uma
tarefa e a nota fica parada por 20 segundos, ele reancora o resto do dia no fim da
ultima tarefa concluida.

**Ele nunca reescreve a hora de tarefa ja marcada.** Sua escolha em 07/09/2026,
entre "empurra o resto" e "realinha tudo": a hora que voce digitou e dado medido.

Onde ver o que ele fez: `Agente Orquestrador\vigia_rotina.log`.

Ligar, desligar e reiniciar:

```
powershell -Command "Start-ScheduledTask -TaskName 'Dodo.IA - Vigia da rotina'"
powershell -Command "Stop-ScheduledTask  -TaskName 'Dodo.IA - Vigia da rotina'"
powershell -Command "Disable-ScheduledTask -TaskName 'Dodo.IA - Vigia da rotina'"
```

**Editou o `vigia_rotina.py`? Precisa reiniciar (Stop e depois Start).** O Python
carrega o arquivo uma vez, na largada. Em 08/09/2026 ele passou o dia inteiro
rodando codigo velho porque nao foi reiniciado, e nao havia janela na tela pra
denunciar. Reiniciar nao e detalhe: e o unico jeito de a correcao existir.

O modo que ele usa por baixo, se voce quiser dar o empurrao na mao:

```
python ".agents\skills\dodo-ia\tools\recalcular_dia.py" --dia Terca --empurrar
```

Igual ao `--apartir-de`, mas achando sozinho a ultima tarefa concluida. Nao precisa
de `--semana`: o script pergunta ao cofre onde o dia mora agora.

---

## 8. Mudei a Rotina mestre e os dias ja escritos ficaram velhos

```
python ".agents\skills\dodo-ia\tools\montar_esqueleto_dia.py" --dia Terca --janela Inercia --dry-run
python ".agents\skills\dodo-ia\tools\montar_esqueleto_dia.py" --dia Terca --janela Inercia
```

Regenera **uma janela so** de um dia que ja existe, na ordem e nas duracoes
vigentes da `Identidade`, e **preserva o resto do bloco**: o alvo da operacao, o
grupo muscular do treino, os links de Ativos e as linhas de hora marcada.

Serve pro caso real de 07/09/2026: voce reordenou a Inercia no meio da semana e os
seis dias seguintes continuaram na ordem velha. Regerar o dia inteiro teria apagado
tudo que voce escreveu a mao neles.

**Ele aborta e lista** se encontrar qualquer linha escrita a mao dentro daquela
janela, em vez de apagar calado. Use `--forcar` so quando quiser mesmo perder.

Nao precisa de `--acordar`: nesse modo a hora vem do `> Acordar:` da propria nota.

---

## Ordem quando o dia ja comecou

1. `--pelo-acordar` **primeiro**, se a hora de acordar mudou.
2. `--apartir-de` durante o dia, quando um bloco atrasou.
3. `--realinhar` no fim, com as duracoes reais preenchidas, pra fechar o dia.

Rodar `--realinhar` antes de preencher as duracoes reais so recalcula pelo
estimado, e ai ele nao esta medindo nada: esta repetindo o plano.
