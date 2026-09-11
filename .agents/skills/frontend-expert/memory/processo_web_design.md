# Processo de Web Design de um Projeto

**Versao:** 1.0 | **Data:** 25/08/2026 | **Owner:** frontend-expert
**Origem:** a repaginacao de um painel de operacao, feita de ponta a ponta em duas sessoes. O fundador mandou salvar o fluxo pra ser o padrao sempre que ele pedir o web design de um projeto.

Quatro etapas, nesta ordem. **Nenhuma pula.** Elas existem porque cada uma barra um erro caro que ja aconteceu.

```
1. CURADORIA        frontend-expert le o que existe, busca referencia real,
   (esta skill)     escreve o design.md
        |
2. PRANCHETAS       /design - UM artefato, DUAS paginas (Computador e Celular),
   (/design)        TODAS as telas nas duas
        |
3. VALIDACAO        o fundador ajusta na mao no proprio canvas
   (fundador)       e manda os ajustes de uma vez
        |
4. IMPLEMENTACAO    frontend-expert no CSS/HTML, dev-expert no JS
```

Isto detalha a **Regra de Ouro 19**, que e a lei; aqui esta o como.

---

## Etapa 1 - Curadoria, e o `design.md`

### 1.1 Leia o que JA existe antes de buscar inspiracao fora

Ache o sistema visual do projeto - `estilo.css`, `tokens.css`, tema do Tailwind, `design.md` anterior. Extraia os valores REAIS (cor, escala tipografica, raio, espacamento, altura de controle), sem arredondar pra grade de 4/8px.

Interface nova ESTENDE esse vocabulario. So quando o fundador pedir repaginacao explicita e que voce troca a base - e ai vale dizer em voz alta o que a troca quebra (no painel de referencia, quebrou a regra de "os dois paineis da casa parecem a mesma ferramenta").

### 1.2 Busque referencia na prateleira certa

`referencias_landing_page.md` cobre landing page. Pra SISTEMA (painel, admin, ferramenta), a prateleira e outra:

| O que falta | Onde buscar |
|---|---|
| Layout de painel inteiro, tratamento de KPI, densidade | Galeria de dashboard e template de admin; busca por ano ajuda a nao pegar padrao morto |
| Componente pronto de codigo | **21st.dev** primeiro (`/community/components`), depois Aceternity e Magic UI |
| Conceito visual, textura, ousadia | **Pinterest** e Dribbble - bom pra achar direcao, ruim pra copiar estrutura |
| **A construcao de um projeto IRMAO da casa** | O codigo do outro projeto. Ver 1.3 |

**Regra que nao muda:** referencia se COLA, nao se descreve. Descrever estilo em palavras ("moderno, clean, premium") produz o default generico de qualquer IA.

### 1.3 A melhor referencia costuma estar dentro de casa

O pedido tipico e "pega a essencia daquele site, mas nao uma copia fajuta". O que funcionou: **abrir o CSS dela e ler a construcao**, nao lembrar do site.

O corte que separa referencia de imitacao:

* **TRAGA a construcao** - o mecanismo. Na vitrine: sombra dura de deslocamento sem desfoque (`4px 4px 0 0`), borda solida de 2px, grade fina no fundo, e a fisica de toque (o elemento encosta na pagina no hover: `translate(-1px,-1px)` e a sombra cresce).
* **NAO TRAGA a identidade** - a cor da marca, o fundo, o logotipo. Aquilo pertence ao outro projeto; copiar e imitacao.

### 1.4 Escolha a identidade POR ELIMINACAO, nao por gosto

Num painel de operacao, verde ja significa "funcionando", amarelo "atencao", vermelho "falhou". **Cor de marca que rouba um desses tres faz o painel mentir sobre o proprio estado.** No painel de referencia sobrou o violeta.

### 1.5 Tipografia: duas familias com papeis declarados

O fundador cobrou uma fonte que desse pra ler todo o conteudo escrito no sistema. A pilha do sistema operacional e boa pra botao e ruim pra ler.

* **Uma familia pra TEXTO** - a que ele escolher. Padrao: Montserrat.
* **Uma MONOESPACADA, so onde o caractere precisa ser inequivoco** - numero grande, preco, codigo, identificador. Onde confundir `l` com `1` custa dinheiro. Sempre com `font-variant-numeric: tabular-nums`, senao o alinhamento danca a cada leitura.
* Fuja do Inter, Roboto e Arial por padrao: sao a resposta automatica de toda IA (`direcao_estetica_playbook.md`).

