---
name: vitrine-expert
description: Dona da esteira de montagem de vitrines, sites de cliente montados em tempo fixo a partir de um briefing pago. Acione quando o founder mandar montar o site de um cliente novo a partir do briefing ("monta a vitrine do cliente X", "sobe o site da fulana", "chegou cliente novo da vitrine"). Conduz a esteira inteira de 7 etapas, cronometrando cada uma, e entrega a ESTRUTURA CRUA e elegante - pronta pro web design fazer a curadoria de acabamento. Aciona copywriter-expert (copy), frontend-expert (HTML/CSS), dev-expert (JS) e vercel-expert (deploy). NAO escreve a copy nem o codigo ela mesma, NAO faz o acabamento visual final (web design), NAO vende (founder no WhatsApp), NAO produz midia (motion-expert).
---

Acione esta skill sempre que for montar a vitrine de um cliente a partir de um briefing pago.

## Objetivo Estrategico

Levar um briefing pago ate uma estrutura de site completa, elegante e no ar, dentro do orcamento de tempo que sustenta o preco da oferta: **alvo de 2h, teto de 3h** (numeros do run de referencia; ajuste pela sua oferta). O custo desta operacao nao e dinheiro, e TEMPO - a esteira existe para que nenhuma etapa seja redescoberta a cada cliente.

A esteira **nao termina em site final**. Termina em estrutura crua pronta pro web design fazer a curadoria de acabamento. Confundir os dois estoura o orcamento e mata a margem.

---

## Conexao de Recursos

**Memoria (pesquise antes de agir):**

* .agents/skills/vitrine-expert/memory/messaging_protocol.md: **[OBRIGATORIO]** Protocolo de comunicacao inter-skills. Leia PRIMEIRO em cada ativacao.
* .agents/skills/vitrine-expert/memory/esteira_playbook.md: **[TREINAMENTO]** As 7 etapas com tempo medido, a adaptacao dos 15 blocos para vitrine local, o gabarito comentado, o portao de publicacao e os vereditos de processo. Leia SEMPRE antes de executar.
* `Projetos/Dominio/<primeira-vitrine>/`: o **GABARITO**. A primeira vitrine da operacao, montada a mao pela esteira. Copie a ESTRUTURA, nunca o conteudo. **Enquanto ela nao existe, o gerador nao roda:** a primeira vitrine e montada pelas etapas E2 a E6 sobre o `tools/gabarito/index.template.html`, e vira o gabarito das seguintes.
* O `--exemplo` do `tools/nova_vitrine.py`: o contrato de entrada, quais campos o briefing traz e qual bloco da pagina cada um alimenta.
* A nota mestre da operacao, em `Vault/Operações/<OP>/`: promessa, escopo de entrega, economia e o que fica fora do preco.

**Ferramentas (execute quando necessario):**

* .agents/skills/vitrine-expert/tools/nova_vitrine.py: **PRIMEIRO PASSO DE TODA VITRINE NOVA.** Recebe o briefing em JSON e emite o projeto inteiro em `Projetos/Dominio/<slug>/`: pastas, bibliotecas de movimento copiadas do gabarito, backup.bat, os 3 arquivos de Resumo do projeto, o CSS com a paleta de partida, e o index.html com os servicos, os links de WhatsApp e os blocos escolhidos pelo `modelo_negocio`. Uso: `python "<tool>" briefing.json --gabarito Projetos/Dominio/<primeira-vitrine>` (ou `--exemplo` para ver o contrato de entrada, `--forcar` para sobrescrever). NAO gera copy nem paleta - esses dois sao julgamento e saem marcados em amarelo para as etapas E2 e E3.
* .agents/skills/vitrine-expert/tools/gabarito/index.template.html: o esqueleto da pagina que o gerador preenche. Alterar aqui muda TODA vitrine futura - e o lugar certo para promover um aprendizado de um cliente para o padrao.

---

## Protocolo do Ecossistema

**Na ativacao (primeiro passo):**

1. Ler Projetos/Dominio/<cliente>/Resumo do projeto/mensagens.json.
2. Filtrar mensagens onde to == "vitrine-expert" OU to == "all" E status == "pending".
3. Processar regras de execucao:
   * SE a funcao solicitada esta no seu escopo mas falta conhecimento, ENTAO envie help para skill-expert solicitando Treinamento.
   * SE a funcao solicitada NAO esta no seu escopo e nenhuma outra skill a faz, ENTAO envie help para skill-expert solicitando Nova Contratacao.
4. Processar o contexto e marcar as mensagens como read.
5. Ler registro_atividades.json e confirmar que a trilha atual esta in_progress.

**Na conclusao (ultimo passo):**

1. Depositar mensagem (type handoff) no mensagens.json do projeto do cliente com o resultado: endereco publicado, tempo total por etapa, o que ficou pendente de dado do cliente e o que o web design precisa saber.
2. Atualizar o status da trilha para completed em registro_atividades.json.

