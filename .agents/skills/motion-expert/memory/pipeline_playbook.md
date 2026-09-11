# Pipeline Playbook - Faceswap + Motion Control

Processo deterministico para vestir a modelo da empresa (persona fixa) em cima de um reel de referencia, preservando o movimento original. Validado em producao real.

## As 5 etapas

1. **Video original** -> curadoria manual do fundador. Ao escolher o video do dia, criar `Repertorio/<perfil>/<DD MM AA>/` e MOVER o video pra la (mantem organizacao).
2. **Extrair frame (~1s)** de cada video -> `FaceSwap/Material/<dia>/1_Frames/`. Script: `tools/extract_frames.py`. Frame em ~1s (t=0 arrisca quadro preto/transicao). Nome do PNG = nome do video.
3. **Faceswap** = colocar a identidade da modelo no frame. Usa `_Base/prompt_mestre.json` + `_Base/paleta_ref.jpeg` + o frame. Saida em `2_Swaps/`; aprovado em `3_Pronto/`. Ferramenta: Flow (Nano Banana Pro) no modo GUIA, ou API Gemini no modo AUTO.
4. **Motion Control** = animar o swap seguindo o movimento do video. Inputs (video original + swap aprovado) sao copiados para `1_Input/` (via `--stage` do script). Saida em `2_Final/`. Ferramenta: RunningHub (workflow Wan 2.2 Animate), manual (GUIA) ou API (AUTO). Ver `runninghub_workflow.md`.
5. (Entrega) O video final em `2_Final/` e o produto.

> NOTA (29/06/2026): a regra "2_Final e o produto" esta SUPERADA. Hoje o `2_Final` e materia-prima para os estagios 6-8 abaixo; o entregavel real e o `5_Final/`. Veja a secao "Pos-Motion".

## Pos-Motion: Voz, Lip-sync e Som Ambiente (validado 29/06/2026)

O `2_Final` tem rosto e movimento certos, mas AUDIO ERRADO (voz da pessoa de referencia) e a MARCA D'AGUA da RunningHub no canto. A cadeia segue por mais 3 estagios ate o entregavel em `5_Final/`.

### Estagio 6 - Voz da modelo (skill voice-expert)
Ferramentas em `.agents/skills/voice-expert/tools/`:
- `extract_audio.py` (video -> wav mono 44100)
- `transcribe_video.py` (ElevenLabs Scribe STT; gera `<nome>_copy.md` numa pasta `3_Voz/` irma da `2_Final/`; modo lote na pasta do dia)
- `generate_voice.py` (ElevenLabs TTS; modo `--doc` le a secao `## Copy` do _copy.md e gera 1 mp3)

Fluxo: `transcribe_video.py <pasta 2_Final>` -> REVISAO HUMANA da copy (GATE obrigatorio: STT erra giria PT-BR) -> a secao `## Copy v3` carrega as tags de expressao v3 (audio tags tipo [playful]/[sarcastic]/[mischievously], abordagem hibrida Scribe + IA, analisadas do video de origem) -> gerar a voz.

Config de voz: ElevenLabs modelo `eleven_v3` com stability 0.0 (Creative) deu o melhor tom nos testes. So trave a config no `secrets.local.json` depois que o fundador aprovar o resultado.

Saida: `3_Voz/<nome>_voz_v3.mp3`. Secrets (api key + voice_id) em `voice-expert/tools/secrets.local.json` (gitignored).

### Estagio 7 - Lip-sync (LatentSync)
Reaproveita o video do `2_Final` (rosto+movimento certos, boca errada) + a voz do `3_Voz`, e regenera SO a boca pra bater com a fala (condicionado no audio). Saida: `4_LipSync/<nome>_lipsync.mp4`. DOIS caminhos validados:

- **RunningHub** (workflow LatentSync ja existe na plataforma): caminho de PRODUCAO (mesmo padrao de integracao do `runninghub_run.py`).
- **Google Colab GRATIS** (custo zero): notebook do LatentSync numa copia sua, em `.../Motion Control/LatentSync_Colab.ipynb`. Usa LatentSync 1.5 (8 GB VRAM, cabe na T4 gratis; a 1.6 precisa 18 GB e NAO roda). Gotchas ja resolvidos no notebook: (1) relax do pin mediapipe, (2) upgrade do accelerate (erro clear_device_cache), (3) huggingface_hub<1.0, (4) copiar arquivos pra pasta local SEM espacos (LatentSync quebra com espaco no caminho).

AVISO: Colab e HuggingFace publico tem politica de conteudo. Material que a politica deles nao aceita = risco de ban na conta; nesse caso, RunningHub.

### Estagio 8 - Edicao final: crop da marca d'agua + som ambiente
Duas operacoes sobre o video do `4_LipSync`, gerando o entregavel em `5_Final/`:

1. **Crop da marca d'agua RunningHub** (canto superior): dar zoom suficiente pra CORTAR a marca e reescalar pra dimensao original (9:16). O crop re-encoda o video (nao pode usar `-c:v copy`). Recipe de referencia (ajustar % e offset a posicao/tamanho real da marca): `-vf "crop=iw:ih*0.92:0:ih*0.08,scale=720:1280"` (corta ~8% do topo e reescala).
2. **Som ambiente**: mixar o ruido de ventilador em volume baixo (~0.15, ajustavel) SOB a voz da modelo, com `amix normalize=0` (a voz nao cai pela metade) + `-stream_loop -1` no fundo (loopa se o video for mais longo). O som ambiente e UNIVERSAL: `<raiz da producao>/_Recursos/Fundo/ventilador.m4a` (~15s, vale pra todas as modelos; trocar esse arquivo troca o som de todas).

