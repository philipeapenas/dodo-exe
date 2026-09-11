# Playbook de Organizacao - pasta de gravacao de processo

A estrutura **e fixa.** A ferramenta le e escreve nesses lugares; mudar a
estrutura sem avisar quebra o pipeline.

## As cinco pastas

```
<projeto>/material/processo/
  gravaçao/      planos brutos, direto do gravador de tela
  editado/       cada plano com o tempo morto cortado, velocidade normal
  completo/      os planos emendados: o registro inteiro
  final/         a versao pra quem vai assistir
  comunicacao/   o relatorio de comunicacao
```

> Repare no acento: a pasta e `gravaçao`, do jeito que o fundador criou. Nao
> "corrija" o nome, os caminhos apontam pra ela.

## A diferenca entre `completo` e `final`

Esse e o ponto que se erra com facilidade.

| | `completo/` | `final/` |
|---|---|---|
| Pra que serve | registro do processo, referencia | conteudo pra publico assistir |
| Tempo morto | cortado | cortado |
| Vicio de linguagem | **mantido** | **excisado** |
| Velocidade | normal | 1,4x |

O `completo` e a memoria fiel do processo, e contra ele que o relatorio de
comunicacao aponta os tempos, porque e nele que os tropecos ainda existem. O
`final` e o produto.

**`final` nao e necessariamente pro cliente.** Ele e pro publico que o fundador
quer que veja o conteudo: pode virar material de treinamento interno, aula, ou
entrega. Depende do caso.

## Onde isso vira nota no vault

As duas notas (relatorio de comunicacao e passo a passo do processo) vao para:

```
Estudos/Areas da Vida/Auto Conhecimento/Recursos/Comunicação/
```

**Nao em `Processos/`.** Gravacao de processo e classificada como **auto
conhecimento**, nao como documentacao tecnica: o que o fundador extrai disso e a
evolucao da propria comunicacao. Mover pra `Processos/` achando que esta
organizando melhor contraria esse desenho.

Quem escreve as notas e a `assistente-expert`, acionada por handoff.

## Entrega pra cliente

Quando a gravacao for entregue a um cliente, a copia sai do `final/` e vai pra
pasta de entrega do projeto com o **nome que o cliente pediu**. Use o parametro
`--entrega` com o caminho completo.

O nome vem do briefing do cliente e **nunca se inventa**. Quando a pasta de
entrega ja tem criativos, siga o padrao de nome deles. Se o nome nao estiver
claro, **pergunte ao fundador**: arquivo com nome errado na mao do cliente e
retrabalho e vergonha.

## Formato

Gravacao de tela fica em **paisagem, na resolucao nativa**. Nao converta pra
vertical: o conteudo da tela vira ilegivel. Ao juntar planos de tamanhos
diferentes, **preencha a borda ate um quadro comum em vez de redimensionar** -
escalar borra o texto da interface, que e justamente o que a pessoa precisa ler.

## Antes de rodar

Se a pasta parecer estar no meio de uma reorganizacao (arquivo em lugar
inesperado, subpasta vazia recem-criada), **pare e pergunte**. Rodar em cima de
estrutura em movimento produz saida em lugar errado e apaga trabalho.

E lembre: o Google Drive montado como unidade no computador as vezes lista pasta vazia por engano. Antes de
concluir que sumiu alguma coisa, tente enumerar de novo algumas vezes.
