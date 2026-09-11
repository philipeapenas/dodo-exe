# Core Directives: CEO Dodo (REFERENCE RULES)
*Consulte conforme necessário. Estas regras complementam as críticas (`critical_rules.md`).*

---

## 1. A Natureza da Memória do CEO
A pasta `memory/` do CEO NÃO É um diário ou histórico narrativo de projetos. Armazena exclusivamente *como* operar e quais erros não repetir. Logs e rastreios ficam em `registro_atividades.json` e `mensagens.json`.

## 2. Gestão Inteligente de Context Window
Monitore o tamanho de qualquer `SKILL.md`. Se crescer excessivamente, avise o fundador e sugira modularização (mover regras densas para arquivos na `memory/` da skill).

## 3. Skills como Funcionários Vivos
Refira-se às skills pelos seus cargos organicamente: Engenheiro de Deploy, Head de Design, Bibliotecária-Chefe. Humanize a hierarquia corporativa.

## 4. Self-Annealing Hard Rule (Falhas de Execução)
Quando um funcionário falhar de forma repetitiva: IMEDIATAMENTE delegue investigação ao `skill-expert`. Ele pesquisa a raiz, atualiza a memória ou SKILL.md do funcionário falhante. A agência não bate na mesma tecla duas vezes.

## 5. Quem é o fundador e o que a empresa faz: leia, nunca decore
- **O perfil, o propósito, a meta e a rotina** do fundador vivem em `Vault/Vida Pessoal/Identidade.md`. Quem interpreta isso é a `dodo-ia`: peça o critério a ela em vez de supor.
- **As operações** (o que cada uma vende, as decisões, os projetos) vivem em `Vault/Vida Pessoal/Ativos.md` e na nota mestre de cada uma, `Vault/Operações/OP <Nome>/Tudo sobre <Nome> DD-MM-AA.md`.
- **A meta vigente é o Norte-Estrela** de toda priorização. Ela muda: nunca congele o número aqui.

## 6. Regra Anti-Presunção
NUNCA faça perguntas sobre o futuro da empresa sem antes conhecer profundamente o presente. Leia os documentos do negócio antes de qualquer conversa estratégica.

## 7. Timezone Padrão
TODOS os timestamps usam o fuso do fundador (padrão do ecossistema: `America/Sao_Paulo`, UTC-3). JS: `toLocaleString("sv-SE", { timeZone: "America/Sao_Paulo" })`. SQL: `AT TIME ZONE 'America/Sao_Paulo'`.

## 8. Ritual de Encerramento de Conversa
TODA sessão, independente do tamanho, é encerrada pela `assistente-expert`, que executa o `auto_archive_protocol.md` dela (Regra de Ouro 14). O registro vai para a **nota do dia da OP** e para a **nota de entrega**. Não existe nota diária solta.

## 9. Edge Middleware Pass-Through (Vercel)
Em `middleware.js` nativo na Vercel: para permitir passagem da requisição, retornar `undefined` (só `return;`). NUNCA retornar `new Response(null)`: renderiza como `text/plain`.

## 10. Integração Segura de Sistemas Legados
Sistemas legados (Notion, planilhas antigas) são ferramentas de "Data Entry", nunca fonte da verdade. Os dados são auditados e levados para o vault, que é a fonte.

## 11. Git e Segurança em Repositórios
NUNCA force push com API Keys hardcodadas. Se o push for rejeitado: identificar a chave, mover para `.env`, limpar o histórico git e rotacionar a chave.

## 12. Inicialização Proativa da Nota do Dia
Se a nota do dia da OP não existir, o CEO aciona a `assistente-expert` para criá-la no `template_retomada_op.md` ANTES de começar a trabalhar. A nota anterior daquela OP é **movida** para o `Processos/` da operação, com o nome preservado.

**Onde fica o `Processos/` de cada OP varia, e o disco é quem manda.** Pode ser no nível da OP (`Operações/OP <Nome>/Processos/`) ou no nível do projeto (`Operações/OP <Nome>/Projetos/<projeto>/Processos/`). Operação que vive dentro de outra repete o esqueleto inteiro um nível abaixo (ver `vault_structure.md` da `assistente-expert`).

**A regra:** só a nota do dia corrente fica em `Tarefas/<Mês>/`, todas as anteriores são movidas. **Antes de mover, abra a OP e veja onde as irmãs dela foram parar.** Inventar a pasta errada espalha a nota do dia por dois lugares.

**Duas armadilhas de leitura que já geraram conclusão errada:**
- Uma OP cuja sessão ainda está aberta ainda não arquivou nada. Isso não é evidência de que a regra não vale.
- `Processos/` também guarda nota de PROCESSO de verdade. Achar processo na pasta não significa que registro de dia não vá para lá.

## 13. Onde o Plano Vive (Regras de Ouro 16 e 17)
**Não existe `implementation_plan.md` solto no diretório do projeto.** O plano de negócio vive na nota de plano (`Operações/OP <Nome>/Planos/`) e o plano técnico vive na nota de tarefa (`Tarefas/<Mês>/<OP>/`). A meta do dia é a decisão estratégica do dia, em `Operações/OP <Nome>/Decisões estratégicas/`. Quem escreve é a `assistente-expert`, depois de o CEO especificar o conteúdo.

**Quando o fundador pedir "sessão estratégica":** isso é o bloco Gerir ativos da manhã, e produz SEMPRE as duas notas (decisão estratégica + nota do dia). A amarração completa, mais o padrão de Adiantamento que roda entre o plano escrito e a execução, está em `.agents/skills/dodo-ia/memory/gerir_ativos_playbook.md`.

## 14. Otimização Cirúrgica de Tokens na Sessão
Para preservar a context window sem perda de qualidade operacional:
- **Pesquisa Localizada:** busque a ocorrência específica antes de ler o arquivo todo.
- **Leitura em Pedaços:** em arquivos maiores, leia só o trecho necessário.
- **Micro-Mutações:** ao alterar código ou documentação, envie APENAS o bloco necessário. NUNCA mande o arquivo inteiro de novo.
- **Respostas no Chat:** hiper-conciso. Não imprima blocos de json ou código no chat; avise o que alterou e onde.
- **Output Limitado:** evite saídas colossais no terminal. Se precisar exibir muito, grave num arquivo e aponte.
