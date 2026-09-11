# Playbook de Pareamento - casar duracao de audio e video

Validado na primeira rodada completa, num criativo real de cliente.
O que esta marcado como MEDIDO foi conferido com numero. O que esta marcado como
HIPOTESE funcionou uma vez e ainda nao foi testado num segundo material.

## A regra que rege tudo

**A fala e o produto. A imagem e material de cobertura.**

Quando a duracao do audio nao bate com a do video, quem se ajusta e sempre o
video. Cortar audio come palavra e nao tem volta; esticar, encolher ou dobrar
imagem e barato e reversivel.

Corolario pratico: o video de cada bloco deve terminar **igual ou depois** do
audio, nunca antes. Sobra de imagem no fim nao custa nada. Falta de imagem faz o
lip sync ficar sem material e a ultima palavra sai por cima de nada.

## Quando SOBRA video

Corte, nao acelere. Acelerar muda o ritmo do movimento e denuncia a montagem -
num alongamento lento, 30% de aceleracao vira gesto apressado, que e o oposto do
que o roteiro pede.

## Quando FALTA video

Duas saidas, nessa ordem de preferencia:

**1. Dobra vai-e-volta.** Toca o trecho pra frente e depois de tras. A emenda e
invisivel **por construcao**: o quadro que encosta e o mesmo quadro. Dobra o
tempo disponivel sem gerar nada novo.

> Exige trecho SEM gesto direcional. Mao subindo, virada de cabeca ou qualquer
> movimento com sentido fica errado invertido. Escolha o trecho medindo movimento
> quadro a quadro e pegando a janela com o menor pico, nao a olho.

**2. Desaceleracao com interpolacao de movimento.** So quando a dobra nao serve
(gesto direcional, ou o trecho e um clipe fechado tipo b-roll). Gera quadros
intermediarios em vez de repetir os existentes. Funciona bem em movimento lento e
continuo; em movimento rapido, distorce.

MEDIDO: desacelerar 1,33x um b-roll de alongamento ficou liso e natural.

## Diferenca de fracao de segundo

Clipe pronto que erra a fala por decimos (ex: video de 8,00s pra fala de 8,08s)
se resolve reajustando o tempo do video em 1%. Imperceptivel, e evita o lip sync
decepar a ultima palavra.

## Respiros e pausas

- Respiro padrao entre takes dentro de um bloco: **0,35s**.
- Pausa dramatica pedida no roteiro: entra como silencio no audio (ex: 0,80s
  antes do take de virada). **Nunca** como pontuacao dentro da frase, mexer na
  pontuacao muda o texto, e o texto do cliente e intocavel.
- Sobra de video no fim de cada bloco: **0,30s**. O lip sync apara sozinho.

## Protecao do fim do audio

Arredondamento de quadro deixa o video alguns centesimos mais curto que a fala.
Emendar com `-shortest` deceparia o fim da ultima palavra.

MEDIDO: numa emenda de b-roll, os 0,06s cortados tinham pico de -14 dB, som de
verdade, nao silencio.

Solucao: congelar o ultimo quadro e deixar o **audio** mandar na duracao.

## Armadilha de duracao em API

MEDIDO: o isolamento de voz do ElevenLabs tem teto de duracao (~176s observado) e
**devolve audio truncado sem erro nenhum**. Vale a regra geral:

> Toda API de audio que devolve arquivo tem a duracao conferida contra a de
> entrada antes do resultado ser usado. Diferenca acima da tolerancia aborta.

Para arquivo longo: fatiar, processar cada fatia, e **forcar cada resultado de
volta a duracao exata da fatia** antes de emendar. Sem isso a diferenca acumula e
o audio desanda em relacao ao video.

## Ordem de conferencia antes de mandar pro lip sync

1. Cada video de bloco tem duracao >= o audio do mesmo bloco
2. A dobra caiu em trecho sem gesto direcional
3. Nenhum arquivo de fala esta faltando
4. A soma dos blocos bate com o roteiro completo

Pareamento errado so aparece depois do lip sync, quando ja custou tempo de GPU.
