# Playbook de Comunicacao - o que a analise procura

O objetivo: **desenvolver autoridade na comunicacao**. O fundador quer ver onde
titubeia pra corrigir o habito, nao so ter um video limpo.

Isso define a regra central do playbook:

> **Corta-se o que e ruido puro. Aponta-se o que revela inseguranca.**

## O que E cortado do video final

**Vicio solto**: `tipo`, `assim`, `ne`, `entao`, `ai`, `cara`, `beleza`,
`certo`, `ta`, e os arrastados (`eeee`, `ahhh`, `hmmm`). Sai sem prejuizo: a
frase continua inteira sem eles.

**Comeco abortado**: palavra repetida (`esse, esse processo`) ou cortada e
retomada (`aquel- aquele material`). Descarta-se a tentativa, mantem-se a boa.

**Tempo morto**: silencio acima do respiro normal.

## O que NAO e cortado, so apontado

**Marca de incerteza**: "acho que", "nao sei explicar exatamente", "mais ou
menos", "sei la". Cortar quebra a frase e, pior, esconde o problema. E o item que
mais custa autoridade: ele conhece o processo, a fala precisa mostrar isso.

**Autocorrecao**: "na verdade", "quer dizer", "mentira". Sinal de que faltou
decidir a ordem da explicacao antes de gravar.

Esses dois vao inteiros pro relatorio, com tempo e trecho.

## O relatorio

Quatro categorias, cada uma com o porque dela importar:

| Categoria | O que e |
|---|---|
| Recomecos e gagueira | comecou, abortou, recomecou. O mais visivel pra quem assiste |
| Marcas de incerteza | enfraquecem a autoridade |
| Autocorrecoes | se contradisse e voltou atras |
| Travadas | parou pra procurar a palavra |

Mais a **contagem de vicios normalizada por mil palavras**: sem normalizar, uma
gravacao mais longa parece pior so por ser maior.

## A comparacao com a gravacao anterior

E o que transforma o relatorio em treino em vez de foto isolada. A serie fica em
`tools/historico_comunicacao.json` e **nunca deve ser apagada**: perder o
historico e perder a curva de evolucao.

Cada relatorio novo mostra: vicio por mil palavras contra a gravacao anterior, e
a contagem de cada categoria antes e depois.

## Diagnostico que vale repetir

Na primeira analise real (uma gravacao de uns cinco minutos), as tres categorias
apontavam pra mesma causa raiz: **gravar sem roteiro**. Quem gravava conhecia o
processo, mas estava descobrindo a ordem da explicacao enquanto falava.

Quando o relatorio mostrar muitas travadas e recomecos juntos, a recomendacao nao
e "fale melhor", e **fazer um roteiro de topicos de trinta segundos antes de
apertar gravar**. Ataca a causa, nao o sintoma.

## Parametros calibrados

Validados assistindo o resultado:

| Parametro | Valor | O que faz |
|---|---|---|
| `GAP_FRASE` | 0,55s | silencio acima disso separa uma frase da outra |
| `RESPIRO` | 0,32s | pausa que sobra entre frases no corte |
| `PAUSA_LONGA` | 1,5s | a partir daqui conta como travada |
| `VELOCIDADE` | 1,4x | aceleracao da versao final |

Ele aprovou o ritmo com esses numeros. **Nao mude por conta propria**: mudanca
passa por ele assistindo e pela `skill-expert` gravando aqui.
