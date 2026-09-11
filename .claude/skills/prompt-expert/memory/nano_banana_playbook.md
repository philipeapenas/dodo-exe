# Nano Banana Pro - Playbook de Engenharia de Prompts JSON

**Versao:** 1.0 | **Data:** 10/07/2026 | **Owner do arquivo:** skill-expert (Regra 8) | **Operador:** prompt-expert

Fontes: guia oficial de prompting do Google Cloud (03/2026), guia Google AI dev.to (Nano-Banana Pro: Prompting Guide & Strategies), praticas da comunidade (JSON prompting para consistencia de personagem) e aprendizados internos validados em producao no pipeline do motion-expert (`prompts_reference.md`).

---

## 1. Como o Nano Banana Pro pensa (regras de ouro)

O Nano Banana Pro (Gemini 3 Pro Image) e um modelo "pensante": ele raciocina sobre intencao, fisica e composicao antes de gerar. As regras abaixo valem pra TODO prompt:

1. **Frases completas dentro de campos JSON.** Nada de sopa de tags ("mulher, praia, 4k, realista"). O JSON separa as preocupacoes (o que muda, o que fica, estilo, saida); DENTRO de cada campo, escreva frases descritivas completas, como se briefasse um artista humano.
2. **Ordens duras em INGLES.** Validado in-house: o modelo obedece melhor diretivas rigidas em ingles. Textos de paleta/descricao ambiental podem ir em PT, mas `core_directive`, preserve lists e negatives vao em EN.
3. **Positive framing.** Descreva o que voce QUER, nao o que nao quer ("empty street" em vez de "no cars"). Excecao: o campo `negatives`, que existe justamente pra listar armadilhas conhecidas.
4. **Edicao = mudar X, congelar o resto.** Em QUALQUER edicao, declare explicitamente o que muda E o que fica 100% identico (preserve list). O modelo faz mascara semantica por texto: nao precisa mascarar na mao, mas precisa ouvir "keep everything else exactly the same".
5. **Edit, don't re-roll.** Se o resultado saiu 80% certo, nao gere do zero: peca SO a correcao do defeito na mesma conversa do Flow. No JSON, ajuste apenas o campo responsavel (ver tabela de sintomas, secao 5).
6. **Controle de diretor.** Luz ("golden hour backlighting", "three-point softbox"), camera/lente ("low-angle, shallow depth of field f/1.8", "85mm portrait lens"), color grading ("shot on iPhone", "1980s film grain"), materialidade ("sheer black lace", "matte cotton"). Especificidade = qualidade.
7. **Contexto ajuda o modelo a decidir.** Dizer PRA QUE e a imagem ("for a premium Instagram lifestyle feed") faz o modelo inferir acabamento profissional.
8. **Referencias:** ate 14 imagens por prompt (6 com alta fidelidade de identidade). Identity locking explicito: "Keep the person's facial features exactly the same as Image 1". A paleta 9:16 da modelo (grid inteiro, sem recortar celula) e a referencia canonica de identidade - aprendizado do motion-expert.
9. **Resolucao e formato sao pedidos, nao sorte.** O modelo gera 1K/2K/4K nativamente e suporta 1:1, 2:3, 3:4, 4:5, 9:16, 16:9, 21:9 etc. Upscale so funciona bem se pedido explicitamente ("render at 4K resolution").
10. **Texto renderizado vai entre aspas** com fonte descrita ("bold white sans-serif"), se algum dia o prompt envolver texto na imagem.

---

## 2. Anatomia do JSON padrao Dodo

Esqueleto generalizado do padrao validado em producao (prompt mestre do faceswap). Todo prompt novo deriva daqui - campos irrelevantes pra categoria sao omitidos, nunca deixados vazios:

