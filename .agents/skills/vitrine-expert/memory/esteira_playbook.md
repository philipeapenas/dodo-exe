# Playbook da Esteira de Vitrines

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** vitrine-expert
**Origem:** medido em execucao real montando a primeira vitrine (um salao de estetica). Nada aqui e teoria: cada numero saiu do cronometro daquele run.

---

## A economia que manda na esteira

O preco de entrada nao paga o site, paga a **porta**. Quem constroi a empresa e a manutencao mensal. Os numeros abaixo sao de uma oferta real de entrada; troque pelos da sua.

| Item | Valor |
|---|---|
| Preco | R$97 |
| Hospedagem e endereco (Vercel) | R$0 |
| Taxa de pagamento | ~R$1 |
| **Sobra por venda** | **R$96** |

O custo real e tempo. **Alvo: 2h por site (~R$48/hora). Teto: 3h.** Passou disso, ou o preco sobe ou o gabarito melhora - nunca "se vira e entrega".

Consequencia direta: toda etapa da esteira precisa se pagar. Etapa que consome tempo sem mudar o resultado sai, mesmo que pareca boa pratica. Ja aconteceu uma vez (ver Vereditos).

---

## O portao de entrada: duas condicoes

O fluxo operacional tem a **venda no meio** dos dois briefings:

```
Briefing 1 (site)  ->  conversa no WhatsApp  ->  VENDA CONFIRMADA
                                                       |
                                           Briefing 2 (enviado ao cliente)
                                                       |
                                        material completo + pagamento
                                                       |
                                                 ESTEIRA COMECA
```

**Briefing 1** e captura: so identifica o lead e leva pro WhatsApp. Campo a mais ali e atrito puro.
**Briefing 2** e producao: vai depois do pagamento, entao pode ser tao comprido quanto precisar. E dele que sai todo o material da pagina, inclusive as imagens de referencia escolhidas pela propria cliente.

**A esteira nunca comeca com so uma das condicoes.** Pago sem material: nao ha o que montar. Material sem pagamento: a operacao trabalha de graca. O relogio do prazo prometido conta do **briefing 2 completo**, nao do briefing 1.

Detalhe dos campos: o `--exemplo` do `tools/nova_vitrine.py` e o contrato de entrada.

---

## As 7 etapas, com o tempo medido

Referencia: run da primeira vitrine, 20 minutos do briefing a estrutura montada. Os tempos abaixo sao o piso conhecido, nao a meta - o run tinha o gabarito sendo criado junto.

| # | Etapa | Quem | Tempo medido | Observacao |
|---|---|---|---|---|
| E1 | Material do cliente | vitrine-expert | 0,5 min | So porque o founder ja tinha separado. **E a etapa que mais atrasa na pratica** |
| E2 | Copy nos 15 blocos | copywriter-expert | 3 min | Aguarda aprovacao do founder antes do E3 |
| E3 | Direcao visual | frontend-expert | 4,5 min | Paleta e tipografia tiradas do logo |
| E4 | HTML e CSS | frontend-expert | 8 min | Sobre o gabarito |
| E5 | JS (movimento) | dev-expert | 4,5 min | Auto-revisao obrigatoria |
| E6 | Deploy | vercel-expert | - | Nao medido no run de referencia |
| E7 | Entrega | vitrine-expert | - | Fecha o cronometro |

**O gargalo real nao e nenhuma dessas.** E o material do cliente. Enquanto a foto e o endereco chegarem por vai-e-volta de WhatsApp, a montagem de 20 minutos vira entrega de 2 dias. Por isso o briefing 2 existe.

---

## E1 - Material

O que precisa estar na mao antes de comecar:

1. **Logo** - e a fonte da paleta e da tipografia. Sem logo nao ha direcao visual.
2. **Fotos de trabalho, 4 a 6** - em nicho visual e **insumo bloqueante**, no mesmo nivel do nome do negocio.
3. **Referencia visual escolhida pela cliente** - o que ela acha bonito. Substitui a garimpagem de galeria.
4. **Endereco e horario** (se o negocio for local) ou **area de cobertura** (se for digital).
5. **Depoimentos** - 2 ou 3 elogios reais que clientes ja mandaram.

