# Protocolo de Resolução de Problemas
**Versão:** 1.0 | **Data:** 25/06/2026

Este documento define o fluxo determinístico e obrigatório para o arquivamento de soluções de problemas reportados no Vault. O objetivo é manter a separação estrita entre o "relato do problema" e a "entrega técnica da solução".

## Regras Estruturais (Obrigatório)

Sempre que a solução de um problema (localizado na pasta de `Problemas`) for concluída, você DEVE executar os seguintes 3 passos cirúrgicos:

### Passo 1: Criação da Nota de Entrega
- **Local:** `Vault/Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/`
- **Nome:** `Nome descritivo do problema DD-MM-AA.md`
- **Conteúdo Obrigatório no Topo:** 
  A nota DEVE iniciar com a data e um link direto citando a nota do problema original.
  ```markdown
  # Nome descritivo
  **Problema Resolvido:** [[Nome_da_Nota_do_Problema]]
  ```
- **Corpo:** Explicação técnica detalhada de como o problema foi solucionado (arquivos alterados, root cause, bugs mitigados, etc.).

### Passo 2: Limpeza da Nota Original do Problema
- **Local:** Pasta de `Problemas` original onde o relato foi criado.
- **Ação:** NUNCA detalhe a solução técnica nesta nota. Mantenha apenas a descrição original do bug enviada pelo usuário.

### Passo 3: Fechamento (Link Reverso)
- **Ação:** No final da nota original do problema, adicione uma linha divisória e o link apontando para a Nota de Entrega criada no Passo 1, usando EXATAMENTE o formato abaixo:
  ```markdown
  ---

  Resolvido: [[Nome_da_Nota_de_Entrega]]
  ```

Este protocolo garante que o Vault mantenha o rastreamento bidirecional (Problema <-> Entrega) sem poluir as notas de relato com jargão técnico.
