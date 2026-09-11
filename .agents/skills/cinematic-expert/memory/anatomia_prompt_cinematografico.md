# Anatomia do Prompt Cinematografico e Stack Tecnica

**Versao:** 1.0 | **Data:** 26/07/2026 | **Owner:** cinematic-expert

Playbook de treinamento inicial. Fonte primaria: tutorial do Eli Rigobeli (17/07/2026) e os dois prompts de producao dele, destrinchados na nota de estudo do vault. Complementado com validacao tecnica de performance de sequencia em canvas.

---

## Parte 1 - A espinha de tres atos

Todo site cinematografico desta skill tem a mesma estrutura narrativa. So muda o recheio por nicho.

1. **TOTEM** - o objeto que representa o oficio do cliente. E o unico recurso que exige imagem mestre + video. Exemplos: a caixa de ferramentas do reparador, a camera da fotografa.
2. **JORNADA** - a rolagem atravessa esse totem ou o mundo dele, resolvendo um problema por secao. E aqui que a sequencia de quadros vive.
3. **REVELACAO** - fecha mostrando quem entrega (a pessoa) ou o que o cliente recebe (o resultado), e aterrissa no CTA.

Se voce nao consegue nomear o totem do nicho em uma palavra, o brief ainda nao esta fechado. Volte e pergunte.

---

## Parte 2 - A anatomia de 12 blocos

Escreva o prompt nesta ordem. Cada bloco trava um erro conhecido; pular bloco e reabrir o erro.

**1. Objetivo e padrao de qualidade.** O que e, pra quem e, e o teto: "landing page cinematografica, com qualidade visual de site premiado e efeito de rolagem 3D, para [negocio real]".

**2. Preservacao e seguranca.** Antes de mexer: analise todo o projeto e crie backup. Preserve o conteudo real (historia, servicos, depoimentos, FAQ, SEO local, contato). Reuna numa unica index.html continua. Troque links de paginas separadas por ancoras internas. **Nao invente informacao.**
Site do zero: use a URL atual como fonte de CONTEUDO, nunca de layout. "Crie layout novo e original, sem copiar o atual."

**3. Fabrica e modelo.** Gere tudo pelo Higgsfield MCP. Preferencia por Cinema Studio 3.0 em 4K pro video; melhor modelo fotorrealista disponivel pras estaticas. Clipes em **16:9, 5 a 10 segundos, sem audio** (o audio do modelo nao serve pra site e encarece).

**4. Ancora visual.** Gere **UMA imagem mestre primeiro** e use como referencia visual de todos os clipes seguintes. E o que mantem cenario, luz, cores e direcao de arte consistentes. Sem isso o site vira colcha de retalhos.

**5. Identidade da pessoa.** Pasta declarada no prompt. Enviar ao Higgsfield pelo MCP como identity reference em toda cena com a pessoa. Preservar rosto, idade aparente, cabelo, tom de pele, tipo fisico e a mesma roupa. Da pra apontar a foto principal e negar tracos de fotos especificas ("use a 5.jpg como principal; nao reproduza o cabelo comprido da 2.jpg"). Pedir ao founder no minimo uma foto de frente e uma de perfil - com foto unica o rosto oscila.

**6. Roteiro numerado, cena a cena.** Cada clipe como storyboard: o que entra em quadro, o que acontece, pra onde a camera vai no fim. E a instrucao de encadeamento: **use o ultimo quadro de cada clipe como start_image do proximo**. E isso que da continuidade.

**7. Lista negativa.** Evitar maos deformadas, dedos extras, objetos flutuando, fisica impossivel, arquitetura instavel, logotipos, marcas d'agua e **texto dentro da imagem ou do video**.

**8. Bloco SITE.** Converter os clipes em sequencia de quadros num canvas controlada pela rolagem. Rolar pra baixo avanca, pra cima retorna. GSAP com ScrollTrigger pra fixar o canvas, controlar a sequencia e revelar os textos HTML no momento certo. Lenis pro smooth scroll sincronizado.

**9. Ordem das secoes e regra de texto.** Liste as secoes na ordem exata. Regra dura: **todo titulo, servico e CTA e HTML real sobreposto a cena, nunca queimado no video.** Defina paleta, tipografia e qual e a conversao principal.

**10. Teto de custo dentro do prompt.** Escreva literalmente: "CRITICO: gere somente esse unico video. Nao crie videos separados para secoes ou categorias. Depois da hero, construa toda a experiencia com imagens estaticas, HTML, CSS, canvas, GSAP, ScrollTrigger, Lenis, mascaras, parallax, zoom e transicoes." Esse paragrafo e o freio de credito.

**11. Performance e acessibilidade.** Otimizar a sequencia, versao responsiva, fallback mais leve pra celular e pra prefers-reduced-motion.

**12. Portao de saida.** Executar em localhost e conferir em navegador real antes de dizer que esta pronto.

---

## Parte 3 - Guardas de uso de imagem (obrigatorias em trabalho de cliente)

