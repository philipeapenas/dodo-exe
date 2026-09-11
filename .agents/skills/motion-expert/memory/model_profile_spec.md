# Cadastro de Modelo (montar o _Base/)

Toda modelo tem assets PERMANENTES que vivem em `Modelos/<Modelo>/Processos/Motion Control/_Base/` e sao reaproveitados em todo processo diario. Cadastrar uma modelo = montar esse `_Base/`.

## Conteudo do _Base/

1. **`paleta_ref.jpeg`** - folha de referencia 9:16 multi-angulo da modelo. Gerada a partir de UMA foto boa da modelo (pasta `Material` da modelo) com o prompt de paleta (ver `prompts_reference.md`, item 1) no Flow/Nano Banana. Escolher a versao com melhor identidade.
2. **`prompt_mestre.json`** - o prompt de faceswap travado da modelo (`task: portrait_identity_and_hair_transfer`), com o bloco `model_signatures` preenchido com as assinaturas dela.

## Como preencher model_signatures

Descreva em texto (ingles) os tracos PERMANENTES da modelo, observando a paleta:
- `face`: estrutura (ex: high cheekbones, defined jaw, almond eyes)
- `lips`: ex: naturally full lips, never thinned
- `skin`: tom + subtom (ex: warm light-brown skin, neutral undertone)
- `hair`: cor, textura, comprimento, estilo (ex: voluminous shoulder-length blonde curly/afro hair, darker roots)
- `tattoo` / marcas: posicao + descricao (ex: small outlined star tattoo on the upper chest, below the collarbone)

Quanto mais especifica a assinatura, menos repeticoes ate o swap "ficar bom".

## Passos do cadastro

1. Receber/localizar a foto-ancora da modelo (pasta `Material` dela). Em caso de duvida de qual foto, **perguntar ao fundador** (nao cacar).
2. Gerar a paleta com o prompt de paleta -> validar identidade -> salvar `_Base/paleta_ref.jpeg`.
3. Escrever `_Base/prompt_mestre.json` com `model_signatures` da modelo.
4. Garantir as pastas `FaceSwap/Material/` e `Motion/Material/`.
