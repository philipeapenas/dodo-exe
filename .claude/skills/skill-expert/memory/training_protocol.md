# Protocolo de Treinamento e Contratacao V1.1
**Versao:** 1.1 | **Data:** 11/05/2026 | **Owner:** skill-expert (RH)

Este documento e o protocolo canonico de Treinamento e Contratacao do ecossistema Dodo. Sempre que uma skill enviar um `help` (type: `"help"`) ao `skill-expert`, este protocolo DEVE ser seguido integralmente.

---

## Quando este protocolo e ativado

1. Uma skill detecta que **nao sabe** executar uma funcao solicitada.
2. A skill envia um `help` ao `skill-expert` com o campo `context.training_type`:
   - `"upskill"` → A funcao pertence ao escopo da skill, mas ela nao tem conhecimento documentado.
   - `"new_hire"` → A funcao **nao existe** no ecossistema, nenhuma skill a possui.

> **Regra fundamental:** Tanto `upskill` quanto `new_hire` sao **treinamentos**. O resultado e sempre um playbook `.md` gravado na `memory/` de uma skill especifica. No `new_hire` tambem se cria uma nova skill, mas o conhecimento pesquisado SEMPRE e depositado como arquivo na `memory/` do funcionario responsavel.

---

## Fluxo de Treinamento (training_type: "upskill")

```
1. [skill-X] Detecta que nao sabe fazer a funcao solicitada
     ↓
2. [skill-X → skill-expert] Envia mensagem type: "help"
   {
     "type": "help",
     "from": "skill-X",
     "to": "skill-expert",
     "subject": "Treinamento: [descricao da funcao]",
     "context": {
       "training_type": "upskill",
       "skill_to_train": "skill-X",
       "capability_gap": "[Descricao da lacuna]",
       "requested_by": "fundador | outra-skill"
     }
   }
     ↓
3. [skill-expert] Recebe o help → Inicia PESQUISA AUTONOMA
   - Usa search_web para pesquisar melhores praticas, documentacao e discussoes.
   - Compila um playbook/cheatsheet em Markdown.
     ↓
4. [skill-expert → fundador] VALIDACAO OBRIGATORIA
   - Apresenta: o que foi pesquisado, fontes, playbook proposto, nome do arquivo.
   - AGUARDA aprovacao EXPLICITA do fundador antes de gravar.
   - NUNCA gravar na memory/ sem aprovacao.
     ↓
5. [Fundador aprova] → skill-expert grava:
   `.agents/skills/<skill-name>/memory/<playbook_name>.md`
     ↓
6. [skill-expert] Atualiza o SKILL.md da skill treinada:
   - Adiciona referencia ao novo playbook na secao Conexao de Recursos.
   - Executa sync_skills.py.
     ↓
7. [skill-expert → skill-X] Envia response:
   {
     "type": "response",
     "from": "skill-expert",
     "to": "skill-X",
     "subject": "Treinamento Concluido: [nome do playbook]",
     "context": {
       "training_type": "upskill",
       "artifacts": [".agents/skills/<skill-X>/memory/<playbook_name>.md"],
       "next_action": "Releia memory/ e execute a tarefa pendente."
     }
   }
     ↓
8. [skill-X] Agora sabe fazer a funcao. Retoma a tarefa original.
```

---

## Fluxo de Nova Contratacao (training_type: "new_hire")

> **Nova contratacao E treinamento.** Alem de criar a skill nova, o RH pesquisa e compila um playbook que vai direto na `memory/` dessa nova skill.

```
1. [skill-X] Detecta que a funcao NAO pertence ao seu escopo
   E verifica que nenhuma skill no ecossistema a possui.
     ↓
2. [skill-X → skill-expert] Envia mensagem type: "help"
   {
     "type": "help",
     "from": "skill-X",
     "to": "skill-expert",
     "subject": "Contratacao: [descricao da funcao]",
     "context": {
       "training_type": "new_hire",
       "capability_gap": "[Descricao da funcao necessaria]",
       "requested_by": "fundador | outra-skill"
     }
   }
     ↓
3. [skill-expert] Recebe o help → Inicia PESQUISA de persona e tecnica
   - Pesquisa: qual profissional? Quais ferramentas? Quais mental models?
   - Monta o SKILL.md proposto seguindo a anatomia padrao.
   - Compila o playbook de treinamento inicial.
     ↓
4. [skill-expert → fundador] VALIDACAO OBRIGATORIA
   - Apresenta: justificativa, SKILL.md proposto, playbook de treinamento.
   - AGUARDA aprovacao EXPLICITA.
   - NUNCA criar skill sem aprovacao.
     ↓
5. [Fundador aprova] → skill-expert cria:
   - `.agents/skills/<new-skill>/SKILL.md`
   - `.agents/skills/<new-skill>/memory/messaging_protocol.md` (copia)
   - `.agents/skills/<new-skill>/memory/<playbook_name>.md` ← TREINAMENTO
   - `.agents/skills/<new-skill>/tools/`
   - Executa sync_skills.py.
     ↓
6. [skill-expert] Atualiza os orquestradores:
   - Adiciona a nova skill ao CLAUDE.md (router).
   - Executa sync_orchestrators.py.
     ↓
7. [skill-expert → skill-X] Envia response confirmando a nova skill.
     ↓
8. [skill-X] Envia request diretamente para a nova skill.
```

---

## Regras Inviolaveis

1. **Nenhum treinamento ou contratacao acontece sem validacao do fundador.** O skill-expert SEMPRE apresenta o resultado e AGUARDA aprovacao antes de gravar qualquer arquivo.
2. **Todo resultado de pesquisa e um playbook gravado na `memory/` de uma skill especifica**: nunca em arquivos avulsos.
3. **Toda nova skill nasce com `messaging_protocol.md` + playbook de treinamento na sua `memory/`**: factory rule.
4. **O `sync_skills.py` e executado apos qualquer treinamento ou contratacao.**
5. **A skill treinada/contratada recebe um `response` formal** confirmando que esta pronta.
