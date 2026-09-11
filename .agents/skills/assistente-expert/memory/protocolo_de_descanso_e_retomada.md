# Protocolo de Descanso e Retomada

**Versao:** 1.0 | **Data:** 13/08/2026 | **Owner:** assistente-expert
**Origem:** declarado pelo fundador durante a pausa de uma operacao.

Este playbook rege o que a `assistente-expert` faz quando o fundador **pausa** o trabalho do dia. Pausa nao e encerramento de sessao (isso e o `auto_archive_protocol.md`) - e uma interrupcao planejada, com retomada agendada.

---

## O modelo do fundador

A pausa **nasce da agenda, nao do cansaco.** Ele para porque tem outra coisa definida naquele horario nos blocos da agenda dele (`Corpo e Mente`, `Gerir ativos`, `Descanso mental`). Sempre depois da comida vem a recompensa pos-janta. E a aplicacao consciente do principio do descanso, priorizada conforme o dia.

**Numeros duros:**

| Parametro | Valor |
|---|---|
| Limite de trabalho do dia | 00h |
| Teto de operacao por dia | 6h |
| Cochilo - tranquilo | 30 minutos |
| Cochilo - cansado | 1 ciclo completo (1h30) |
| Cochilo - muito cansado | multiplos de ciclo (ex.: 3h = 2 ciclos) |
| Descanso completo depois das 00h | sempre 7h30 |

O que **varia** e a hora de deitar, conforme a demanda do dia. O que **nao varia** e a duracao: 7h30. O objetivo dele e acordar sempre tendo dormido 7h30.

Quando o teto de 6h de operacao bate, ele dorme - mesmo que ja tenha passado das 00h. O limite de 00h manda no que ele se propos a fazer; o teto de 6h manda na hora de parar.

---

## Regras operacionais (inegociaveis)

1. **Pausa nao encerra.** Ao ele avisar que vai pausar, NAO execute o ritual de encerramento. Confirme o ciclo de descanso do dia, calcule o saldo, agende a retomada e registre.

2. **Nunca proponha retomada que quebre ciclo de sono no meio.** Os unicos intervalos validos sao 30 minutos, 1h30, ou multiplos de 1h30.

3. **O saldo do dia sempre desconta o tempo ja rodado.** Ele informa quanto ja trabalhou (ex.: "pausei em 1h28m"). O saldo e `6h - tempo rodado`. Diga o horario de fim que sai da conta - nunca chute duracao.

4. **A escolha do ciclo e dele.** A `assistente-expert` calcula, registra e agenda. Ela nao decide quanto ele descansa. Se ele nao disser, pergunte.

5. **Descanso completo depois das 00h e sempre 7h30.** Nao proponha outra duracao.

---

## Ritual de pausa (4 passos)

**Passo 1 - Confirmar o ciclo**
Pergunte (ou confirme, se ele ja disse) qual intervalo de descanso vai ser aplicado e quanto tempo ele ja rodou no dia. Sem esses dois numeros nao da pra agendar.

**Passo 2 - Calcular o saldo**
`saldo = 6h - tempo ja rodado no dia`. O horario de retomada vem dele (ou do fim do descanso). O horario de fim e `retomada + saldo`. Apresente a conta explicita - ele confere.

**Passo 3 - Agendar a retomada no Google Calendar**
Crie o compromisso no calendario `primary` com:
- **Titulo:** `<bloco da agenda> - Retomada <nome da OP>` (ex.: `Gerir ativos - Retomada OP Loja`).
- **Horario:** inicio informado por ele, fim calculado pelo saldo.
- **Descricao:** o **conteudo do plano do dia da nota da OP** - meta, o que ele levanta sozinho, o operacional, o que esta travado com terceiros, avisos herdados de outros projetos e o nome da nota da OP. Objetiva, sem emoji, sem detalhe tecnico (Regras 11 e 13).
- **Lembrete:** popup 10 minutos antes.

Avise se o compromisso sobrepuser outro bloco da agenda - nao remova nem mexa nos blocos recorrentes dele por conta propria.

**Passo 4 - Registrar a pausa na nota da OP**
Na nota do dia (`Tarefas/<Mes>/OP <Nome>/OP <Nome> DD-MM-AA.md`), dentro do bloco "Trabalho de hoje", acrescente linha curta de pausa e retomada: horario da parada, tempo rodado, motivo (qual bloco da agenda e qual ciclo de descanso) e horario da retomada com o saldo. Nao reescreva o que ele escreveu.

---

## Horizonte declarado

O proposito dele e **automatizar a gestao da propria vida** com base nos objetivos, desejos e sonhos - e ele esta treinando a `assistente-expert` com o conhecimento da rotina dele pra isso. O norte e essa gestao rodar por **Telegram, WhatsApp ou app**, nao so no terminal. Todo conhecimento novo de rotina que ele passar deve ser gravado aqui (ou em playbook irmao), nunca so na conversa.
