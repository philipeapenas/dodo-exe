# RunningHub - Workflow Motion Control (Wan 2.2 Animate)

Workflow ComfyUI hospedado no RunningHub que anima uma imagem de referencia (o faceswap) seguindo a pose+face de um video (o original). E o motor da Etapa 4.

URL do workflow publico de referencia: https://www.runninghub.ai/workflow/2071367983410278402
O mapa de nos abaixo saiu do export `_api.json` desse workflow (payload de automacao). O export em si nao vem no pacote: baixe do RunningHub logado na sua conta.

## Nos que importam (do _api.json)

| No | Titulo | Funcao | Onde mexer |
|---|---|---|---|
| 391 | CARREGAR IMAGEM DE REFERENCIA | LoadImage | injetar o **swap aprovado** (`3_Pronto/`) |
| 392 | Load Video (Upload) | VHS_LoadVideo | injetar o **video original** |
| 341 | DURACAO DO VIDEO | Int | **duracao em segundos** = comprimento do clipe (arredondar pra cima) |
| 349 | FRAME RATE (FPS) | Int | fps de saida (default 30) |
| 374 | TAMANHO MAIOR (960 = rapido) | Int | lado maior em px (960 = rapido) |
| 335 | WanVideo Sampler | seed | **seed fixa = determinismo** (mudar a seed muda o resultado) |
| 326 | Video Combine | saida | de onde sai o mp4 final |

Formula de frames carregados: `no341 (duracao) x no349 (fps) + 1`. Ex: 14s x 30 + 1 = 421 frames.

Modelo usado: Wan2.2-Animate-14B (pose + face driven). Prompt positivo embutido (no 336): "Manter expressoes faciais e posicao da cabeca consistentes, aprimorar realismo."

## Contrato da API (para o dev-expert implementar runninghub_run.py)

Doc oficial: https://www.runninghub.ai/runninghub-api-doc-en (ver "Full Workflow Integration Example", doc-8287472).

Fluxo confirmado na pesquisa (28/06/2026):
1. **Upload** dos arquivos (imagem + video) -> a API retorna um identificador de arquivo.
2. **Run task** enviando o workflow + um `nodeInfoList`: lista de `{ nodeId, fieldName, fieldValue }` que sobrescreve campos dos nos. E assim que se injeta:
   - no 391 -> campo `image` = arquivo do swap
   - no 392 -> campo `video` = arquivo do video original
   - no 341 -> campo `value` = duracao em segundos
   - no 335 -> campo `seed` = seed fixa (determinismo)
3. **Poll** do status da task ate concluir.
4. **Get result** -> baixar o mp4 (do no 326) para `2_Final/`.

Requer pelo menos uma conta com `api_key` + `workflow_id` em `secrets.local.json` (ver secao de contas ativas abaixo). Sem conta configurada -> modo GUIA (config manual no editor web).

> Os endpoints exatos (URLs, headers, shape do payload) o dev-expert confirma direto na doc oficial acima ao implementar. Esta pagina e a referencia de DESIGN, nao o codigo final.

## Pool de keys, contas ativas e fan-out paralelo

O fundador tem VARIAS contas RunningHub. **Limite atual: 1 video/dia por API key.** Por isso cada **conta ativa** (persona/@ do Instagram) recebe **2 keys = 2 videos/dia**, e o motion control roda TODAS as contas EM PARALELO (nao e mais serial com failover).

**Restricao confirmada na doc (doc-8287463):** a API NAO roda workflow publico/compartilhado. O workflow precisa **existir em cada conta**, e **cada conta gera um workflowId proprio**. Nao ha endpoint confiavel para importar workflow via API.

**Setup unico por conta (manual, ~1 min):** abrir o workflow logado na conta -> "copiar pros meus workflows" -> pegar o `workflow_id` na URL -> colar em `secrets.local.json`.

`tools/secrets.local.json` (gitignored, `*.local.json`, NUNCA commitar; template em `secrets.example.json`). Dois formatos aceitos:
- **Explicito (recomendado)** - mapeia cada conta ativa pras suas 2 keys:
  ```json
  { "runninghub_active_accounts": [
      { "conta": "Conta 1", "keys": [ {"api_key":"...","workflow_id":"..."}, {"api_key":"...","workflow_id":"..."} ] }
  ] }
  ```
- **Plano (legado/fallback)** - lista simples; o script auto-pareia 2-a-2 nas contas do manifest, na ordem:
  ```json
  { "runninghub_accounts": [ { "api_key": "...", "workflow_id": "..." } ] }
  ```

