# Playbook de Execucao - rodar o lip sync

Estado em 13/08/2026. Este arquivo tem duas partes: como se roda HOJE, e o mapa
pra sair da dependencia do Colab.

## Hoje: LatentSync no Colab (gratis)

Notebook: uma copia do notebook do LatentSync no Drive do fundador, com os
consertos ja dobrados pra dentro das celulas certas.

> Mantenha UM notebook so. Duas copias com nome parecido (uma arrumada e uma
> antiga com celulas de conserto soltas fora de ordem) ja fizeram a execucao
> rodar na versao errada. Ao achar duas, confirme com o fundador qual e a boa.

**Este passo EXIGE o fundador.** Colab e caderno interativo no navegador, sem
API. A skill prepara os pares e entrega a celula pronta; quem aperta o botao e
ele. Nunca finja que consegue rodar sozinho.

Sequencia que ele executa: ligar GPU T4, rodar as quatro primeiras celulas de
codigo (conferir GPU, instalar, baixar checkpoints, montar o Drive), pular as
celulas que apontam pro pipeline das modelos, criar celula nova e colar o
`tools/celula_colab.py`.

### Armadilhas conhecidas

- **Caminho com espaco quebra o LatentSync.** A celula copia tudo pra
  `/content/job` antes de processar e devolve o resultado pro Drive no fim.
  Caminho de cliente quase sempre tem espaco no nome de alguma pasta.
- **Salva cada bloco assim que termina**, nao no fim de tudo. Sessao gratuita cai
  e o que ja concluiu tem que sobreviver.
- **Pula bloco que ja existe** na pasta de saida, pra retomada nao refazer tudo.
- **Sessao morre** se a aba fechar ou o PC dormir. Colab grátis tambem derruba
  apos ~90 min sem interacao na pagina.
- Tempo de referencia: ~10 min de instalacao e 20 a 40 min pra ~70s de video.

### O que o LatentSync devolve

MEDIDO: **sempre 25 fps**, independente da entrada. A duracao do video sai
arredondada pra quadro inteiro (fica alguns centesimos maior que o audio) e o
audio volta com a duracao exata que entrou. A resolucao e preservada.

Parametros usados: `inference_steps 25`, `guidance_scale 2`, `enable_deepcache`.
Mais passos melhora e demora; guidance mais alto gruda mais a boca mas distorce.

## O norte: sair do Colab

Pesquisa de 13/08/2026.

**O LatentSync esta parado.** Sem release desde junho de 2025; em julho de 2026 o
repositorio tinha 228 issues abertas e o ultimo commit com mais de um ano.
Continua sendo o melhor em fidelidade visual da boca, interior, dente, lingua e
formato de labio saem mais nitidos que nos concorrentes, e e Apache-2.0, seguro
pra uso comercial. Mas nao e aposta permanente.

### Caminhos de execucao sem servidor proprio

| Onde | Como | Observacao |
|---|---|---|
| fal.ai | API do LatentSync, cobra por rodada | caminho mais curto pra automatizar |
| Replicate | API do LatentSync, cobra por rodada | mesma ideia |
| RunningHub | workflow LatentSync na plataforma | exige salvar o workflow na conta e pegar o workflow_id, igual ao motion control |

O RunningHub tem a vantagem de a integracao ja existir no ecossistema (mesmo
padrao de `nodeInfoList`, poll e download). fal.ai e Replicate tem a vantagem de
nao precisar de setup por conta.

### Alternativas de modelo, se o LatentSync apodrecer

- **MuseTalk**: apontado em 2026 como quase fotorrealista, com geracao em tempo
  real e boa preservacao de identidade. Codigo MIT, uso comercial liberado. E o
  substituto mais provavel.
- **Wav2Lip**: continua sendo a referencia de precisao de sincronia pura, seis
  anos depois, e e leve e robusto. Perde feio em nitidez: serve quando sincronia
  importa mais que acabamento.

### Regra ao migrar

Qualquer troca de execucao ou de modelo passa por **comparacao lado a lado no
mesmo material**, com o fundador julgando a imagem. Ele e o portao visual. Numero
de benchmark de terceiro nao substitui ele assistindo.