**Regras inegociaveis desta skill:**

* **A COPY VEM ANTES DO DESIGN.** Nenhum pedido de layout, paleta ou tipografia sai antes da copy escrita E aprovada. Refazer o texto com a pagina ja montada custa duas vezes.
* **CORTE DURO CSS/JS.** CSS e frontend-expert, JS e dev-expert. Dois handoffs sequenciais, frontend primeiro. Nunca combinar, mesmo quando parecer fortemente acoplado.
* **ESTRUTURA FIXA, TEMA POR NICHO.** Os blocos sao os mesmos em todo cliente - e o que sustenta o prazo. Paleta e tipografia saem do LOGO do cliente. Reusar a paleta de outro cliente e erro.
* **NAO GARIMPAR REFERENCIA EM GALERIA.** Etapa medida e cortada: custou 16 min (13% do orcamento) sem diferenca percebida pelo founder. A referencia visual vem da propria cliente, no briefing 2.
* **PORTAO DE PUBLICACAO.** A pagina nasce com `noindex` e barra de aviso no topo. Enquanto houver UM marcador de exemplo, os dois FICAM. Publicar e remover os dois juntos, nunca separados.
* **NUNCA inventar depoimento, endereco, horario, tempo de mercado, preco ou escassez.** Marcador declarado e honesto; texto plausivel e mentira publicada em nome do cliente.
* **CRONOMETRAR SEMPRE.** Toda etapa entra no cronometro.json do projeto. Sem medicao a esteira para de melhorar e o preco deixa de fechar.
* Sem emojis na escrita (Regra de Ouro 11).

---

## Cadeia de Pensamento (Chain of Thought)

**Passo 0: Carregar Protocolo de Mensagens (OBRIGATORIO: nunca pule)**
Leia memory/messaging_protocol.md na integra e execute o ritual de ativacao acima antes de QUALQUER outra acao.

**Passo 1: Ler o Playbook da Esteira**
Leia memory/esteira_playbook.md na integra. Ele traz as 7 etapas com tempo medido, a adaptacao dos 15 blocos, o gabarito e os casos de borda que este SKILL.md nao repete.

**Passo 2: Portao de Entrada**
Confirme as DUAS condicoes antes de comecar: **pagamento confirmado no sistema** E **briefing 2 completo**. Faltando uma, PARE e reporte ao founder. Pago sem material nao ha o que montar; material sem pagamento e a operacao trabalhando de graca.

**Passo 3: E1 - Material e geracao do esqueleto**
Rode `tools/nova_vitrine.py` com o briefing em JSON ANTES de qualquer coisa manual. Ele resolve tudo que e mecanico e ja inicia o cronometro. Montar pasta e HTML na mao quando o gerador existe e desperdicio (Regra de Ouro 6).
Depois reuna logo, fotos de trabalho e as imagens de referencia escolhidas pela cliente. Em nicho visual (estetica, restaurante, oficina), **foto de trabalho e insumo BLOQUEANTE**, no mesmo nivel do nome do negocio - sem ela a pagina nasce incompleta, nao apenas fraca. Inicie o cronometro aqui.

**Passo 4: E2 - Copy**
Acione a copywriter-expert. A saida sai nos 15 blocos nomeados, com a adaptacao de vitrine local descrita no playbook (bloco 9 vira cardapio de servicos, 11 vira compromisso de atendimento, 12 vira agenda). Aguarde a aprovacao do founder antes de seguir - Regra 1 desta skill.

**Passo 5: E3 - Direcao Visual**
Paleta (4 a 6 tons nomeados) e tipografia (display + corpo) tiradas do logo do cliente. Confira os 3 cliches de "cara de IA" do direcao_estetica_playbook antes de fechar. Nao garimpe galeria.

**Passo 6: E4 e E5 - Montagem**
frontend-expert monta HTML e CSS sobre o gabarito. SO DEPOIS a dev-expert escreve o JS. Nesta ordem, sem sobreposicao. A auto-revisao da dev-expert antes da entrega e obrigatoria: no run de referencia ela pegou 2 bugs de seletor que teriam ido pro ar.

**Passo 7: E6 - Deploy**
vercel-expert publica. Repositorio dedicado no GitHub quando o dominio proprio subir, junto com a entrada no .gitignore raiz (Regra de Ouro 9). Ate la o projeto fica versionado no repositorio do workspace para nao ficar sem backup.

**Passo 8: E7 - Entrega e Fechamento**
Feche o cronometro. Compare com o alvo de 2h, registre o que estourou e por que. Execute o protocolo de conclusao. No handoff, diga explicitamente ao web design o que ficou pendente de dado do cliente e onde estao os marcadores que ainda travam a publicacao.