### Modo LOTE (fan-out paralelo) - principal
`runninghub_run.py --manifest lote.json` monta os jobs do dia e dispara em paralelo (1 thread por job, `ThreadPoolExecutor`). O manifest so diz o @ do repertorio de cada conta; o script DESCOBRE os swaps na pasta do dia, PAREIA cada swap por NOME com o video em `Repertorio/<@>/`, e le a duracao via `ffprobe`. Manifest:
```json
{ "motion_control_root": "...\\Processos\\Ativos\\Instagram\\Skills\\Motion Control",
  "repertorio_root": "<raiz da producao>\\Repertorio",
  "mes": "Julho", "dia": "13 07 26", "seed": 514990883467325,
  "contas": [ { "conta": "Conta 1", "repertorio": "<@ do perfil de referencia>" } ] }
```

**Layout do Drive:** a raiz do Motion Control e `<Modelo>/Processos/Ativos/Instagram/Skills/Motion Control`. FaceSwap e Motion ganharam nivel de MES: `Material/<Mes>/<DD MM AA>/`. O Repertorio NAO tem mes (`Repertorio/<@>/<DD MM AA>/`). Por isso o manifest tem o campo OPCIONAL `mes` (presente -> FaceSwap+Motion usam `Material/<mes>/<dia>`; ausente -> layout antigo sem mes, retrocompativel).

**Descoberta de swap (o script resolve sozinho, nesta ordem):** o fundador organiza os swaps de 3 jeitos; a primeira pasta que existir e tiver arquivo vence:
1. `<dia>/Conta N/output/`         (uma pasta por conta)
2. `<dia>/output/Conta N/`         (pasta individual dentro do output agrupado)
3. `<dia>/output/Contas X-Y/`      (pasta AGRUPADA, ex "Contas 2-4"; filtra so os arquivos cujo nome comeca pelo NUMERO da conta -> Conta 3 pega `3.jpeg`/`3a.jpeg`, ignora `2.jpeg`/`4.jpeg`).

O preview imprime a origem de cada swap (ex: `swap de: output/Contas 2-4`) pro fundador conferir. NAO precisa mais copiar swap na mao pra pasta individual.

**Seguranca de cota (1 video/key/dia que COMPLETA):**
1. **PREVIEW por default:** sem `--fire`, o script so imprime o plano (conta, swap -> video pareado, duracao, key mascarada, saida) SEM chamar a API. Gate obrigatorio: pareamento errado queima a cota do dia. Disparo real = `--fire`.
2. **Pula job ja pronto:** se o mp4 de saida ja existe no `2_Final` da conta, pula (nao re-renderiza). Force com `--overwrite`.
3. **Reserva de key so com folga:** se a conta tem mais keys que jobs (ex: 1 video restante, 2 keys), um job que der 414 (cota gasta) / 810 (workflow) cai na key reserva DA PROPRIA conta. Com 2 jobs / 2 keys nao ha reserva (1 por key). NAO ha rotacao entre contas.
4. **421 (fila cheia) e FAILED (OOM) sao transitorios e NAO queimam cota:**
   - **421** (fila da key cheia): espera e retry na MESMA key.
   - **FAILED**: a task morreu na GPU do RunningHub (tipicamente `torch.OutOfMemoryError` nos nos `WanVideoSampler` / `WanVideoTextEncodeCached`), NAO por cota. Medido em 13/07/26: apos 2 FAILED, o `/uc/openapi/accountStatus` das keys mostrava `remainCoins: 100`, `currentTaskCounts: 0` (saldo intacto). Re-disparar na mesma key resolveu. **A regra "1 video/key/dia" so vale para render que COMPLETA.**
   - O `runninghub_run.py` ja re-tenta FAILED automaticamente na mesma key (ate 4 tentativas, esperas 30/60/120s -> const. `FAILED_RETRY_WAITS_S`) e loga o motivo real, extraido do `/task/openapi/outputs` do taskId falhado (retorna `code 805` + `data.failedReason.exception_type` / `node_name`).

Saida cai no `2_Final` de cada conta. O motion PARA no cru (2_Final); voz/lip-sync/edicao final sao estagios 6-8 separados.

### Modo SINGLE (compat)
`runninghub_run.py --image <swap> --video <original> --output <2_Final> [--duration N]` roda 1 par com rotacao entre as contas planas (comportamento legado). Sem `--duration`, usa `ffprobe`.

`gemini_api_key` no mesmo arquivo fica reservado para quando/se a Etapa 3 for automatizada (hoje a recomendacao e manter o faceswap manual no Flow, que e gratis).
