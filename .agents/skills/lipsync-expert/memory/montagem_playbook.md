# Playbook de Montagem - conformar as pecas e gerar a legenda

Validado em 13/08/2026. O entregavel desta skill nao e um video "quase certo":
sao pecas que encaixam na edicao sem ajuste nenhum.

## A regra dos 25 fps

**Conforme tudo em 25 fps, porque e a taxa que o LatentSync devolve.**

Nao e escolha estetica. Adotando a taxa que ele ja entrega, as pecas com lip sync
- que sao a maior parte do tempo de tela, passam **sem reamostragem**. Só os
clipes de outra origem se ajustam, e eles sao a minoria.

Escolher 30 fps faria o caminho contrario: remexeria o material principal pra
acomodar o secundario, com perda em cima do que mais importa.

Clipe de origem diferente (Veo costuma sair em 24 fps) se ajusta por
**desaceleracao**, nao por duplicacao de quadro, quando ha folga de tempo -
desaceleracao e continua, duplicacao da tranco.

## Resolucao

Unifique tudo num alvo unico. As origens tem tamanhos diferentes (clipe do Veo em
720x1280, saida do motion control em 544x960), e a unificacao acontece de
qualquer jeito. Fazer isso uma vez aqui, no alvo final, evita que o editor de
video faca de novo depois.

Padrao usado: **1080x1920** com escala lanczos e letterbox preservando proporcao.

> A nitidez real vem da origem, nao da conformacao. Subir a resolucao nao inventa
> detalhe, so evita reamostragem dupla na edicao.

## A legenda: alinhamento forcado, nao transcricao

Nao transcreva o video montado. Use o **alinhamento forcado** do ElevenLabs em
cima do mp3 de cada take, junto com o texto que voce ja sabe que esta ali. Ele
devolve o tempo exato de cada palavra.

Vantagens sobre transcrever: nao regera audio, nao chuta palavra, custa quase
nada, e acerta sigla e nome proprio que reconhecimento automatico erra.

MEDIDO: alinhar 14 takes custou 47 caracteres de cota.

### Agrupamento das cartelas

- 3 a 4 palavras por cartela, no maximo ~1,9s
- **Quebre na pontuacao**, nao no meio da frase, cartela terminando em virgula
  ou ponto le muito melhor
- Guarde uma lista de abreviacoes (`dr`, `mr`, `st`...): ponto de abreviacao nao
  e fim de frase e nao pode quebrar cartela

### O erro que ja aconteceu

**Calcule o inicio de cada bloco pela duracao REAL da peca montada, nunca pela
planejada.** Duas coisas fazem o planejado divergir: o lip sync apara o video no
fim da fala, e a emenda dos blocos pode nao ter o respiro que voce previu.

MEDIDO: usar o tempo planejado atrasou a legenda quase 1 segundo no fim do video.

Por isso a ordem e: montar as pecas PRIMEIRO, gerar a legenda DEPOIS.

## Fonte unica de verdade

A ordem dos takes, os respiros e as pausas vivem num lugar so, e o **mesmo dado**
gera o audio e a legenda. Assim e impossivel a legenda sair fora de sincronia com
a voz, mudou um respiro, os dois mudam juntos.

## Entrega

Entregue as duas coisas:

1. **As pecas conformadas**, uma por trecho, com a duracao e o ponto de entrada
   de cada uma anotados.
2. **O video completo emendado**, pra quem quiser comecar de algo pronto.

Mais o SRT, que o CapCut importa direto.

A edicao criativa, ritmo, zoom, enfase, estilo de legenda, e do fundador. Esta
skill entrega material tecnicamente correto, nao material editado.
