# Playbook de Portabilidade - Exportar Skill pra Fora do Ecossistema

**Versao:** 1.0 | **Data:** 06/09/2026 | **Owner:** skill-expert
**Origem:** a primeira exportacao real, de duas skills de criacao de site empacotadas pra um time de devs. Este playbook destila o processo que funcionou, pra nao ser reinventado a cada pedido novo.

Acione quando o fundador pedir pra empacotar, disponibilizar, exportar ou "dar" uma ou mais skills pra um time, cliente ou workspace que NAO e o Dodo.exe. Ex: "quero criar uma pasta com as skills de X pro meu time de devs", "monta um pacote da skill Y pra mandar pro cliente".

**Objetivo:** entregar a skill FUNCIONANDO sozinha em qualquer workspace de Claude Code, sem depender de nenhum arquivo, skill ou convencao que so existe aqui dentro.

---

## Passo 1 - Escopo

Pergunte, se nao vier claro no pedido:

1. **Quais skills exatamente entram.** Nao adivinhe por proximidade tematica, confirme a lista.
2. **Solta/portatil (sem nenhum acoplamento ao ecossistema) ou copia identica com a infra junto?** A segunda opcao so faz sentido se o destino tambem vai rodar o protocolo de mensagens inteiro (raro, e mais caro pra manter). Portatil e o default.

## Passo 2 - Ler skill por skill, arquivo por arquivo

Antes de cortar qualquer coisa, leia o `SKILL.md` inteiro e TODOS os arquivos de `memory/` e `tools/` de cada skill que vai no pacote. Nao adivinhe o que e generico pelo nome do arquivo, leia o conteudo.

## Passo 3 - Classificar cada arquivo/trecho em 3 baldes

- **GENERICO** (mantem, edicao minima): conhecimento tecnico de verdade, valido em qualquer projeto (ex: cascata de CSS, Clean Code, checklist de self-review, tecnica de animacao de scroll).
- **ADAPTAVEL** (mantem, mas reescreve): referencia um caminho, convencao de pasta ou nome de skill que nao vai no pacote, mas a ideia de fundo e boa. Reescreve genericamente (ex: "devolva pra copywriter-expert" vira "peca a copy aprovada antes de desenhar").
- **INTERNO** (remove por completo): protocolo de mensagens, `mensagens.json`, `registro_atividades.json`, `regras_de_ouro.md`, handoff pra `skill-expert`/`ceo-dodo`/qualquer skill que nao vai no pacote, vault do Obsidian (`Vault/`), IP ou credencial de infra (VPS, chave, token), conteudo de UM projeto/cliente especifico que nao generaliza (design tokens de um produto so, prompts amarrados a paginas de um cliente so).

**Teste rapido pra decidir GENERICO/ADAPTAVEL vs INTERNO:** se eu apagar o nome do cliente/projeto desse arquivo, ele ainda ensina alguma coisa que serve em qualquer lugar? Se sim, e generico ou adaptavel, reescreve. Se o arquivo INTEIRO so faz sentido pra aquele projeto especifico, e INTERNO, remove o arquivo inteiro (nao tente salvar 10% dele).

**Nunca deixe passar:** IP de servidor, token, e-mail interno, nome de cliente real fora do escopo do pedido. Esses vazam mesmo quando o resto do arquivo e generico, procure neles com atencao redobrada.

## Passo 4 - Reescrever o `SKILL.md` de cada skill

Remove sempre:

- A secao inteira "Protocolo do Ecossistema" (`mensagens.json`, `registro_atividades.json`).
- O "Passo 0: Carregar Protocolo de Mensagens" da Cadeia de Pensamento.
- Qualquer "envie help pro skill-expert" ou handoff pra skill que nao vai no pacote.
- Referencia a Regra de Ouro numerada, reescreve o CONTEUDO da regra como principio direto, sem citar o numero (o numero so faz sentido aqui dentro).

Mantem, adaptado:

- Objetivo Estrategico.
- Conexao de Recursos, apontando so pros arquivos que sobreviveram ao Passo 3.
- Cadeia de Pensamento, renumerada sem o Passo 0, com qualquer trava que citava outra skill reescrita em termos genericos (ex: "cliente/stakeholder" no lugar de "fundador").

## Passo 5 - Escrever o pacote de distribuicao

Estrutura fixa, sempre a mesma, pra qualquer exportacao:

```
<nome-do-pacote>/
├── README.md         humano: o que e, o que tem dentro, requisito
├── INSTALAR.md        agente: instrucoes que o dev manda direto pra IA dele executar
├── install.ps1         instalador Windows (PowerShell)
├── install.sh           instalador Mac/Linux/Git Bash
└── skills/
    └── <skill>/
        ├── SKILL.md
        ├── memory/
        └── tools/
```

O instalador copia cada `skills/<nome>` pra `<projeto-do-dev>/.claude/skills/<nome>`, faz backup (`.bak`) se ja existir algo com o mesmo nome ali, e nao mexe em mais nada do projeto. **Teste rodando de verdade** num diretorio de teste antes de entregar, instalacao limpa E reinstalacao (pra confirmar que o backup funciona). Nao entregue instalador sem ter rodado.

O `INSTALAR.md` e escrito como instrucao direta pra uma IA de codigo executar (passo numerado, comando exato, criterio de "deu certo"), nao como texto explicativo. O mesmo arquivo serve pra leitura humana.

## Passo 6 - Varredura final (obrigatoria antes de entregar)

Rode grep no pacote inteiro atras de vazamento de acoplamento interno:

```bash
grep -rEli "regras_de_ouro|mensagens\.json|registro_atividades|skill-expert|Vault/|ceo-dodo|fundador|<qualquer IP ou credencial de infra>|<nomes de skill que NAO entraram no pacote>" <pasta-do-pacote>
```

Silencio (nenhum arquivo listado) e o criterio de pronto. Qualquer resultado e vazamento, corrige antes de entregar. Nao pule este passo mesmo quando a edicao pareceu completa, ele ja pegou vazamento que a leitura visual deixou passar.

## Passo 7 - Repositorio proprio (quando o pedido for nutrir ao longo do tempo)

Se o fundador quer ir atualizando o pacote com o tempo (nao e uma entrega unica), o pacote ganha repositorio Git proprio, seguindo o mesmo ritual da Regra de Ouro 9 (projeto com repositorio dedicado):

1. Pasta vive em `Projetos/Dominio/<nome-sem-espaco-sem-acento>/`.
2. `gh repo create <usuario-do-github>/<nome> --private --source=. --remote=origin --push` (privado por padrao, mesma convencao dos outros projetos; publico so se pedido explicitamente).
3. Adicionar o caminho ao `.gitignore` raiz do Dodo.exe, na secao "Projetos com repositorio dedicado".
4. `tools/backup.bat` no padrao dos outros projetos de `Projetos/Dominio/` (adaptar: sem etapa de publicacao Vercel se o pacote nao publica nada, so `git add -A && commit && push`).

## Relacionadas

* Regra de Ouro 9 (projeto com repositorio dedicado).
* Regra de Ouro 8 (so skill-expert edita `SKILL.md` e `memory/*.md`).
* Regra de Ouro 1 (Regra do Ecossistema Onisciente, upskill antes de contratar skill nova).