### 1.6 Escreva o `design.md`

Fecha a etapa. Vive na raiz do projeto e e o registro escrito do sistema:

```
# Design - <projeto>
## Identidade      a cor da marca e POR QUE ela, nao so o hex
## Paleta          4-6 hex nomeados + as cores semanticas, separadas da marca
## Tipografia      as familias, com o papel de cada uma
## Construcao      o mecanismo (sombra, borda, textura) e de onde veio
## O que NAO veio  o que foi deliberadamente deixado na referencia, e por que
## Superficies     o que levanta e o que afunda (cartao x campo preenchivel)
```

**A secao "O que NAO veio" e obrigatoria.** E ela que impede a proxima pessoa de "completar" o design copiando o resto da referencia.

---

## Etapa 2 - As pranchetas no `/design`

**UM artefato. DUAS paginas: Computador e Celular. TODAS as telas nas duas.**

O fundador travou isso pra ter a ciencia de todo o web design do projeto num lugar so. Sistema de seis abas entrega **doze** pranchetas, num link so. Duas paginas no `canvas.json` (`pages`), nunca dois artefatos.

Regras do conteudo:

* **Estado REAL, nao estado feliz.** Se a publicacao esta desligada, ela aparece desligada. Desenho todo verde esconde justamente o que precisa de decisao.
* **Dado do banco**, ou pelo menos no formato e ordem de grandeza do real. Numero inventado gera layout que quebra no primeiro dia.
* **Numero derivado mostra a conta na tela.** "199 dias" sozinho e numero em que ninguem confia; "599 na esteira / 3 por dia" e verificavel.
* **A adaptacao pro celular e decisao de design, e vai anotada.** No painel de referencia: a barra lateral virou fita de abas rolavel, e nao barra inferior com icone - porque barra inferior obrigaria encurtar os nomes e o sistema passaria a ter dois vocabularios, um por tamanho de tela. Escreva a alternativa que voce recusou e o custo da que escolheu.

---

## Etapa 3 - Validacao

O fundador ajusta na mao no proprio canvas e manda os ajustes **de uma vez**. Por isso a etapa 2 entrega tudo: descobrir problema tela a tela custa uma rodada de conversa por tela.

**Se ele salvou no canvas, LEIA A VERSAO DELE DE VOLTA antes de continuar** (`--extract` num diretorio novo) e compare com os seus arquivos. Republicar por cima de uma edicao dele apaga o trabalho dele. Na primeira vez o diff mostrou so normalizacao do editor - mas so da pra saber isso olhando.

**Nada e implementado antes do ok.** Primeiro o fundador ve o desenho; so depois de aprovado a mudanca entra no projeto.

---

## Etapa 4 - Implementacao

Ordem da casa: **frontend-expert no CSS e no HTML, dev-expert no JS.** Nessa ordem - JS escrito antes do CSS briga com layout que ainda vai mudar.

### A armadilha que ja custou uma entrega

**Pagina autocontida nao recebe a repaginacao sozinha.** No painel de referencia o `login.html` e servido ANTES da sessao, entao ele nao pode carregar o `estilo.css` - ele espelha os tokens a mao. A repaginacao subiu, o fundador abriu no celular e a tela de login estava com a cara antiga.

Antes de dar a repaginacao por pronta, varra o projeto por **toda pagina que nao carrega a folha principal**: login, erro, e-mail, PDF, qualquer coisa servida fora do fluxo normal. E deixe no arquivo um aviso nomeando o episodio, nao um "manter em sincronia" generico.

### Preserve o contrato de IDs

Ao reestruturar o HTML, os IDs sao contrato com o JS. Confira ANTES de subir:

```
IDs que o JS usa e nao existem mais no HTML  -> quebra silenciosa
IDs novos no HTML sem JS                      -> tela morta
```

---

## Relacionadas

* **Regra de Ouro 19** - a lei (desenho antes do codigo, a cadeia, a fonte, todas as telas, mesmo artefato).
* `direcao_estetica_playbook.md` - o criterio estetico, que roda dentro da Etapa 1.
* `referencias_landing_page.md` - as prateleiras de referencia pra LANDING PAGE.
* `tema_escuro_playbook.md` - traducao pro modo escuro, quando o projeto tiver os dois.