**Por que foto e bloqueante e nao "seria bom ter":** conferido em dois sites de referencia do mesmo mercado. Nos dois, a fotografia E o conteudo - foto de cliente real em quase toda secao, mosaico de trabalho, foto do espaco, retrato de quem atende. Vitrine de estetica sem foto nao e uma vitrine ruim, e uma vitrine **incompleta**: falta o material que carrega metade da pagina.

No run de referencia isso apareceu como nota: a copy se autoavaliou em **5,0** por falta total de prova, com todos os blocos de texto entre 8 e 9. A nota geral e a MENOR nota entre as secoes, nunca a media - a media daria 8,2 e esconderia o problema.

---

## E2 - Copy: os 15 blocos adaptados para vitrine local

A copywriter-expert entrega nos 15 blocos canonicos do `landing_page_playbook.md`. Aquela estrutura assume **LP de venda com preco, pilha de valor, garantia e escassez**. Vitrine de negocio local nao tem isso. A adaptacao, que a skill deve pedir explicitamente:

| Bloco | Na LP de venda | Na vitrine local |
|---|---|---|
| 9. Apresentacao da oferta | Pilha de valor com ancoragem e preco | **Cardapio de servicos.** Sem preco publicado, salvo se o cliente pedir |
| 11. Garantia | Transferencia de risco com prazo | **Compromisso de atendimento.** Nao existe garantia formal; o que existe e conversa honesta antes de comecar |
| 12. Urgencia e escassez | Lote, turma, prazo | **Agenda.** So entra se o cliente CONFIRMAR que a agenda fecha de verdade. Se nao confirmar, o bloco sai inteiro |

Os demais blocos seguem a estrutura canonica integralmente.

**Estagio de consciencia:** servico local vive no estagio 3 e 4 - a pessoa ja quer o servico, esta escolhendo ONDE. A pagina nao precisa convencer ninguem a cuidar do cabelo. Precisa dar **clareza (o que tem), credibilidade (quem cuida) e facilidade (como agendo)**. Copy longa de educacao aqui atrapalha.

**Objecao silenciosa do mercado:** "quanto custa?". Ela ganha **bloco proprio** na pagina, nao linha escondida em acordeao. O texto honesto e do tipo "o valor depende do que voce quer fazer, do tamanho e do estado do cabelo - eu te passo certinho antes de voce vir, sem surpresa na hora de pagar", com o botao do lado.

---

## E3 - Direcao visual: do logo, nao da galeria

1. Abrir o logo do cliente e tirar dele **4 a 6 tons nomeados** e **2 familias tipograficas** (display + corpo).
2. Conferir contra os **3 cliches de "cara de IA"** do `direcao_estetica_playbook.md`. O cliche numero 1 (fundo creme + serifada de alto contraste + acento terracota) e exatamente o buraco natural de um brief de estetica, casamento ou wellness.
3. Escolher **um** elemento-assinatura, derivado de algo verdadeiro do logo.

**A inversao que funciona:** usar a cor da marca como **CAMPO** (preenchendo secoes inteiras), nao como acento num botao. Cor de marca so no botao e o que faz a pagina parecer template.

**Exemplo do gabarito:** logo de line art rose, script elegante, moldura circular. Virou: rose como campo, texto em cacau (nao preto), dourado so na assinatura, Fraunces + Karla (serifada de BAIXO contraste, fugindo do cliche), e o **arco** como elemento-assinatura - a moldura circular do logo virou estrutura (topo em arco nos cards de servico, filete-arco que se desenha sob cada titulo).

**Nao repetir a paleta nem as fontes entre clientes.** O gabarito e a estrutura; o tema e de cada um.

---

## E4 e E5 - Montagem

**Estrutura de arquivos** (igual ao gabarito):

```
Projetos/Dominio/<cliente>/
  index.html
  assets/css/style.css
  assets/js/movimento.js
  assets/js/vendor/{gsap,ScrollTrigger,lenis}.min.js
  assets/img/logo.*
  tools/backup.bat
  Resumo do projeto/{mensagens.json, cronometro.json, copy.md}
```

