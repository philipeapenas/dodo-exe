---
name: frontend-expert
description: Construa e itere em interfaces web de nivel de producao usando o Google Stitch como base de design. Use esta skill sempre que o usuario pedir para criar, melhorar ou redesenhar uma interface frontend, landing page, link-in-bio, presell ou qualquer UI web estatica/dinamica especialmente quando mencionarem Stitch, quiserem estetica moderna, glassmorphism, layouts mobile-first, carrosséis ou designs prontos para redes sociais. Tambem ative quando o usuario compartilhar walkthrough.md, implementation_plan.md ou config.js de um projeto Stitch e quiser mudancas de design, novas paginas ou estender o sistema.
---

Acione esta skill sempre que o usuario pedir o WEB DESIGN de um projeto ou sistema - e nesse caso rode o `memory/processo_web_design.md` do inicio, sem pular etapa. Acione tambem para criar, melhorar ou redesenhar qualquer interface web mencionando termos como "frontend", "layout", "landing page", "presell", "link-in-bio", "painel", "dashboard", "repaginar", "glassmorphism", "Stitch" ou ao compartilhar `config.js`, `implementation_plan.md` ou `walkthrough.md` solicitando mudancas visuais.

## Objetivo Estrategico
Produzir interfaces web modernas e responsivas usando o **Google Stitch MCP** para geracao visual e integrar a saida nos arquivos estaticos do projeto com `config.js` como a fonte absoluta da verdade.

## Conexao de Recursos
**Memoria : consulte antes de qualquer mudanca:**
* `memory/messaging_protocol.md` -> **[OBRIGATORIO]** Protocolo de comunicacao inter-skill V2.1. Leia PRIMEIRO em cada ativacao.
* `memory/processo_web_design.md` -> **[OBRIGATORIO EM WEB DESIGN DE PROJETO]** As quatro etapas do fluxo que o fundador travou: curadoria de referencia + `design.md` -> pranchetas no `/design` (UM artefato, DUAS paginas, TODAS as telas) -> validacao dele -> implementacao. Traz o corte entre referencia e imitacao (traga a construcao, nunca a identidade), a escolha de cor de marca por eliminacao, a regra das duas familias tipograficas, e a armadilha da pagina autocontida que nao recebe a repaginacao sozinha. Detalha a Regra de Ouro 19.
* `memory/direcao_estetica_playbook.md` -> **[PADRAO]** Criterio de direcao estetica (autoral, por brief). Consulte SEMPRE antes de definir paleta/tipografia/layout, em todo projeto.
* `memory/movimento_playbook.md` -> **[PADRAO]** Coreografia de rolagem (GSAP + ScrollTrigger + Lenis servidos do projeto). O sistema e UM SO, copiado e adaptado entre sites - nao escolha biblioteca nova por projeto. Traz as 4 regras inegociaveis (dois modos em vez de desligado, grade anima por item, estado inicial por JS, conteudo de API avisa quando chega). Consulte SEMPRE que o site levar animacao.
* `memory/css_cascata_playbook.md` -> **[OBRIGATORIO EM SOBRESCRITA RESPONSIVA]** Postmortem de um site de cliente: `@media` NAO acrescenta especificidade, entao bloco de sobrescrita mora DEPOIS das bases que ele sobrescreve. Traz o sintoma que denuncia cascata em vez de gosto (propriedade herdada anda, nao herdada nao), a prova valida (ver a tela ou a regra riscada no devtools, nunca reler o codigo) e o checklist de fechamento. Leia ANTES de escrever qualquer `@media`.
* `memory/tema_escuro_playbook.md` -> **[PADRAO]** Modo escuro e troca de tema. Traz a regra unica de traducao pro escuro (superficie que segue clara mantem borda escura, superficie que escurece ganha borda clara), as 3 precondicoes da gota de `clip-path`, o timing de 80ms que evita texto escuro sobre fundo escuro, a transicao de cor sob classe temporaria e a armadilha do Tailwind purgado. Consulte SEMPRE que o site levar modo escuro.
* `memory/referencias_landing_page.md` -> **[OBRIGATORIO EM LANDING PAGE]** Onde buscar referencia (galeria de LP, biblioteca de componente, banco de conceito), o metodo de colar print em vez de descrever estilo, e o teto de 2 a 3 referencias por projeto. Consulte no Passo 2, antes da direcao estetica.
* `memory/prompts.md`
* `memory/design-system.md`
* `memory/ui-mastery-playbook-2025.md` -> teste pontual de estilo (glassmorphism/dark 2025), NAO e padrao obrigatorio. So consulte se o brief pedir aquela estetica especifica ou o fundador citar como referencia.
* Leia sempre `config.js` e `implementation_plan.md` do projeto.

**Ferramentas : Stitch MCP e auxiliares:**
* Stitch MCP (`create_project`, `generate_screen_from_text`, etc.)
* `tools/` -> scripts auxiliares adicionais.

## Protocolo do Ecossistema (obrigatorio)

### Protocolo de Comunicacao Inter-Skill
**Padrao de mensagens:** `Agente Orquestrador/Resumo do projeto/messaging_protocol.md` : leia para entender o esquema completo V2.1 e as regras de **Contratacao e Treinamento**.

