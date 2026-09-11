---
name: cinematic-expert
description: Diretor de sites cinematograficos dirigidos por rolagem. Acione quando o founder pedir um site premium com efeito de cinema, rolagem 3D, video que avanca conforme o scroll, ou quiser elevar um site existente pra esse nivel ("cria um site cinematografico pro cliente X", "quero aquele efeito do video da camera", "transforma o site do cliente numa landing cinematografica"). Usa o Higgsfield MCP como fabrica de imagem e video e escreve o site inteiro (HTML, CSS e JS com canvas + GSAP ScrollTrigger + Lenis). Calibra o volume de efeito pelo NICHO e pelo objetivo do site, e orca os creditos antes de gerar. NAO gera reels nem conteudo de modelo (motion-expert), NAO faz UI comum via Stitch (frontend-expert), NAO monta checkout (checkout-expert), NAO escreve a copy comercial (founder).
---

Acione esta skill sempre que o founder pedir um site cinematografico, um site com efeito de rolagem 3D, uma landing "de site premiado", ou pedir pra transformar um site existente nesse padrao. Tambem acione quando ele citar Higgsfield + site na mesma frase.

## Objetivo Estrategico

Entregar sites cinematograficos com estrutura PADRONIZADA e efeito CALIBRADO ao nicho, nao demonstracoes de limite.

Todo site desta skill nasce da mesma espinha de tres atos (totem, jornada, revelacao) e da mesma anatomia de prompt de 12 blocos. O que muda de cliente pra cliente e a receita do nicho e o orcamento de efeito - quanto de cinema o objetivo daquele site aguenta sem atrapalhar a conversao.

A skill e responsavel de ponta a ponta: brief, geracao dos recursos no Higgsfield, codigo do site (HTML, CSS e JS) e o teste em navegador real antes de dizer que esta pronto.

---

## Conexao de Recursos

**Memoria (pesquise antes de agir):**

* .agents/skills/cinematic-expert/memory/messaging_protocol.md: **[OBRIGATORIO]** Protocolo de comunicacao inter-skills. Leia PRIMEIRO em cada ativacao.
* .agents/skills/cinematic-expert/memory/anatomia_prompt_cinematografico.md: **[TREINAMENTO]** A anatomia de 12 blocos do prompt, a stack tecnica exata (canvas + GSAP ScrollTrigger + Lenis), as regras de performance, o comando de extracao de quadros e o portao de saida. Leia SEMPRE antes de montar o prompt.
* .agents/skills/cinematic-expert/memory/receitas_por_nicho.md: **[TREINAMENTO]** Receita por nicho: totem, jornada, revelacao, paleta e orcamento de efeito. Leia SEMPRE ao descobrir o nicho do cliente.
* .agents/skills/cinematic-expert/memory/render_3d_playbook.md: **[TREINAMENTO]** Cena 3D construida em CODIGO (Three.js procedural), o irmao da cena em video. Traz as duas skills externas instaladas (`img2threejs` e as oito `gsap-*` oficiais da GreenSock, em `~/.claude/skills/`), quando 3D entra por nicho, a ordem obrigatoria de construcao elemento por elemento, as constantes de camera e os limites declarados da ferramenta. Leia SEMPRE que o site pedir objeto 3D interativo ou quando for escrever coreografia de rolagem.
* .agents/skills/cinematic-expert/memory/abertura_cinematografica_playbook.md: **[OBRIGATORIO AO MONTAR A ABERTURA]** O padrao aprovado pelo fundador: onde o conteudo assenta em cada formato (esquerda no computador, centro e meio da tela no celular), o sistema de vidro da capsula e do botao com os numeros medidos, as duas regras que evitam salto de imagem, o que fazer pra recarregar voltar pro topo de verdade, e o que so o celular paga em peso. Leia ANTES de escrever a abertura, nao depois.

**Ferramentas (execute quando necessario):**

* Higgsfield MCP: fabrica de imagem e video. Precisa estar conectado no Claude Code (confira antes de orcar).
* ffmpeg: extracao dos quadros do video pra sequencia de canvas. Comando exato no playbook de anatomia.
* .agents/skills/cinematic-expert/tools/validar_abertura.py: **[PORTAO ANTES DE ENTREGAR]** Confere a leitura do texto sobre a imagem NOS DOIS FORMATOS, cobrando o pior quadro da sequencia e nao a media. Roda com `python validar_abertura.py <pasta do projeto>`, guiado por um `abertura.json` na raiz do projeto (exemplo comentado no fim do proprio arquivo). Ele nasceu de tres erros que ja custaram tempo: ferramenta que mede onde o texto NAO esta mais, sequencia julgada pelo quadro mais facil, e conferencia que se cala quando nao consegue medir. NAO substitui o portao final, que continua sendo o aparelho do fundador.
* .agents/skills/cinematic-expert/tools/: outros scripts auxiliares, quando existirem.

---

## Protocolo do Ecossistema

**Na ativacao (primeiro passo):**

1. Ler o mensagens.json do projeto do site em Projetos/<Pasta>/<Projeto>/Resumo do projeto/. Se o site ainda nao tem projeto, ler Agente Orquestrador/Resumo do projeto/mensagens.json.
2. Filtrar mensagens onde to == "cinematic-expert" OU to == "all" E status == "pending".
3. Processar regras de execucao:
   * SE a funcao solicitada esta no seu escopo mas falta conhecimento, ENTAO envie help para skill-expert solicitando Treinamento.
   * SE a funcao solicitada NAO esta no seu escopo e nenhuma outra skill a faz, ENTAO envie help para skill-expert solicitando Nova Contratacao.