```json
{
  "task": "nome_da_operacao_em_snake_case",
  "model": "Modelo N (se houver identidade da empresa envolvida)",
  "core_directive": "One or two hard sentences in English stating the non-negotiable outcome.",
  "inputs": {
    "image_1": "what the attached image 1 is and what role it plays",
    "image_2": "same for image 2 (e.g. the 9:16 identity palette of the model)"
  },
  "edit": {
    "change": ["surgical list of what MUST change"],
    "how": "full-sentence description of the target state, positive framing"
  },
  "preserve": ["explicit list of everything that must stay 100% identical"],
  "model_signatures": "(so quando ha identidade) permanent traits of the model: face, lips, skin, hair, tattoos",
  "conflict_priority": "(quando ha 2 referencias) which image wins on conflict",
  "blending": "how the edit must merge photorealistically with the untouched area",
  "negatives": ["known failure modes to avoid for this category"],
  "output": {
    "description": "one sentence describing the final image",
    "resolution": "2K | 4K (se relevante)",
    "aspect_ratio": "9:16 (se relevante)"
  }
}
```

Regras do esqueleto:
- `task` + `core_directive` primeiro: o modelo le a intencao antes dos detalhes.
- `preserve` e tao importante quanto `edit.change`. Edicao sem preserve list = identidade derretida.
- `negatives` por categoria (secao 4), nao generico.
- JSON e a ESTRUTURA; o conteudo dos campos e frase completa, nunca tag.

---

## 3. Fluxo padrao de trabalho no Flow

1. Founder anexa a(s) imagem(ns) no Flow na ORDEM declarada em `inputs`.
2. Cola o JSON como mensagem.
3. Avalia o resultado com o checklist de QA (secao 5).
4. Defeito pontual -> corrigir na MESMA conversa com frase curta ("Keep everything, only fix X") ou reenviar o JSON com o campo ajustado.
5. 2 falhas seguidas do mesmo defeito -> trocar de estrategia (outra celula da paleta, simplificar o pedido em 2 passos: editar primeiro, upscale depois).

---

## 4. Receitas por categoria

### 4.1 Troca de identidade (vestir a modelo em foto avulsa)

**Quando usar:** foto/frame avulso FORA do pipeline diario. (Dentro do pipeline diario, o prompt travado e o `prompt_mestre.json` da modelo - ativo do motion-expert, nao recriar.)

**Receita:** derivar do padrao `portrait_identity_and_hair_transfer` validado:
- `inputs`: image_1 = foto alvo (cena/pose/corpo), image_2 = paleta 9:16 da modelo (ancora = celula frontal neutra).
- `core_directive`: "The output must be unmistakably the woman from image 2. Discard 100% of the face and hair of the person in image 1."
- `take_from_image_2`: rosto, cabelo, assinaturas permanentes (tatuagens renderizadas mesmo com corpo da image_1).
- `preserve` (da image_1): pose, expressao, olhar, luz, corpo, roupa, fundo, textos sobrepostos, aparencia de foto de celular.
- `conflict_priority`: image_2 SEMPRE vence em rosto/cabelo.
- `blending`: casar tom de pele na transicao rosto-pescoco, adaptar apenas a luz.
- `negatives`: no 50-50 morph, do not keep the original nose/lips/skin, do not thin the lips, do not omit tattoos, no 3D/cartoon look.
- **Pre-requisito:** modelo COM `_Base/paleta_ref.jpeg`. Sem paleta -> pausar e mandar cadastrar via motion-expert.

### 4.2 Edicao de corpo

- `task`: `body_reshape`.
- `edit.change`: nomear a regiao e a direcao da mudanca; `edit.how` descreve o ESTADO FINAL em linguagem natural e proporcional: "noticeably broader and more defined shoulders, proportional to the frame, natural muscle shape and shading".
- Roupa deve ACOMPANHAR a mudanca: "the clothing adapts naturally to the new shape, fabric tension and neckline follow the new volume".
- `preserve`: face and identity 100% identical, same pose, same skin tone and texture, same lighting, same background, same framing.
- `negatives`: no waist/hip change unless asked, no plastic/balloon look, no anatomy distortion, no warped background lines near the body, no identity drift, no change in skin texture.
- **QA especifico:** linhas retas do fundo perto do corpo (portas, azulejos) continuam retas? Maos/cotovelos intactos? Rosto identico?

### 4.3 Qualidade / upscale

