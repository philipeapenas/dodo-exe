# Senior Developer Playbook

## 1. Clean Code & SOLID Principles
- **Clarity over Cleverness:** Code should be readable. Good naming > comments.
- **Single Responsibility (SRP):** Functions and classes should do exactly one thing.
- **DRY (Don't Repeat Yourself):** Avoid redundant logic, but prefer slight duplication over the wrong abstraction.
- **YAGNI (You Aren't Gonna Need It):** Build for today's requirements, don't over-engineer for hypotheticals.

## 2. Defensive Programming
- **Graceful Degradation:** The code should never randomly crash. If an API is down or data is malformed, handle the exception and return a safe fallback or a graceful error.
- **Input Validation:** Treat all inputs, function arguments, and external data as hostile. Default to explicit typing/checks.
- **Null Safety:** Always handle `null`, `undefined`, or empty arrays before trying to map/filter or read properties.

## 3. Strict Self-Review Checklist
Before delivering code, you must statically analyze the modified files against these criteria:
- [ ] **Data Flow:** Are there orphan variables or unused imports?
- [ ] **Edge Cases:** Are boundaries handled? (e.g. empty lists, negative inputs, max values)
- [ ] **Error Path:** Is `catch` effectively logging and recovering?
- [ ] **Performance:** Does it loop exponentially (O(n^2)) unnecessarily?
- [ ] **Security:** Is it exposed to injection or leaking sensitive data?

### A exigencia antes de dizer que esta pronto (29/08/2026)

Travado pelo fundador depois de uma sessao em que a mesma familia de defeito
apareceu tres vezes. Nao e sugestao: e o que separa entregar de achar que
entregou.

- [ ] **Medi, ou estou supondo?** "Deve funcionar" nao e resultado. Se a mudanca
      tem numero (contraste, posicao, peso, tempo), o numero vai no relatorio.
- [ ] **Rodei as conferencias que o projeto ja tem** antes de mostrar. Elas
      existem porque alguem ja pagou o preco de nao ter.
- [ ] **A conferencia mede o que esta no ar hoje?** Ferramenta que assume posicao
      antiga reprova tela certa e aprova tela errada (secao 6).
- [ ] **Quando nao consegui medir, eu AVISEI** em vez de deixar passar.
      Conferencia que se cala quando falha e pior que conferencia nenhuma.
- [ ] **Parte da mudanca pegou e parte nao?** Entao e disputa de dono de
      propriedade, nao e gosto e nao adianta redesenhar. Ver
      `frontend-expert/memory/css_cascata_playbook.md` e o
      `movimento_playbook.md`.
- [ ] **Conferi por duas vias.** Print e medicao que discordam significam que
      nenhum dos dois esta provado (secao 8).
- [ ] **O commit leva so o que EU toquei** (secao 7).

## 4. Politica de Scripts Temporarios (scratch/)

Quando precisar criar um script de checagem/debug rapido durante uma sessao, voce tem 2 caminhos validos. Nao existe um terceiro.

**(a) Util com reuso obvio -> promover IMEDIATAMENTE a subcomando do CLI do projeto.**
- Adicionar como subcomando em `tools/cli.py` (ou CLI equivalente)
- Nome bom (verbo curto: `check-queue`, `count-failed`, `dump-session`)
- Documentar no README do projeto na secao CLI Reference
- NAO deixar como arquivo solto em `scratch/`

**(b) Throwaway de 5min para 1 bug pontual -> rodar inline e nao salvar.**
- Usar REPL Python (`python -c "..."`), one-liner shell, ou query SQL direta no console do Supabase
- Se foi necessario salvar em arquivo, DELETAR no fim do dia
- NAO acumular em `scratch/`

**Razao:** Scratch eterno vira cemiterio. Scripts esquecidos geram retrabalho, em 2 semanas ninguem lembra que existiam, refazem do zero. Numa limpeza real de projeto sobraram 7 scripts `check_*.py` que ninguem usava ha semanas.

**Como aplicar:** Default = promover (caminho a). Pular pra throwaway (caminho b) APENAS se o script for verdadeiramente unico (one-shot pra um bug que nao volta). Em caso de duvida, promover. Custa poucos minutos extras agora e economiza horas de retrabalho depois.

**Sinal de alerta:** Se voce esta criando o terceiro `check_*.py` da semana, pare. Os 3 deveriam ser subcomandos do CLI desde o primeiro.

---

## 5. Migration de Banco: escrever E APLICAR, sempre (26/08/2026)

**Escrever o `.sql` nao e entregar a migration. A dev-expert aplica ela, na mesma sessao, sem devolver isso como tarefa pro fundador.** Quando o banco e do proprio fundador, aplicar a migration faz parte da entrega.

**A razao e a posse:** quando o Supabase e self-hosted na VPS do fundador, o acesso por SSH existe. Nao e servico de terceiro onde falta permissao - o acesso existe. Deixar o `.sql` escrito e nao aplicado cria um estado pior que nao ter feito nada: o codigo novo ja espera a coluna, e quem publicar primeiro derruba a tela.

### O procedimento

```
scp <migration>.sql <usuario>@<ip-da-vps>:/tmp/
ssh <usuario>@<ip-da-vps> "docker cp /tmp/<arquivo>.sql supabase-db:/tmp/m.sql \
  && docker exec supabase-db psql -U supabase_admin -d postgres -v ON_ERROR_STOP=1 -f /tmp/m.sql"
```

Quatro coisas que nao sao opcionais:

1. **`-U supabase_admin`, nunca `postgres`.** No Supabase self-hosted o `postgres` nao e dono dos objetos e o DDL falha.
2. **`-v ON_ERROR_STOP=1`.** Sem isso o psql segue depois de um erro e a migration "termina" pela metade, com exit 0 mentindo que deu certo.
3. **Avisar a API pra reler o schema depois:** `NOTIFY pgrst, 'reload schema';`. Coluna nova fica **invisivel pro PostgREST** ate isso - a migration esta certa, o banco esta certo, e o painel jura que a coluna nao existe. Mordeu em 26/08/2026.
4. **Provar pelo caminho que a aplicacao usa**, nao pelo log do psql: um `curl` no endpoint REST com o `select` exato que o frontend faz. `ALTER TABLE` no log nao prova que a aplicacao enxerga (Regra: verificar resultado observavel).

### Migration idempotente por padrao

`ADD COLUMN IF NOT EXISTS`, e `DROP CONSTRAINT IF EXISTS` antes de `ADD CONSTRAINT` - senao rodar duas vezes quebra. O `NOTICE: constraint does not exist, skipping` na primeira execucao e esperado, nao e erro.

**Ordem de entrega quando a mudanca envolve schema:** aplicar a migration ANTES de publicar o frontend que le as colunas novas. O inverso deixa a tela vazia parecendo bug.

---

## 6. Ferramenta de auditoria envelhece com o layout (29/08/2026)

**Origem:** postmortem de um site de cliente. O projeto tinha `tools/audita_hero.py`, que media a faixa central da foto pra julgar se o texto do hero estava bem posto. Depois que o texto saiu do centro pra esquerda, a ferramenta passou a reprovar medindo o pedaco onde o texto nao esta mais.

O problema nao e a ferramenta estar errada. E ela estar **silenciosamente** errada: devolve reprovacao com cara de reprovacao legitima, e quem le acredita.

**Regra:** toda ferramenta de auditoria que le posicao fixa no layout (coordenada, faixa, recorte, offset em pixel) e uma suposicao congelada sobre o design. Quando uma mudanca move um elemento de lugar, confira se alguma auditoria assume a posicao antiga, e atualize ou aposente a ferramenta na mesma entrega.

**Sintoma:** auditoria que reprova uma tela que o olho aprova, ou aprova uma que o olho reprova. Nos dois casos, desconfie da ferramenta antes de desconfiar do layout.

**Extensao do principio:** vale pra qualquer verificador que codifique um estado do sistema em vez de consultar o estado real. Teste que fixa um id, script que assume ordem de coluna, health check que bate numa rota renomeada. Verificacao desatualizada e pior que verificacao ausente, porque ela mente com autoridade.

Familia direta do achado de CSS do mesmo dia, documentado em `frontend-expert/memory/css_cascata_playbook.md`: nos dois casos o codigo estava aparentemente certo e a realidade na tela era outra.

---

## 7. Commit cirurgico: `git add -A` varre o que nao e seu (29/08/2026)

**Falha real, cometida por mim.** Um commit cuja mensagem falava so de mover uma
nota de processo levou junto **297 linhas de codigo de outra sessao** - um
carrossel em profundidade que estava sendo construido em paralelo, no mesmo
repositorio, e ainda nao tinha sido commitado. Foi empurrado assim.

Nada se perdeu. O estrago foi outro, e e serio do mesmo jeito: **o historico
passou a mentir** (a mensagem nao descreve o conteudo) e o trabalho de outra
pessoa foi commitado antes de ela decidir commitar - talvez no meio de um passo.

### A regra

**Adicione por caminho, nunca `-A` nem `.`.**

```bash
git add caminho/do/arquivo.css caminho/do/arquivo.js
```

**Antes de commitar, sempre `git status`** e confira, item a item, se voce
reconhece cada arquivo listado. Arquivo que voce nao tocou nao entra.

### Quando aparecer arquivo que nao e seu

1. **Nao commite junto.**
2. **Nao reverta, nao apague, nao guarde em stash.** E trabalho real de alguem, e
   o working tree e compartilhado.
3. **Avise.** Diga o que apareceu e siga com o seu commit, so com os seus
   arquivos.

### Se ja foi empurrado

**Nao reescreva historico compartilhado.** Outra sessao pode estar com o
repositorio aberto agora, e reescrever quebra o estado dela. Reporte, explique o
que entrou e deixe a decisao com o fundador.

### Por que isso e mais provavel neste workspace

Duas sessoes trabalhando no mesmo projeto ao mesmo tempo e situacao normal aqui,
nao excecao. Ja tinha sido anotado antes, com outro sintoma: **o arquivo que voce
leu no comeco pode nao ser o que esta la no fim.** Antes de continuar um trabalho
que ficou parado alguns minutos, confira o estado real.

---

## 8. Navegador sem interface mente - saiba o que ele nao ve (29/08/2026)

Conferir por navegador sem interface e barato e util, mas **ele nao enxerga duas
coisas**, e acreditar nele custou horas nesta sessao: diagnostiquei defeito
inexistente duas vezes seguidas.

**1. Tempo virtual congela transicao e animacao.** Com `--virtual-time-budget`, o
valor computado de uma propriedade em transicao fica preso no estado ANTERIOR,
pra sempre. Voce le "nao mudou" e conclui que a regra nao pegou - quando ela
pegou e so nao terminou de animar.

**2. Ele tem largura minima de janela.** Pedir uma janela de celular no Windows
desenha num layout mais largo e so RECORTA o print. O corte que aparece e da
ferramenta, nao do site - parece estouro de layout que nao existe.

### Como conferir de verdade

| Quero saber | Como olhar |
|---|---|
| A regra casou? | Leia uma propriedade da mesma regra que **nao** esteja em transicao (`cursor`, `z-index`) |
| O valor final ficou certo? | Force o modo de menos movimento: a transicao vira instantanea e o computado passa a ser o final |
| A peca foi pro lugar? | Meca geometria (`getBoundingClientRect`), nao olhe o print |
| Como fica no celular? | **Nao da pra saber por aqui.** O portao e a tela real do fundador |

**E a regra que fecha:** duas vias sempre. Se a medicao e o print discordam,
nenhum dos dois esta provado ainda - procure a terceira leitura antes de mexer
no codigo.
