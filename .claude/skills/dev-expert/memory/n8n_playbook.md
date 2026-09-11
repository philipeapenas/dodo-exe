# Playbook de Fluxo n8n

**Versao:** 1.0 | **Data:** 25/08/2026 | **Owner:** dev-expert
**Origem:** os dois fluxos de um canal de links de cliente (ingestao e publicacao), reconstruidos varias vezes em dois dias. Todas as armadilhas abaixo foram PAGAS, nao lidas em documentacao.

## Regra zero: o fluxo se reconstroi do repositorio

Fluxo n8n nao se edita na tela e nao se versiona sozinho. No workspace ele nasce de um script (`build_wf.py`, `build_wf_ingestao.py`) que monta o JSON e sobe pela API. **A tela e leitura; o script e a fonte.** Editar direto na tela cria uma versao que o proximo `build` apaga sem avisar - e a ferramenta nao tem copia de seguranca.

## As cinco armadilhas

### 1. `$json` e a saida do no ANTERIOR, e ninguem avisa quando isso muda

Inserir um no no meio de um fluxo que ja funciona **muda em silencio o que `$json` significa** em todos os nos seguintes. Mordeu **duas vezes no mesmo dia**, nos dois fluxos.

```js
// FRAGIL - quebra no dia em que alguem inserir um no antes
const cab = $json?.headers;

// FIRME - le pelo NOME do no, que so muda se alguem renomear de proposito
const cab = $('Abrir o link curto').first().json?.headers || {};
```

**Antes de publicar qualquer fluxo em que voce inseriu um no:** `grep -n '\$json' build_wf*.py` e confira cada ocorrencia a jusante. Custa segundos; o prejuizo foi link curto quebrado e execucao morta com KeyError.

### 2. No que devolve ZERO linhas encerra o RAMO INTEIRO

Consulta sem resultado nao "passa vazio" - ela mata o que vem depois, sem erro e sem log util. Se o comportamento desejado e "segue mesmo sem achar", `alwaysOutputData: True` no no. **E o codigo seguinte tem que aguentar item vazio** - ligar a bandeira sem tratar o vazio so troca o sintoma.

### 3. Nome de instancia, grupo e horario sao CONFIGURACAO, nunca URL fixa

`sendText/<nome-da-instancia>` virou 404 no dia em que o numero foi trocado - e o fluxo ficou dando erro sem que nada no fluxo tivesse mudado. O que vier a mudar sem passar por deploy (instancia, destino, horario, codigo de afiliado) **le do banco e entra por expressao**. A regra pratica: se um humano pode mudar isso pela tela, nao pode estar escrito no fluxo.

### 4. Registre a recusa DENTRO da mesma consulta

Ramo separado so pra gravar "por que nao passou" e ramo que alguem esquece de ligar. Faca a propria consulta de decisao gravar o descarte:

```sql
with achado as (select nome from public.grupos where jid = $1 and ativo),
     registro as (insert into public.recusas (grupo_jid, motivo)
                  select $1, 'Veio de um grupo que nao esta na lista'
                  where not exists (select 1 from achado))
select nome from achado
```

Decisao e registro na mesma transacao: ou os dois acontecem, ou nenhum. Sem isso, **falha vira silencio** - e silencio nao da pra depurar depois.

### 5. Reconstruir o fluxo APAGA a credencial se a variavel nao estiver no ambiente

Mordeu no `build_wf.py` de um fluxo real. O script so anexa a
credencial do Postgres se achar `PG_CRED_ID` no ambiente:

```python
cred_id = os.environ.get("PG_CRED_ID")
if cred_id:
    for n in nodes:
        if n["type"] == "n8n-nodes-base.postgres":
            n["credentials"] = {"postgres": {"id": cred_id, "name": "Supabase"}}
```

Sem a variavel, o `PUT` sobe os nos **sem credencial nenhuma** e o script
imprime `fluxo atualizado` com toda a cara de sucesso. O erro so aparece
DEPOIS, na hora de ativar: *"Cannot publish workflow: 4 nodes have
configuration issues - Missing required credential: postgres"*. E se o fluxo
ja estivesse ativo, ele continuaria ativo e quebrando em execucao.

**Antes de rodar qualquer builder, pegue o id da credencial de um fluxo que
funciona** e passe na chamada:

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY"   https://<seu-n8n>/api/v1/workflows/<UM_QUE_FUNCIONA>   | grep -o '"postgres":{"id":"[^"]*"'

PG_CRED_ID=<id> python3 build_wf.py
```

E confira o que ficou no fluxo, nao o que o script imprimiu: baixe o fluxo
pela API e procure o trecho novo da consulta. `exit 0` aqui nao prova nada.

## Como testar sem esperar o relogio

Fluxo agendado nao se testa esperando a hora. O padrao e um script que **clona o fluxo pulando os nos de porteiro** (o gatilho de horario e o "e hora de publicar?"), roda o clone e apaga em seguida.

**A armadilha do proprio teste:** ao inserir um porteiro novo no fluxo, inclua-o na lista de pulados do script - senao o teste passa sem executar a parte que voce queria testar, e voce comemora um verde falso.

**E o teste que liga alguma coisa tem que ser desligado e DECLARADO** ao fechar (aviso herdado de um fluxo de teste que ficou ligado e postou uma semana inteira no grupo de um cliente).

## Relacionadas

* `senior_dev_playbook.md` - o criterio de codigo, que continua valendo aqui.
* **Regra de Ouro 7** - simplicidade e cirurgia; um fluxo remontado inteiro nao e desculpa pra redesenhar o que ja funcionava.