- `task`: `photo_enhancement_upscale`.
- `core_directive`: "Reproduce this exact image at higher fidelity. This is a restoration, not a reinterpretation."
- `edit.how`: "render at 4K, recover fine skin texture with visible pores, individual hair strands, fabric weave, remove compression artifacts and noise".
- `preserve`: EVERYTHING - identity, pose, expression, framing, colors, lighting, background. Nada muda alem de nitidez/detalhe.
- `output.resolution`: "4K" (ou 2K). Pedir explicitamente, senao o modelo nao upscala.
- `negatives`: no plastic/airbrushed skin, no beauty-filter look, no face restructuring, no color shift, no added objects, no crop.
- **Dica validada da comunidade:** upscale rende mais como passo ISOLADO (editar primeiro, upscalar por ultimo).

### 4.4 Troca de roupa / cenario

- `task`: `outfit_swap` ou `scene_swap` (ou os dois, mas prefira 2 passos se o resultado derreter).
- Roupa: descrever com MATERIALIDADE ("a fitted ribbed knit mini dress in deep red, matte fabric") - tecido, caimento, cor exata, comprimento.
- Cenario: descrever o ambiente + reiluminar coerente: "relight the subject to match the new environment (warm indoor tungsten light)".
- `preserve`: identity, face, hair, body proportions, pose (a menos que pedido junto).
- `negatives`: no identity drift, no body reshape, no floating/disconnected shadows, clothing must respect body physics.

### 4.5 Pose / enquadramento

- `task`: `pose_change` ou `reframe`.
- Usar vocabulario de camera (regra de ouro 6): "low-angle medium shot", "3/4 body turned slightly left, chin down, eyes to camera".
- Identidade TRAVADA: anexar a paleta como referencia extra quando a mudanca de pose e grande (rosto vai ser re-renderizado) + `model_signatures`.
- `preserve`: identity, outfit, environment, lighting mood.
- `negatives`: no new accessories, no expression change unless asked, no anatomy errors in hands.
- **Aviso:** e a categoria de maior risco de identity drift. Mudancas grandes de angulo -> conferir QA de identidade com atencao redobrada.

### 4.6 Remocao de elementos

- `task`: `object_removal`.
- Nomear o elemento SEM ambiguidade ("the watermark text in the bottom-left corner", "the man in the background on the right").
- Instruir o preenchimento: "fill the space with logical textures that match the surrounding environment (tiles, wall, skin)".
- `preserve`: everything else pixel-faithful.
- `negatives`: no blur patch, no smudge, no leftover outline, do not alter adjacent areas.
- **Nota de fluxo:** remocao RECORRENTE de marca d'agua em lote de video e foto pede ferramenta deterministica (crop por script), nao prompt. Prompt e pro caso avulso em foto unica onde o crop nao serve.

---

## 5. QA e tabela sintoma -> campo

**Checklist apos cada geracao:**
1. Identidade: e inconfundivelmente a modelo? (comparar com a paleta)
2. Anatomia: maos, dentes, transicao rosto-pescoco, reflexos/espelhos.
3. Fundo: linhas retas continuam retas perto da area editada?
4. Luz: a area editada tem a MESMA luz do resto?
5. O que devia ficar identico ficou? (roupa, fundo, textos da imagem)

**Sintoma -> onde mexer no JSON:**

| Sintoma | Correcao |
|---|---|
| Rosto mudou / morph 50-50 | Reforcar `core_directive` + `conflict_priority`; ancorar na celula frontal da paleta; adicionar negative "do not blend faces" |
| Mudou coisa que nao pedi | Adicionar o item EXPLICITAMENTE ao `preserve` (o modelo so congela o que ouve) |
| Edicao ficou artificial/plastica | Reforcar `blending` + negatives de textura ("natural skin texture with pores") |
| Fundo distorceu perto da edicao | Negative "keep background lines straight and undistorted" + preserve do fundo |
| Resultado veio em baixa resolucao | `output.resolution` explicito ("4K") |
| Roupa nao acompanhou o corpo | Frase de adaptacao de tecido na `edit.how` (receita 4.2) |
| Texto/estampa da imagem corrompeu | Preserve explicito: "keep all overlaid text and prints exactly as they are" |

---

## 6. Divisao de escopo (lembrete)

- Prompts TRAVADOS do pipeline diario (paleta + prompt_mestre por modelo): ativos do `motion-expert`. Consultar `prompts_reference.md`, nunca duplicar/editar.
- Este playbook so e editado pelo `skill-expert` (Regra 8). Receita nova validada -> `help`/`upskill`.
