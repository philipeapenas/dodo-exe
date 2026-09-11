# Organizacao de Credenciais do Workspace

Padrao de onde vive qualquer arquivo de credencial (chave de API, `.json` de OAuth, arquivo de sessao) que uma integracao do ecossistema precise ler.

## O caminho canonico

```
<pasta pessoal fora do workspace>/credenciais/<Servico>/<conta>/<arquivo>
```

Exemplo: `<pasta pessoal>/credenciais/MCP - Google Agenda/<conta>/client_secret_....json`

**Uma pasta por servico, uma subpasta por conta.** A subpasta por conta existe para a mesma integracao poder atender duas contas diferentes sem misturar arquivo.

A pasta de credenciais do fundador e dele: pergunte onde ela fica na primeira vez que precisar e registre o caminho aqui.

## Regras

1. **Fora de qualquer repositorio.** A pasta de credenciais nao e versionada. Credencial nunca entra em pasta de projeto, mesmo com `.gitignore`: o `.gitignore` protege contra o commit, nao contra o backup do projeto e nao contra copia de pasta.
2. **O agente nunca imprime o conteudo do arquivo** em chat, log, nota do vault ou `mensagens.json`. Referenciar sempre pelo caminho.
3. **Configuracao de MCP e de script aponta para o caminho**, nunca copia o arquivo para dentro do projeto.
4. **Escopo `local`** ao registrar MCP que consome credencial (`claude mcp add <nome> -s local -e ...`), para o caminho nao ir para o repositorio.
5. **Excecao conhecida:** algumas skills leem um `tools/secrets.local.json` dentro da propria pasta (ignorado pelo git por `*.local.json`). O modelo e o `secrets.example.json` ao lado. Nunca comitar o `.local`.

## Se o workspace mudar de lugar

Todo caminho absoluto hardcoded em config, script e tarefa do Windows precisa ser atualizado, e o registro de MCP em escopo local guarda caminho absoluto e precisa ser refeito. Por isso caminho relativo a raiz do workspace vale mais que caminho absoluto em qualquer ferramenta nova.
