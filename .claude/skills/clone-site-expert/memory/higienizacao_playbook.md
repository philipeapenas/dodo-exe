# Playbook de Higienizacao

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** clone-site-expert

Higienizar e cirurgia em codigo minificado. O que protege nao e cuidado, e **metodo**: simular antes, falhar cedo e conferir depois.

---

## A trava que vem antes de tudo

**Nunca limpe antes de apresentar o inventario e receber o OK.** Nao e formalidade: o fundador pediu isso explicitamente. Ele precisa saber que existia um pixel, mesmo depois de ele sair.

---

## O metodo do script

Higienizacao **nao se faz na mao**, arquivo por arquivo. Se faz por script, por tres motivos que se pagam na primeira execucao:

1. **Modo `--conferir`** - aplica as trocas em memoria, valida as contagens e nao escreve nada. Erro de padrao aparece antes de corromper arquivo.
2. **Falha alto** - se uma troca esperada nao encontra alvo, o script **para e nao escreve nada**. Silencio e o inimigo: troca que nao aplicou vira rastreador que ficou.
3. **Conferencia final** - varre o resultado atras de cada rastro do dono e falha se sobrar. E ela que autoriza dizer "limpo". Falhando, **descarta o destino**: site meio limpo no disco e convite a publicar por engano.

A contagem esperada por troca (`1`, `2`, `QUALQUER`, `OPCIONAL`) e o que transforma o script em rede de seguranca. Sem ela, um padrao que casa zero vezes passa despercebido.

### Motor e configuracao

**O metodo vive no `motor_limpeza.py` e nao se reescreve. Cada site novo escreve so a
configuracao:** identidade do dono, lixo, lista de trocas com contagem e lista de residuos
proibidos. Copie `exemplo_config.py` para `tools/limpar_<projeto>.py` do projeto, junto com o
motor, e preencha.

Isso nasceu de um problema real. O antigo `limpar_httrack.py` se apresentava como limpador
generico, mas tinha o GA, o token do Meta, o deploy da Vercel e o WhatsApp do primeiro site
clonado cravados como constantes, e abortava em espelho com mais de uma pasta de dominio. Ao encontrar
um site de construtor (Atomicat) ele nao serviu de nada.

**Pior: o `--conferir` dele nao conferia.** Em simulacao ele rodava so a copia e pulava todas as
etapas de limpeza, entao nunca chegava a testar padrao nenhum. E as trocas nao declaravam
contagem esperada. Ou seja, este playbook descrevia um metodo que a ferramenta nao implementava.
Se um playbook promete uma garantia, confira no codigo se ela existe.

As duas armadilhas que a refatoracao expos, e que valem para qualquer script de limpeza:

- **Contar ocorrencia em arquivo que a copia descartou infla a contagem.** Um filtro so decide
  quem sobrevive, e a copia e as trocas usam o mesmo. Sem isso as contagens acusam o dobro.
- **`**/*.html` nao casa com arquivo na raiz.** No `fnmatch` esse padrao exige ao menos uma
  pasta no caminho. Numa configuracao onde a pasta de dominio vira a raiz, a pagina principal
  escapa de todas as trocas **em silencio**. O motor trata `**/` como zero ou mais pastas.

**Referencia de Next.js:** em site Next.js a identidade do dono se esconde no payload de
hidratacao, nos chunks do webpack e no modulo de evento. Guarde o `tools/limpar_<projeto>.py`
do primeiro clone em Next.js congelado e funcionando: no proximo, leia de la em vez de
redescobrir.

---

## O que remover, e como

**Lixo do HTTrack:** `hts-cache/`, `hts-log.txt`, `backblue.gif`, `fade.gif` e o `index.html` **da raiz** - esse ultimo e propaganda do proprio HTTrack, nao o site. Mais os comentarios injetados em cada pagina.

**Rastreamento** - em quatro frentes, todas necessarias:
- a tag de preload do script no `<head>`
- o componente dentro do payload de hidratacao
- o import do modulo no chunk de layout
- os **disparadores de evento** no bundle

Nos disparadores, nao delete o modulo: **transforme as funcoes em vazias**, preservando os nomes exportados. Quem chama continua chamando e recebe `undefined`, em vez de estourar erro.

**Nao apague chunk de fornecedor** so porque o codigo dele ficou sem uso. O runtime do webpack lista os chunks numa dependencia (`e.O(0,[...])`); sumir com um arquivo trava a inicializacao. Deixe o codigo morto no lugar e garanta que ninguem o invoca.

---

## A regra de ouro do HTML hidratado

> **Todo texto da pagina existe em DOIS lugares: no HTML renderizado e dentro do bundle. Os dois mudam JUNTOS, ou nenhum muda.**

Se so o HTML mudar, o React reescreve o valor antigo por cima na hidratacao, e parece que a alteracao "nao pegou". Foi exatamente o sintoma que o fundador reportou.

Depois de toda edicao de copy, **conte as ocorrencias nos dois arquivos** e confirme que batem.

Corolario: **nao adicione atributo nenhum ao HTML** (nem `data-*`) sem espelhar no bundle. Precisando marcar elemento pra script, selecione por estrutura e classe que ja existem.

---

## Escape em texto minificado

Bundle guarda acento como escape (`R\xe1pida`). Ao escrever script de substituicao:

- **Escreva o script em ARQUIVO, nunca em heredoc de terminal.** O heredoc come a barra dupla: `\\xe1` chega ao Python como `\xe1` e vira o caractere `á` de verdade, que nao casa com o arquivo. Isso ja quebrou a sincronia entre HTML e bundle duas vezes.
- JSON-LD dentro do payload vem **escapado duas vezes**: sao **tres** barras invertidas por aspa (`\\\"name\\\"`), nao uma.
- Texto de selo costuma ter **espaco a esquerda** (`" Entrega em "`), separando do icone. Padrao sem o espaco nao casa.

---

## Otimizacao segura, e o preco de cada corte

| Corte | Ganho real |
| --- | --- |
| `polyfills.js` (`noModule`) | disco. Navegador moderno nem baixa |
| Subset de fonte fora do alfabeto usado | disco. O `unicode-range` ja evitava o download |
| Bloco `@font-face` orfao no CSS | correcao, nao ganho: apontava pra arquivo apagado |

**Ao apagar arquivo, apague a referencia.** Rode `conferir_referencias.py` depois de todo corte.

---

## A bateria de verificacao

Nesta ordem, e **sem pipe** - canalizar pro `tail` engole o codigo de saida e o encadeamento segue com falha:

1. `conferir_referencias.py` - todo `src`, `href` e `url()` resolve
2. `conferir_classes.py` - toda classe usada existe no CSS purgado
3. `node --check` em cada `.js` editado
4. Payload de hidratacao ainda bem formado - **compare contra o original como controle**. Foi assim que um falso alarme do proprio verificador foi descoberto: o original apresentava as mesmas falhas
5. Servir local e conferir as rotas por `curl`
6. Conferencia final do script: zero ocorrencia de cada rastro

**Exit code de script nao e prova de resultado.** Prova e o rastro ausente na varredura e o arquivo respondendo 200.
