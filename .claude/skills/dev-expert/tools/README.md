# Ferramentas do dev-expert

## clonar_repo.py

Traz um repositorio Git pra dentro do workspace, de forma idempotente.

```
python .agents/skills/dev-expert/tools/clonar_repo.py <url>
python .agents/skills/dev-expert/tools/clonar_repo.py <url> --nome meu-projeto
python .agents/skills/dev-expert/tools/clonar_repo.py <url> --destino "Projetos/Dominio" --branch dev
python .agents/skills/dev-expert/tools/clonar_repo.py <url> --dry-run
```

- Destino padrao: `Projetos/Localhost/<nome-do-repo>`, com hifen ou underscore
  solto do fim do nome removido (`meu-projeto-` vira `meu-projeto`).
- Ja clonado e mesmo origin: roda `git pull --ff-only` em vez de falhar.
- Pasta ocupada por outro repo, ou com conteudo que nao e repo git: aborta com
  codigo 2, sem escrever nada por cima.
- No fim imprime branch, ultimo commit e os proximos passos deduzidos da stack
  (`requirements.txt`, `package.json`, arquivos `*.example.*` que precisam de
  credencial).

Ser colaborador de um repo e permissao de push, nao e ter o codigo na maquina:
por isso clonar continua sendo passo obrigatorio, e o push vai direto na branch,
sem fork e sem pull request.

## Validacao de codigo

As validacoes de codigo (Code Review) do dev-expert continuam sendo feitas por
analise estatica lendo os arquivos. Se lints, formatadores ou hooks forem
adotados, os scripts configuradores moram aqui.