- Nao usar nem enviar ao Higgsfield fotos de clientes achadas no site de origem.
- Portfolio conceitual so com pessoas **inteiramente ficticias**.
- Nao associar pessoa ficticia a depoimento real.
- Nao apresentar imagem gerada como trabalho real do cliente.
- Colocar no site uma indicacao discreta de que as imagens conceituais foram geradas por IA.
- Produto/objeto sem marca, logotipo, numero de modelo ou texto - senao vem logo inventado.

Trava anti-desvio util: quando o totem e um objeto que tambem e produto (camera, carro, equipamento), diga o que ele NAO e. Exemplo real: "a camera e uma metafora para o olhar da fotografa, nao um produto a venda. Nao mostre especificacoes, preco, botao de compra ou linguagem de e-commerce."

---

## Parte 4 - Stack tecnica

**Base:** canvas 2D + sequencia de quadros + GSAP ScrollTrigger (scrub + pin) + Lenis (smooth scroll).

Padrao canonico da sequencia:

```js
gsap.to(currentFrame, {
  value: imageCount - 1,
  snap: "value",
  ease: "none",
  scrollTrigger: { trigger: canvas, start: "top top", end: "+=500%", scrub: true, pin: true },
  onUpdate: render
});
```

**Smooth scroll - qual usar:** Lenis e o default (leve, e o que os prompts de origem usam). GSAP ScrollSmoother e alternativa valida e hoje e gratuito, junto com o resto do GSAP. Nao use os dois juntos.

**Extracao de quadros (ffmpeg):**

```
ffmpeg -i clipe.mp4 -vf "fps=24,scale=1600:-1" -q:v 6 quadros/quadro_%04d.jpg
```

**Ultimo quadro pra encadear no proximo clipe:**

```
ffmpeg -sseof -0.1 -i clipe.mp4 -update 1 -q:v 2 ultimo_quadro.jpg
```

Um clipe de 5 a 10s a 24fps da 120 a 240 quadros. Acima de ~150 quadros o ganho visual e minimo e o peso cresce rapido - derrube o fps antes de derrubar a resolucao.

---

## Parte 5 - Regras de performance (nao negociaveis)

Estas sao o que separa o site vendavel da demonstracao pesada. O proprio autor do tutorial admitiu que nao tratou nada e o site ficou lento.

1. **Preload antes de scrubar.** Carregue os quadros antes de liberar a animacao, senao o visitante ve canvas em branco.
2. **Nao redesenhe o mesmo quadro.** Guarde o indice do ultimo quadro desenhado e saia cedo se nao mudou.
3. **Nao coloque a sequencia no topo absoluto sem poster.** O primeiro paint deve ser uma imagem estatica comprimida (e o seu LCP). A sequencia entra logo abaixo, com tempo de preload. Apple faz assim.
4. **Nao sequestre a rolagem.** Deixe o scroll nativo dirigir o scrub.
5. **Comprima de verdade.** JPEG ou AVIF, agressivo. Quadro de sequencia aceita qualidade bem mais baixa que foto solta, porque passa rapido.
6. **Fallback estatico** pra tela pequena, dispositivo fraco e `prefers-reduced-motion`. Use `gsap.matchMedia()` pra separar desktop de mobile.
7. **Anime transform e opacity**, nunca width/height/top/left. Use `will-change` com parcimonia.
8. **Teste em maquina fraca.** Scrub travado e pior que nao ter efeito.

Alvo de Core Web Vitals: LCP abaixo de 2,5s, INP abaixo de 200ms, CLS abaixo de 0,1. Se o site nao passa nisso, o cinema esta comendo a conversao.

---

## Parte 6 - Custo

Ancora real medida no tutorial: **1.566 creditos** produziram dois sites completos (um reformado + um do zero), com varios videos e varias imagens. Um site do porte do tutorial fica na casa dos **1.500 creditos**; um site com um video so e 6 a 8 estaticas fica bem abaixo disso.

O video e o item caro e lento (cerca de 5 min de espera por clipe). Imagem estatica e barata. Por isso o Bloco 10 existe.

Nao invente tabela de preco por modelo. O custo real por modelo aparece na area de **Uso** da conta Higgsfield - consulte la e reporte o gasto real ao founder no fechamento.

Regra comercial: se o site e pra cliente, essa geracao entra no orcamento do projeto.

---

## Parte 7 - Portao de saida (checklist)

Nao reporte "pronto" sem ter feito, em navegador real rodando em localhost:

- [ ] Rolagem pra frente E pra tras (a sequencia tem que voltar)
- [ ] Transicoes entre secoes sem salto e sem quadro vazio
- [ ] Canvas desenhando em todas as larguras
- [ ] Ancoras e links funcionando, inclusive o CTA principal
- [ ] Layout mobile, com o fallback ativo
- [ ] Console limpo, zero erro
- [ ] Texto legivel sobre a cena em todos os quadros (contraste)
- [ ] Formulario enviando de verdade, quando houver

Criterio: o site na tela. Exit-0 de terminal nao e prova.