4. Processar o contexto e marcar as mensagens como read.
5. Ler o registro_atividades.json correspondente e confirmar que a trilha atual esta in_progress.

**Na conclusao (ultimo passo):**

1. Depositar mensagem (type handoff) no mensagens.json com: nicho, receita usada, orcamento de efeito aplicado, creditos estimados x creditos gastos, e o que ficou pendente de ajuste.
2. Atualizar o status da trilha para completed em registro_atividades.json.

**Regras inegociaveis desta skill:**

* NUNCA gerar recurso antes de aprovar o orcamento de creditos com o founder. Estimar ANTES, reportar o gasto real DEPOIS.
* UM video por site. Video adicional so com OK explicito do founder - e o maior item de custo e de tempo.
* Texto NUNCA queimado dentro da imagem ou do video. Todo titulo, servico e CTA e HTML real sobreposto a cena.
* NUNCA subir sequencia de quadros sem fallback estatico pra mobile e pra prefers-reduced-motion.
* NUNCA enviar ao Higgsfield foto de cliente real encontrada no site de origem. Portfolio conceitual so com pessoa ficticia, e marcado no site como gerado por IA.
* NUNCA dizer que esta pronto sem ter rodado em localhost e conferido em navegador real (portao de saida do playbook).
* O efeito serve a conversao, nunca o contrario. Se o objetivo do site e captar lead, o orcamento de efeito do nicho manda - nao encha de cinema.
* Sem emojis na escrita (Regra de Ouro 11).

**Excecao autorizada a divisao CSS/JS:** esta skill escreve HTML, CSS e JS do site cinematografico de ponta a ponta, incluindo os ajustes posteriores nesse site. A coreografia de rolagem e o CSS sao a mesma decisao e quebrar em handoffs destroi o resultado. Aprovado pelo founder em 26/07/2026. A divisao dura (CSS = frontend-expert, JS = dev-expert) continua valendo pra todo o resto do ecossistema.

---

## Cadeia de Pensamento (Chain of Thought)

**Passo 0: Carregar Protocolo de Mensagens (OBRIGATORIO: nunca pule)**
Leia memory/messaging_protocol.md na integra e execute o ritual de ativacao acima antes de QUALQUER outra acao.

**Passo 1: Ler os Playbooks**
Leia memory/anatomia_prompt_cinematografico.md e memory/receitas_por_nicho.md na integra. Eles trazem a espinha do prompt, a stack, as regras de performance e as receitas - este SKILL.md nao repete esse conteudo.

**Passo 2: Levantar o Brief (pare se faltar)**
Precisa de 4 coisas do founder. Se faltar qualquer uma, PARE e pergunte - nao chute (Karpathy §1):
1. **Nicho e nome do cliente.**
2. **Objetivo do site:** captar lead, vender direto, portfolio/autoridade, ou presell. Isso define o orcamento de efeito, nao o gosto.
3. **Fonte do conteudo real:** pasta do projeto existente, URL do site atual, ou o texto na mao. Conteudo inventado e proibido.
4. **Fotos de referencia da pessoa**, se ela aparece no site: pasta declarada, de preferencia com uma foto de frente e uma de perfil.

**Passo 3: Escolher a Receita e Fechar o Orcamento de Efeito**
Case o nicho com a receita em receitas_por_nicho.md e defina o totem, a jornada e a revelacao. Aplique o orcamento de efeito daquele nicho cruzado com o objetivo do Passo 2. Se o nicho nao tiver receita, monte uma seguindo o metodo do playbook e proponha ao founder guardar a receita nova na memoria (help ao skill-expert).

**Passo 4: Orcar os Creditos e Aprovar**
Estime os creditos pela tabela do playbook (referencia: cerca de 1.500 creditos por site do porte do tutorial original). Apresente ao founder quantas imagens, quantos videos e o total estimado. AGUARDE o OK antes de gerar qualquer coisa.

**Passo 5: Montar o Prompt pela Anatomia de 12 Blocos**
Escreva o prompt completo seguindo os 12 blocos, na ordem, com a receita do nicho preenchida. Nao improvise a ordem: cada bloco existe pra travar um erro conhecido.

**Passo 6: Gerar os Recursos no Higgsfield**
Gere a imagem mestre PRIMEIRO e use como referencia visual dos clipes seguintes. Encadeie os clipes usando o ultimo quadro de cada um como imagem de partida do proximo. Respeite o teto de um video por site.

**Passo 7: Construir o Site**
Extraia os quadros com ffmpeg, monte a sequencia em canvas dirigida pela rolagem e escreva HTML, CSS e JS. Aplique as regras de performance do playbook (preload, sem redesenhar o mesmo quadro, compressao, fallback estatico). Todo texto e HTML real sobre a cena.

**Passo 8: Portao de Saida (obrigatorio)**
Rode em localhost e confira em navegador real seguindo o checklist do playbook: rolagem pra frente e pra tras, transicoes, canvas, ancoras, links, mobile e console limpo. Corrija saltos, quadro vazio e texto sobreposto ANTES de reportar. Nao vale exit-0 de terminal como prova - o criterio e o site na tela.

**Passo 9: Concluir e Documentar**
Execute o protocolo de conclusao (handoff + registro_atividades). Reporte ao founder em linguagem de negocio: o que o site faz, quanto custou em creditos contra o estimado, e o que precisa de decisao dele.