Os arquivos de vendor sao **copiados de um projeto existente**, nunca de CDN.

**Corte duro:** frontend-expert faz HTML e CSS. Depois, dev-expert faz o JS. Nunca ao mesmo tempo, nunca a mesma skill.

**Movimento:** o sistema e UM SO, copiado e adaptado entre sites (`movimento_playbook.md` da frontend-expert). As 4 regras inegociaveis valem sempre: dois modos em vez de desligado, grade anima por item, estado inicial por JS, conteudo de rede avisa quando chega.

**A auto-revisao da dev-expert nao e formalidade.** No run de referencia ela pegou 2 bugs de seletor aninhado (bloco animando dentro de bloco animando) que teriam ido pro ar. Etapa mantida por veredito medido.

---

## O portao de publicacao

Enquanto faltar dado do cliente, a pagina e montada com **preenchimento visivelmente marcado**, nunca com texto plausivel:

1. `<meta name="robots" content="noindex">` no head.
2. Barra vermelha no topo do body avisando que a estrutura esta em montagem.
3. Todo trecho de exemplo dentro de `<span class="exemplo">`, com fundo amarelo e borda pontilhada.

**Publicar e remover as tres coisas juntas.** Enquanto houver UM marcador, as outras duas ficam.

**Por que isso importa:** dado ficticio plausivel num site de cliente real e perigoso de verdade. Depoimento inventado publicado em nome do cliente e problema juridico e de reputacao, nao detalhe de acabamento. O marcador visivel torna o vazamento por descuido impossivel.

---

## Onde a esteira TERMINA

Em **estrutura crua e elegante**, pronta pro web design fazer a curadoria de acabamento - o que da ao site "cara de quem vale 10K".

A vitrine-expert entrega: os blocos todos no lugar, a copy certa, o tema do cliente, o movimento funcionando, no ar.
A vitrine-expert **nao** entrega: o refino visual final, a arte autoral, a selecao fina de imagem.

Confundir os dois estoura o orcamento de 2h e mata a margem. No handoff, diga explicitamente o que ficou pendente de dado do cliente e onde estao os marcadores.

---

## Vereditos de processo (medidos, nao opinados)

**CORTADO - busca de referencia visual em galeria.** Testada em 15/08/2026 a pedido do founder, depois de ter sido pulada na primeira passada. Custou 16 min (13% do orcamento de 2h). O founder comparou o antes e o depois: *"nah, nao senti diferenca"*.

O que a busca ensinou virou regra permanente do gabarito e nao precisa ser redescoberto a cada cliente:
- Faixa de preco como bloco proprio, nunca escondida em acordeao.
- Botao de agendar em toda secao, nao so no topo e no fim.
- Italico dentro do titulo separando o fato do sentimento ("Tem dia que da vontade de *cuidar de tudo de uma vez*").
- Cor de marca como campo, nao como acento.

Dois achados que sobrevivem como conhecimento, mesmo com a etapa cortada:
- **Filtrar galeria por categoria de mercado devolve a referencia errada.** "Beauty" e quase todo e-commerce de skincare. O filtro certo e **modelo de negocio**: serve a pagina que termina em "agende", nunca a que termina em "comprar". Das 137 da lapa.ninja, sobraram 2.
- Em nicho visual, foto de trabalho e insumo bloqueante.

**MANTIDO - auto-revisao estatica da dev-expert antes da entrega.** Pegou 2 bugs reais no unico run medido. Custo baixo, retorno comprovado.

---

## Proxima evolucao conhecida

`tools/nova_vitrine.py` - o gerador. Recebe o briefing 2 e emite o projeto inteiro: pastas, vendor copiado, backup.bat, mensagens.json, cronometro ja rodando e o index.html preenchido com os dados reais nos blocos fixos e marcadores no que falta.

Derruba as etapas mecanicas de ~20 min para ~2 min. O que ele NAO faz e o julgamento: o mecanismo unico da copy, a leitura do logo e o acabamento continuam humanos ou de skill.

O worker automatico e so o gerador com um gatilho na frente: pagamento confirmado E briefing 2 completo.
