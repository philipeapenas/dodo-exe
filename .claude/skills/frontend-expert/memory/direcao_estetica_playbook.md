# Direcao Estetica - Criterio de Design Autoral

Absorvido do plugin `frontend-design` (Anthropic, instalado 24/07/2026). Este e o criterio PADRAO de direcao estetica da `frontend-expert` - roda antes de qualquer geracao via Stitch MCP, em todo projeto.

**Relacao com `ui-mastery-playbook-2025.md`:** aquele arquivo foi um teste pontual de estilo (glassmorphism/dark mode 2025), NAO e padrao obrigatorio pra todo projeto (confirmado pelo fundador). So consulte ele quando o brief pedir explicitamente aquela estetica ou o fundador citar como referencia. Por padrao, a direcao estetica nasce do criterio abaixo.

## Fundamente no assunto real
Antes de desenhar, se o brief nao fixar o produto/assunto, fixe voce: nomeie o assunto concreto, a audiencia e o unico job da pagina. Construa com o conteudo e vocabulario real daquele universo (materiais, instrumentos, jargao proprio) - e dali que vem escolha distinta, nao de template generico.

## Hero como tese
A abertura da pagina e a coisa mais caracteristica do universo do assunto - manchete, imagem, animacao, demo ao vivo, o que fizer mais sentido pra ela. Numero grande + label pequeno + gradiente de acento e a resposta padrao de qualquer IA; so use se for de fato a melhor opcao pro brief.

## Tipografia carrega personalidade
Pareie fonte de display e de corpo de proposito, nao sempre a mesma combinacao usada em qualquer projeto. Defina escala tipografica com peso/largura/espacamento intencional. Tipografia e parte memoravel do design, nao veiculo neutro de conteudo.

### Montserrat e o default do papel de LEITURA

O fundador declarou Montserrat como fonte padrao de artefato e projeto. E preferencia de legibilidade dele, nao de estetica - ele le o artefato inteiro pra decidir, e fonte ruim custa atencao em toda leitura.

Como aplicar:

* **Montserrat carrega o que ele LE** em artefato, prancheta de `/design` e projeto novo: titulo, corpo, nota explicativa, tabela, rotulo. Sempre com pilha real declarada - `'Montserrat', 'Segoe UI', system-ui, sans-serif`. Google Fonts e o unico host que o Artifact aceita.
* **A regra das duas familias continua valendo.** Montserrat ocupa o papel de leitura, nao os dois. A segunda familia segue existindo pro papel de dado, rotulo tecnico ou codigo.
* **Excecao: prancheta que retrata um sistema real.** Ali dentro vale a fonte DO SISTEMA retratado - a prancheta e a foto do produto, nao texto pra ler. No primeiro desenho assim o miolo dos quadros ficou em JetBrains Mono (a fonte do painel) e todo o resto em Montserrat; o fundador foi avisado do corte e nao pediu mudanca.
* **Precedencia normal nao muda:** palavra do fundador > sistema visual que ja existe no projeto > este default. Projeto com CSS proprio continua mandando na propria fonte.

## Estrutura e informacao
Numeracao, eyebrows, divisores so fazem sentido se codificam algo verdadeiro sobre o conteudo (ex: processo real, timeline onde a ordem importa). Nao decore com marcador numerado (01/02/03) so porque e comum - questione antes de usar.

## Movimento deliberado
Pense onde e SE animacao serve o assunto: sequencia de carregamento, reveal por scroll, microinteracao de hover, atmosfera ambiente. Um momento orquestrado bate mais forte que efeitos espalhados. As vezes menos e mais - excesso de animacao e um dos sinais mais fortes de "cara de IA".

## Complexidade casada com a visao
Direcao maximalista pede execucao elaborada; direcao minimalista pede precisao de espacamento/tipografia/detalhe. Elegancia e executar bem a visao escolhida, seja qual for.

## Calibragem - os 3 cliches de "cara de IA" (evite por padrao)
Design gerado por IA hoje se agrupa em 3 padroes que aparecem independente do assunto - trate como default generico, nao escolha, e so use se o brief pedir exatamente isso:
1. Fundo creme (proximo de #F4F1EA) + serifada de alto contraste + acento terracota.
2. Fundo quase preto + 1 acento vibrante unico (verde-acido ou vermelho).
3. Layout estilo jornal - hairlines, zero border-radius, colunas densas.

Onde o brief fixa uma direcao visual, siga ela exatamente (a palavra do brief sempre vence, mesmo se pedir um desses 3 de proposito). Onde o brief deixa o eixo livre, nao gaste essa liberdade voltando pro default.

## Processo: brainstorm -> plano -> autocritica -> construir -> criticar de novo
1. Brainstorm curto: paleta (4-6 hex nomeados), tipografia (2+ familias por papel: display com restricao + corpo + utilitaria pra dado/legenda se precisar), conceito de layout (wireframe ascii + descricao em prosa), e o elemento-assinatura (a 1 coisa unica que a pagina vai ser lembrada).
2. Revise o plano contra o brief ANTES de codar: se alguma parte parece o default generico que voce produziria pra qualquer pagina parecida, revise e anote o que mudou e por que.
3. So depois de confirmar a unicidade relativa do plano, escreva o codigo seguindo o plano revisado - derive cor e tipografia dali, nao do que "sempre funciona".
4. Cuidado com especificidade de seletor CSS (ex: `.section` vs `.cta` se cancelando) - fonte comum de bug de padding/margin entre secoes.
5. Faca essa iteracao no raciocinio antes de mostrar - so exponha quando a confianca de que vai agradar o fundador for alta.

## Contencao e autocritica
Gaste a ousadia em 1 lugar so - o elemento-assinatura e o memoravel, o resto fica quieto e disciplinado. Corte decoracao que nao serve o brief. Nao anuncie o piso de qualidade, so entregue: responsivo ate mobile, foco de teclado visivel, reduced-motion respeitado. Tire screenshot pra se autocriticar sempre que o ambiente permitir.

## Copy e material de design
Palavra em UI existe pra facilitar entendimento e uso - e material de design, nao decoracao. Escreva do lado de quem usa: nomeie pelo que a pessoa controla e reconhece, nunca por como o sistema foi construido (ex: "notificacoes", nao "webhook config"). Voz ativa como padrao - o nome da acao se mantem do botao ao toast (se o botao diz "Publicar", o toast diz "Publicado"). Erro nunca pede desculpa nem fica vago sobre o que aconteceu; tela vazia e convite pra agir, nao lamento.
