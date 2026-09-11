# Padroes de Bots do Telegram - Dodo.exe

Este documento dita as diretrizes de arquitetura para a criacao de bots de Telegram, minimizando a necessidade de instrucoes redundantes no `SKILL.md`.

**Referencia de Arquitetura Absoluta (Template de Fluxo em Markdown):**
Sempre que for criar a arquitetura de um novo bot, estruture o documento de comandos (ex: `comandos_telegram.md`) seguindo este TEMPLATE estrutural de Maquina de Estados e Botoes Inline:

```markdown
# POP - Maquina de Estados e UI do Bot Telegram

## 🎯 Arquitetura Interativa (Wizard)
Em vez de exigir a memorizacao de argumentos posicionais exatos, o bot opera atraves de uma interface de botoes (Inline Keyboard) e um gerenciador de estados em memoria.

## 📱 Menu Principal (`/start` ou `/menu`)
- **Botoes Inline:**
  - `[ ➕ Acao 1 ]`
  - `[ 💸 Acao 2 ]`
  - `[ 📊 Acao 3 ]`

## ⚙️ Fluxos de Botao

### Fluxo: `[Nome da Acao]`
1. **`AWAIT_[ACAO]_[PASSO_1]`**: Pede "[Pergunta em texto solicitando o dado]"
2. **`AWAIT_[ACAO]_[PASSO_2]`**: 
   - Botoes Inline: `[ Opcao A ]` | `[ Opcao B ]`
3. **`AWAIT_[ACAO]_[PASSO_3]`**: Pede "[Outro dado se necessario]"
4. **Finalizacao**: Salva no banco (Supabase) e exibe sucesso.

## 🛡️ Invariantes de Input
- O Bot sempre oferece uma opcao para "Cancelar" e voltar ao Menu Principal durante qualquer fluxo.
- [Regra de validacao de input 1, ex: converter virgula em ponto]
- [Regra de validacao de input 2]
```

## Stack e Arquitetura Principal
1. **Linguagem:** Node.js (preferencialmente, exceto quando especificado Python).
2. **Framework Telegram:** Telegraf.
3. **Banco de Dados:** Supabase (`@supabase/supabase-js`).
4. **Estado / Flow:** Uso mandatario de sessoes (`telegraf/session`) para gerenciar as etapas do usuario (ex: `ctx.session.step = 'AWAIT_DATA'`).

## Regras de UX e Interface (Obrigatorio)
1. **Menu Nativo (Fim do `/start`):** O bot **NUNCA** deve depender puramente do usuario digitar `/start`. O menu principal deve ser configurado nativamente na interface do Telegram para aparecer como um botao ou ao lado da caixa de texto.
   - Implementacao: `bot.telegram.setMyCommands([{ command: 'menu', description: 'Abrir Painel Principal' }])`
2. **Botoes Interativos (Inline Keyboards):** Sempre que o usuario precisar escolher opcoes, utilize botoes em vez de pedir texto. 
   - Implementacao: `Markup.inlineKeyboard([...])`
3. **Comunicacao Simples:** Textos curtos, diretos e com emojis de forma a guiar o usuario claramente atraves dos fluxos.
4. **Protecao de Estado:** Certifique-se de tratar mensagens de texto baseadas no estado da sessao atual, ignorando-as se o usuario estiver na etapa `IDLE` ou equivalente.

## Inicializacao
1. Garantir tratamento do `process.env` (Tokens do Telegram e Supabase URL/Key).
2. Verificar erro de variaveis faltando para crashar imediatamente se desconfigurado.
3. Iniciar instanciando a `Telegraf`, middleware de sessao e cliente do Supabase.