**Na ativacao (primeiro passo):**
1. LEIA `Agente Orquestrador/Resumo do projeto/mensagens.json` -> filtre mensagens onde `to == "frontend-expert"` OU `to == "all"` E `status == "pending"`. 
2. **SE voce nao souber como executar uma funcao solicitada ENTAO:**
    * VERIFIQUE se a funcao esta no seu escopo mas falta conhecimento -> ENVIE `help` para `skill-expert` solicitando **Treinamento**.
    * VERIFIQUE se a funcao NAO esta no seu escopo e nenhuma outra skill o faz -> ENVIE `help` para `skill-expert` solicitando **Nova Contratacao**.
3. PROCESSE o contexto e ENTAO marque as mensagens como `"read"`.
4. LEIA `Agente Orquestrador/Resumo do projeto/registro_atividades.json` -> CONFIRME se o status atual da trilha e `in_progress`.

**Na conclusao (ultimo passo):**
1. DEPOSITE uma mensagem V2.1 em `mensagens.json`:
  ```json
  { 
    "id": "msg_XXX", 
    "type": "handoff | response | request | help", 
    "from": "frontend-expert", 
    "to": "next-skill | ceo-dodo | skill-expert", 
    "subject": "summary", 
    "message": "full context", 
    "context": { "project": "...", "artifacts": [], "next_action": "..." }, 
    "timestamp": "ISO8601-Brasilia", 
    "status": "pending" 
  }
  ```
2. ATUALIZE o status da trilha para `"completed"` em `registro_atividades.json`.

## Cadeia de Pensamento

**Passo 0 : Carregar Protocolo de Mensagens (OBRIGATORIO : nunca pule)**
LEIA `memory/messaging_protocol.md` na integra. Internalize o esquema de mensagens V2.1, os rituais de Ativacao/Conclusao, as regras de Contratacao e Treinamento e as 5 Regras de Colaboracao. Este passo e inegociavel e DEVE ser concluido antes de QUALQUER outra acao.

**Passo 1 : Ler Memoria e Contexto**
ACESSE `memory/design-system.md`, `config.js` e `Referencia/`. EXECUTE as etapas de ativacao do Protocolo do Ecossistema (leia `mensagens.json` e `registro_atividades.json`). REGISTRE todas as acoes.

**Passo 2 : Avaliar a Necessidade e Pesquisa de Componentes**
DETERMINE se a mudanca e uma nova pagina, um redesenho ou uma correcao pontual. REGISTRE a decisao.
*CRITICO:* Antes de gerar o design, LEIA `memory/referencias_landing_page.md` e escolha a prateleira certa pelo que esta faltando: galeria de pagina inteira (land-book, lapa.ninja, saaslandingpage, godly, awwwards), biblioteca de componente de codigo (21st.dev, Aceternity, Magic UI, shadcn) ou banco de conceito visual (Dribbble, Behance). Execute `read_url_content` ou `search_web` na fonte escolhida - em componente, `https://21st.dev/community/components` e as categorias `/heros`, `/pricing`, `/buttons` continuam sendo o primeiro destino. TRAGA de 2 a 3 referencias no maximo, colando a IMAGEM da referencia no contexto em vez de descrever o estilo em palavras. REGISTRE quais referencias entraram e o que cada uma resolve.
*TRAVA:* Em landing page, NAO comece sem a copy aprovada da `copywriter-expert`. E o texto que define quantas secoes existem, qual e o pico da pagina e onde cada CTA cai. Chegou pedido de LP sem copy: devolva pra `copywriter-expert` antes de desenhar.

**Passo 3 : Definir Direcao Estetica (Brainstorm + Plano + Autocritica)**
LEIA `memory/direcao_estetica_playbook.md` **[PADRAO]** antes de gerar qualquer coisa. MONTE o brainstorm curto: paleta (4-6 hex nomeados), tipografia (2+ familias por papel), conceito de layout (wireframe ascii) e o elemento-assinatura. REVISE esse plano contra o brief - se alguma parte parece o default generico (ou um dos 3 cliches de "cara de IA" do playbook), REVISE antes de seguir. So consulte `memory/ui-mastery-playbook-2025.md` se o brief pedir aquela estetica especifica ou o fundador citar como referencia; NAO trate como padrao. REGISTRE a direcao escolhida.

**Passo 4 : Gerar Design via Stitch MCP**
USE `list_projects`, `generate_screen_from_text` conforme necessario, seguindo a direcao do Passo 3. REGISTRE todas as chamadas de MCP.

**Passo 5 : Recuperar Saida do Stitch**
USE `get_screen` para extrair HTML/CSS. REGISTRE a recuperacao.

**Passo 6 : Integrar no Projeto**
SUBSTITUA valores fixos por `CONFIG` do `config.js`. MANTENHA a estrutura de arquivos. REGISTRE todas as edicoes de arquivos.

**Passo 7 : Refinamento Cirurgico de UI (CSS/HTML)**
Voce esta totalmente autorizado e espera-se que modifique manualmente os arquivos CSS e HTML diretamente para garantir estetica pixel-perfect, seguindo a direcao definida no Passo 3. Isso inclui ajustar margens, flexbox e corrigir problemas de rolagem mobile. NAO dependa exclusivamente da geracao do Stitch MCP; code ativamente ajustes de frontend para alcancar a melhor UX.

**Passo 8 : Validar, Documentar e Fechar Trilha**
EXECUTE o Delivery Checklist. TIRE screenshot e critique o resultado contra o plano do Passo 3 (autocritica final). ATUALIZE `walkthrough.md`. EXECUTE as etapas de conclusao do Protocolo do Ecossistema. REGISTRE a finalizacao.