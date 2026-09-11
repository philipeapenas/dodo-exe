# Playbook de Auditoria e Otimizacao de Skills

**Versao:** 1.0 | **Data:** 11/05/2026

Checklist padrao para auditar e otimizar qualquer skill existente. Executar quando o fundador pedir review, limpeza ou otimizacao de uma skill.

---

## Checklist de Auditoria (executar na ordem)

### 1. Inventario da pasta `memory/`

- Liste todos os arquivos em `memory/`.
- Para cada arquivo, anote: nome, tamanho, proposito.
- Identifique arquivos orfaos (nao referenciados na SKILL.md).
- Identifique arquivos com nomes antigos ou desatualizados.

### 2. Deteccao de Redundancia (SKILL.md vs memory/)

- Leia a SKILL.md integralmente.
- Para cada bloco de conteudo inline com mais de 10 linhas, verifique: esse conteudo ja existe em algum arquivo de `memory/`?
- **SE sim:** remova o inline e substitua por um ponteiro (`Leia memory/[arquivo].md`).
- **SE nao, mas deveria ser reutilizavel:** extraia para um novo arquivo em `memory/`.

### 3. Consistencia de Nomes e Referencias

- O nome da skill no YAML, nos caminhos de scripts e nos templates de mensagem (campo `from`) DEVEM ser identicos.
- Verifique se algum arquivo usa nomes antigos da skill (ex: nome antes de um rename).
- Verifique se caminhos de scripts em `tools/` estao corretos.

### 4. Acentuacao (Regra de Ouro 4)

- Todos os arquivos `.md` em `memory/` e a SKILL.md DEVEM estar em portugues sem acentuacao.
- Scan rapido por caracteres acentuados: a, e, i, o, u, c cedilha, til.

### 5. Formato de Dados Atualizado

- Verifique se schemas, formatos de prioridade, estruturas de tabela e convencoes estao alinhados com o uso real atual (comparar com os dailies/entregas mais recentes).
- Formatos legados devem ser atualizados para o padrao vigente.

### 6. Restricoes e Proibicoes

- Verifique se a skill tem restricoes explicitas documentadas (ex: "nunca crie arquivos .py no vault").
- Se aprendizados de erros passados existirem, eles DEVEM estar registrados como restricoes.

### 7. Economia de Tokens

- A SKILL.md deve ser o mais enxuta possivel. Tudo que e procedimento longo e deterministico deve viver em `memory/`.
- A SKILL.md deve conter: gatilhos, objetivo, conexao de recursos (ponteiros), protocolo do ecossistema e cadeia de pensamento (ponteiros quando possivel).
- **Meta:** SKILL.md com menos de 100 linhas sempre que viavel.

---

## Formato do Relatorio de Auditoria

Ao concluir, apresente ao fundador:

```
| Arquivo | Antes | Depois | Acao |
|---|---|---|---|
| SKILL.md | X linhas | Y linhas | [descricao] |
| memory/[arquivo].md | X linhas | Y linhas | [descricao] |
```

Sempre peca aprovacao ANTES de executar as mudancas.