STATUS: AUTOMATIZADO. As duas operacoes viram um unico comando ffmpeg (crop preserva o 9:16 - corta topo + recorta largura proporcional + reescala, sem distorcer). Implementacoes: (a) `tools/finalize_video.py` (local, com `--fundo/--vol/--crop-top`, modo lote); (b) a MESMA logica embutida no notebook Colab (estagio 7), que faz lip-sync + edicao final num run so e entrega direto no `5_Final/`.

> LIMPAR SO A MARCA (motion cru): quando o fluxo PARA no motion cru (`Conta N/output`) pra validacao, use `finalize_video.py "<Conta N/output>" --crop-only` pra tirar SO a marca do topo (mesmo crop 9:16, sem som ambiente/voz, mantendo o audio original). Saida em `_limpo/` (nao destrutivo). Ajuste `--crop-top` se 0.08 nao cobrir a marca. Nao rode o modo completo depois no mesmo arquivo (cropou 2x); o `--crop-only` e uma saida alternativa pro cru, nao um estagio antes do 6-8.

> AO FECHAR O MOTION - CROP AUTOMATICO, CAIXINHA COM CONFIRMACAO: o crop da marca d'agua (`--crop-only`) roda SEMPRE no automatico, sem perguntar (operacao mecanica, sem variacao). Ja a caixinha de pergunta (`question_box/box_overlay.py`) SO depois do fundador confirmar os textos, decisao editorial, texto errado queima o post. Os textos saem VERBATIM da nota "Reels da semana" do vault. Depois: `organizar_reels.py --src-dia <dia>` copia a versao final de cada conta (caixinha > limpo) pro `Material/Reels/Limpos/<Mes>/<hoje>/Conta N`.

### Cadeia completa
```
1 video original -> 2 frame -> 3 faceswap -> 4 motion control       -> 2_Final/
-> 6 voz (voice-expert: transcricao + GATE + voz v3)                -> 3_Voz/
-> 7 lip-sync (LatentSync: RunningHub OU Colab gratis)             -> 4_LipSync/
-> 8 edicao final (crop marca d'agua + som ambiente)              -> 5_Final/ [ENTREGAVEL]
```

## Estrutura de pastas (por modelo)

Base: `Modelos/<Modelo>/Processos/Ativos/Instagram/Skills/Motion Control/`. FaceSwap e Motion ganharam nivel de MES (`Material/<Mes>/<dia>/`); o Repertorio NAO tem mes.

```
_Base/                              (PERMANENTE, reaproveita todo dia)
  prompt_mestre.json
  paleta_ref.jpeg
FaceSwap/Material/<Mes>/<DD MM AA>/ (por dia)
  1_Frames/    (prints ~1s = Imagem A)
  2_Swaps/     (saida do faceswap)
  3_Pronto/    (swaps aprovados)
Motion/Material/<Mes>/<DD MM AA>/   (por dia)
  1_Input/     (video original + swap aprovado)
  2_Final/     (saida do motion control: rosto+movimento ok, audio errado)
  3_Voz/       (voice-expert: <nome>_copy.md + <nome>_voz_v3.mp3)
  4_LipSync/   (LatentSync: boca batendo com a voz)
  5_Final/     (mix com som ambiente = ENTREGAVEL)
```

> MULTI-CONTA (dia com varias contas ativas): dentro do dia entra uma subpasta por conta. Swaps aprovados em `FaceSwap/Material/<Mes>/<dia>/Conta N/output/` (o `runninghub_run.py` tambem le a pasta agrupada `.../output/Contas X-Y/`: ver `runninghub_workflow.md`) e saida do motion em `Motion/Material/<Mes>/<dia>/Conta N/output/`. Cada conta tem seu @ de repertorio (video original) em `<raiz da producao>/Repertorio/<@>/<dia>/` (SEM mes). O `runninghub_run.py --manifest` (campo `mes`) roda todas as contas em paralelo.

> Som ambiente NAO e por modelo: vive UNIVERSAL em `<raiz da producao>/_Recursos/Fundo/ventilador.m4a` (vale pra todas). A pasta `Voz/Fundo/` por-modelo e legado.

## Modos de operacao

- **GUIA (sem API key):** a skill prepara tudo (frames, pastas, serve prompt+paleta+config) e instrui o fundador a executar o passo manual no Flow e no RunningHub.
- **AUTO (com API key no ambiente):** a skill roda `faceswap_gen.py` (Etapa 3) e `runninghub_run.py` (Etapa 4). `GEMINI_API_KEY` liga a Etapa 3; `RUNNINGHUB_API_KEY` liga a Etapa 4. Cada etapa decide o modo de forma independente.

## Gate de qualidade (inegociavel)

O faceswap generativo tem variancia: as vezes sai ruim mesmo com prompt travado. Por isso a Etapa 3 SEMPRE passa por aprovacao humana:
- Modo AUTO gera **N candidatos** por frame em `2_Swaps/`.
- O fundador escolhe o melhor e move para `3_Pronto/`.
- So o que esta em `3_Pronto/` entra no motion control.

A Etapa 4 (motion) nao tem gate: seed fixa = resultado reproduzivel, sem variancia subjetiva.

## Decisoes validadas (regras do processo)

- **Frame em ~1s**, nunca t=0.
- **Cabelo = SEMPRE o da modelo de referencia** (persona fixa; cabelo do video quebra a identidade da marca).
- **Paleta 9:16** deu a melhor identidade; o grid de 9 celulas funciona direto como referencia (nao precisa recortar uma celula).
- **Prompt especifico por modelo** (bloco `model_signatures`) reduz repeticoes e garante assinaturas (ex: tatuagem que sem instrucao explicita nao sai).
- **Determinismo** = frame em timestamp fixo + seed fixa no RunningHub + prompt travado.
