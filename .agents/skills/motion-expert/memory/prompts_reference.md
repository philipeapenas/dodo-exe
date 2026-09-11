# Prompts de Referencia

Dois prompts JSON sustentam o pipeline. Regra de idioma: **paleta em PT** (gera bem), **faceswap em INGLES** (Nano Banana responde melhor a ordem dura em ingles).

## 1. Geracao da paleta de referencia (PT) - usado so no cadastro da modelo

Objetivo: a partir de UMA foto da modelo, gerar uma folha de referencia (contact sheet) 9:16 multi-angulo, identidade identica em todas as celulas. Salvar como `_Base/paleta_ref.jpeg`.

Chaves principais: `task: identity_reference_sheet`, `source_image` (unica fonte de verdade), `identity_lock.manter_identico` (estrutura ossea, olhos, sobrancelhas, nariz, labios, pele, marcas, cabelo, etnia/idade), `layout` (grade, fundo neutro, luz uniforme), `angulos` (frontal, 3/4, perfis, inclinacoes), `expressoes` (neutra, sorrisos, boca falando, olhos fechados), `negativos` (sem texto, sem mudar identidade entre celulas, sem cartoon/3d).

Aprendizado: **9:16 deu melhor identidade**; o grid inteiro serve direto como referencia no faceswap (nao recortar celula).

## 2. Faceswap / transferencia de identidade + cabelo (EN) - usado todo dia

Objetivo: `task: portrait_identity_and_hair_transfer`. Substituir a cabeca da pessoa da Imagem A (frame) pela modelo da Imagem B (paleta), mantendo de A apenas pose, expressao, luz, corpo, roupa, fundo. **Cabelo vem de B.**

Estrutura do objeto:
- `model` (ex: "Modelo 1")
- `core_directive`: ordem dura, o resultado TEM que ser inconfundivelmente a modelo de B; descartar 100% o rosto e o cabelo de A.
- `inputs.image_A_video_frame` / `inputs.image_B_reference` (paleta; usar celula frontal neutra como ancora).
- `model_signatures`: **as assinaturas permanentes da modelo** (face, lips, skin, hair, tattoo). E o que reduz repeticoes e garante tracos que sem instrucao explicita o modelo omite.
- `take_from_B_identity`: lista do que vem de B (incluindo cabelo e tatuagem renderizada no peito mesmo o corpo vindo de A).
- `keep_from_A_scene`: pose, olhar, expressao, luz, corpo, roupa, fundo, textos sobrepostos, aparencia de foto de celular.
- `conflict_priority`: em conflito de rosto/cabelo, B sempre vence.
- `blending`: encaixe fotorrealista, casar pele na transicao rosto-pescoco, so adaptar a luz.
- `negatives`: nao parecer A, sem morph 50-50, nao manter pele/nariz/labios de A, nao afinar labios, nao omitir a tatuagem, sem 3d/cartoon.
- `output`: a modelo na cena/pose/luz exatas de A.

O JSON travado de cada modelo vive em `Modelos/<Modelo>/Processos/Motion Control/_Base/prompt_mestre.json`. Cada modelo nova = um `prompt_mestre.json` proprio com `model_signatures` dela (ver `model_profile_spec.md`).

## Por que prompt travado por modelo

A modelo e usada em escala. Travar `model_signatures` em texto (alem da imagem de ref) ancora a identidade, garante assinaturas (tatuagem, formato dos labios, cor do cabelo) e corta as repeticoes ate "ficar boa". Pras outras modelos, so troca o bloco `model_signatures`.
