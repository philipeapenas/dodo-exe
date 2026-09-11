# Vault Structure (Obsidian)

**Owner:** assistente-expert

> **Regra permanente: confira no disco antes de escrever.** Este mapa envelhece porque o
> fundador reorganiza o vault sozinho, sem avisar. Um `ls` na raiz custa segundos; escrever
> nota em pasta inexistente custa a confianca dele.

## Localizacao

`Vault/` na raiz do workspace, criado pela instalacao a partir de `vault-modelo/`. Nao esta em
git - **conteudo apagado ali nao volta.** Mover e preservar, nunca deletar.

---

## Raiz (pastas de fabrica)

| Pasta | O que guarda |
| --- | --- |
| `Vida Pessoal/` | `Identidade.md` (quem ele e), `Ativos.md` (o que ele gere), `Semana/` (nota da semana) e `Rotina/<Mes>/` (autopsia do dia) |
| `Operações/` | **O centro.** Uma pasta por operacao de negocio |
| `Tarefas/` | Notas de tarefa do dia a dia, por mes e por operacao |
| `Processos/` | Processos que se repetem, por area ou OP (Regra de Ouro 22) |
| `Estudos/` | Extracao de conhecimento (dominio da estudos-expert). As notas que definem um bloco da rotina sao os neuronios (Regra de Ouro 17) |
| `Insights/` | `Insights Geral.md`, o acervo do que ele anota no dia |
| `Problemas/` | Registro de problema por area |
| `Recursos/` | `Documentos/`, `Imagens/`, `Audios/`: material de consulta |
| `Investimentos/` | Financeiro pessoal, por mes |
| `Canvas/` | Canvas do Obsidian |

**Nao existe:** pasta numerada na raiz, `_Templates/`, `Home.md`, nota diaria solta. Os modelos
de nota vivem em `memory/templates/` desta skill, nao no vault.

---

## A anatomia de uma operacao

A instalacao cria cada OP com este esqueleto. Em duvida, abra a OP mais completa do vault e copie
a forma.

```
Operações/OP <Nome>/
├── Tudo sobre <Nome> DD-MM-AA.md     nota mestre da operacao (nota_operacional_playbook.md)
├── Planos/
├── Decisões estratégicas/
├── Processos/                        registro de tarefa ARQUIVADO desta OP
├── Material/  (e Material/Imagens/)
└── Projetos/<projeto>/
    ├── 01_PRF.md                     documento de estado, como funciona HOJE
    ├── 03_Entregas/<DD-MM-AA>/       uma pasta por dia
    │   └── <slug>-DD-MM-AA.md
    └── Processos/
```

**A numeracao existe aqui dentro** (`01_PRF`, `03_Entregas`), mesmo sem existir na raiz. Nao
"corrija" isso.

### Onde cada coisa vai

| O que | Caminho |
| --- | --- |
| Nota mestre da operacao | `Operações/OP <Nome>/Tudo sobre <Nome> DD-MM-AA.md` |
| Plano | `Operações/OP <Nome>/Planos/<Titulo> DD-MM-AA.md` |
| Decisao estrategica | `Operações/OP <Nome>/Decisões estratégicas/<decisao> - <Projeto> - DD-MM-AA.md` |
| Registro de tarefa arquivado | `Operações/OP <Nome>/Processos/<Titulo> DD-MM-AA.md` |
| Documento de estado do projeto | `Operações/OP <Nome>/Projetos/<projeto>/01_PRF.md` |
| Nota de entrega | `Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/<slug>-DD-MM-AA.md` |
| Nota de tarefa **em uso** | `Tarefas/<Mes>/<OP>/<Titulo> DD-MM-AA.md` |

### Operacao que guarda varias operacoes dentro

Quando uma operacao e guarda-chuva (varias operacoes menores dentro), cada operacao menor vive
em `Operações/OP <Mae>/Projetos/<Nome da operacao>/` e **repete o esqueleto canonico inteiro um
nivel abaixo**: nota mestre, `Decisões estratégicas/`, `Planos/`, `Processos/`, `Projetos/`. O
`Processos/` dela e o dela, nao o da OP mae, e a nota do dia arquivada vai pra la.

So use esse formato quando o fundador declarar que uma operacao e projeto de outra. Operacao
propria segue o esqueleto canonico direto.

---

## Naming (as tres armadilhas)

1. **Data e `DD-MM-AA`, no FIM do nome.** Nao `YYYY-MM-DD`, nao no comeco.
2. **Entrega mora em pasta por dia** dentro de `03_Entregas/`, nao solta.
3. **Olhe o mes de destino antes de criar pasta.** O fundador pode subdividir um mes por semana
   e outro nao; o disco manda.

**Ao arquivar, preserve o nome do arquivo.** Wikilink do Obsidian resolve por nome, nao por
caminho: mover pasta nao quebra nada, **renomear quebra tudo**.

**Drift de nome na nota mestre:** notas antigas podem estar sem data ou com artigo
(`Tudo sobre a <Nome>`). A forma a seguir daqui pra frente e **`Tudo sobre <Nome> DD-MM-AA.md`**,
sem artigo. Nao renomeie as antigas: quebraria wikilink.

---

## As duas ambiguidades reais

Nao invente regra pra resolver. Na duvida, **pergunte ao fundador**: a organizacao do vault e
dominio dele, nao seu.

**1. `Projetos/` pode existir em dois lugares.** Dentro de cada OP (`Operações/OP <Nome>/Projetos/`)
e o padrao. Se o fundador criar um `Projetos/` na raiz, ele e pra trabalho que nao pertence a
nenhuma operacao (o proprio ecossistema, por exemplo).

**2. `Processos/` existe em dois lugares.** Na raiz, por area, para processo geral que atravessa
operacoes. Dentro de cada OP, para registro de tarefa **arquivado** daquela operacao.

---

## Regras de escrita

- **Wikilink `[[Nome da Nota]]`** para link interno, sempre.
- **Sem emoji** em qualquer nota (Regra de Ouro 11), inclusive em titulo e em campo de status.
- **Nota objetiva, linguagem de negocio** (Regra de Ouro 13): sem caminho de arquivo, nome de
  funcao, tabela, endpoint ou bloco de codigo.
- **Excecao unica a Regra 13: a nota de tarefa** (Regra de Ouro 16). Ali detalhe tecnico e
  permitido e desejado.
- **Nunca crie arquivo que nao seja `.md`** dentro do vault. Codigo e script ficam no
  workspace.
- **Antes de criar nota nova, procure a existente.** Se o fundador ja abriu nota pro assunto,
  o resultado vai **na nota dele**, abaixo do que ele escreveu, sem alterar o texto dele.

## Relacionados

- `auto_archive_protocol.md` - o ritual de encerramento que usa este mapa
- `nota_operacional_playbook.md` - o esqueleto da nota mestre de operacao
