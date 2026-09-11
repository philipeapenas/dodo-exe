# Playbook de Publicacao na Vercel

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** clone-site-expert

Espelho editado a mao quebra premissas que a Vercel assume sobre projeto Next de verdade. Estas sao as tres que mordem.

---

## 1. A armadilha do cache immutable (a que mais dói)

Num build real do Next, cada arquivo em `_next/static` nasce com o hash do proprio conteudo no nome. Por isso e correto servir com:

```json
{ "source": "/_next/static/(.*)",
  "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] }
```

**Num espelho editado a mao essa premissa e falsa.** O conteudo muda e o nome fica igual. Com `immutable`, o navegador guarda o arquivo por um ano e **nem pergunta** se mudou. O visitante recebe o HTML novo com o JavaScript velho, e na hidratacao o React reescreve a pagina com o conteudo antigo.

O sintoma engana: o servidor esta certo, o arquivo servido esta certo, e o fundador continua vendo o valor antigo ao recarregar.

**A correcao e devolver a premissa**, nao remover o cabecalho: rode `carimbar_versao.py` antes de cada deploy. Ele deriva um carimbo do conteudo e o insere no nome (`page-abc123.v56692566.js`). Nome novo, URL nova, cache antigo nao se aplica.

Como ele e derivado do conteudo, rodar duas vezes seguidas nao muda nada - so muda quando algum arquivo mudou de verdade.

> **Cuidado de implementacao, que ja falhou:** o padrao que remove o carimbo antigo **nao pode ter ancora de fim de texto**. Com `$`, ele casa com o nome do arquivo mas nunca com a referencia no meio do HTML - os arquivos sao renomeados, as referencias ficam apontando pro carimbo velho, e o site sobe sem CSS e sem JS.

Arquivo fora de `_next/static` (CSS proprio, script proprio, favicon) recebe da Vercel `max-age=0, must-revalidate` e nao sofre disso.

---

## 2. `cleanUrls` e a estrutura mista

O HTTrack salva `briefing.html`, mas o site original linkava `/briefing`. E o **bundle React continua gerando `/briefing`** - se o HTML apontar pro `.html`, a hidratacao vai divergir.

```json
{ "cleanUrls": true, "trailingSlash": false }
```

Com isso `/briefing` serve o arquivo e `/briefing.html` responde 308 pro extensionless. **Alinhe os links do HTML no formato sem extensao**, pra bater com o bundle e evitar o salto de redirect.

**A armadilha:** `cleanUrls` se comporta mal quando o espelho mistura `arquivo.html` com `pasta/index.html`. Confira a estrutura antes de ligar. Espelho de site simples costuma ser plano e seguro.

---

## 3. Nada de CDN

Biblioteca vai **servida do proprio projeto**, nunca de CDN. Vale pro que ja vem no espelho e pro que voce adicionar depois. Copie de um projeto irmao que ja tenha o arquivo, em vez de baixar de novo.

---

## O ritual de deploy

```
1. carimbar_versao.py        (sempre, antes de tudo)
2. conferir_referencias.py   (sem pipe)
3. conferir_classes.py       (sem pipe)
4. node --check em cada .js editado
5. vercel deploy --prod --yes
6. provar por curl
```

**O passo 6 nao e opcional.** Prove:

- cada rota (`/`, as internas, uma inexistente devolvendo 404)
- **cada arquivo que o HTML pede**, extraindo a lista do HTML servido em vez de conferir de cabeca
- os rastros do dono ausentes no que esta sendo servido
- formulario que grava em servico externo: teste o **preflight de CORS** e o POST com o `Origin` do dominio publicado. E o que quebra so no navegador, e voce nao veria de outro jeito

**Nunca canalize validador pra outro comando.** O pipe engole o codigo de saida: `validador | tail` seguido de `&& deploy` publica build quebrada. Ja aconteceu.

---

## Publicou? Entao o projeto muda de pasta (Regra de Ouro 9)

**No mesmo turno em que o site vai ao ar, o projeto sai de `Projetos/Localhost/` e vai pra `Projetos/Dominio/`.** Nao e arrumacao pra depois: projeto publicado morando em `Localhost/` e mentira no nome da pasta, e quem abrir o workspace depois nao tem como saber que aquilo esta no ar.

**O gatilho e o deploy publico, nao o dominio pago.** Subdominio gratuito `.vercel.app` ja conta - o site esta acessivel pra qualquer pessoa na internet, que e o unico criterio que importa.

O ritual da promocao:

1. Mover com `robocopy /MOVE /R:10 /W:2`, nunca `Move-Item` - robocopy tolera lock de file watcher.
2. **Aproveitar pra corrigir o nome da pasta.** Espelho costuma herdar o nome da marca do DONO ORIGINAL, que e exatamente o que a higienizacao passou a sessao inteira removendo. A pasta tem que levar o nome da nossa operacao, sem espaco e sem acento.
3. **Garantir o repositorio proprio no GitHub** - ver o bloco abaixo.
4. Criar `tools/backup.bat` (modelo em `Agente Orquestrador/tools/backup_projeto.bat`).
5. Varrer o workspace inteiro pelo caminho antigo e atualizar cada referencia: nota do vault, `Resumo do projeto/`, memoria de skill, memoria do agente. Referencia orfa vira link morto.
6. Conferir que o vinculo com a Vercel sobreviveu (`.vercel/project.json` continua valendo, o CLI reconhece e o site responde 200).
7. Acrescentar a pasta ao `.gitignore` da raiz, **depois** do passo 3. Se o projeto ainda era rastreado pelo dodo-company, rodar tambem `git rm -r --cached <caminho>`: o `.gitignore` sozinho nao para de rastrear arquivo ja rastreado.

### O repositorio proprio (passo 3)

**Nao e pendencia do fundador.** Voce verifica, cria e envia no mesmo turno.

```
gh repo list --limit 100 | grep <nome>
gh repo create <nome> --private --source=. --remote=origin --push
```

Convencao `<usuario-do-github>/<nome-da-pasta>`, **privado por padrao**.

**Antes de enviar, varra por segredo e confira o PAPEL de cada token achado.** Num clone higienizado a chave `anon` do Supabase aparece dentro do HTML e do JS do formulario: ela e publica por natureza e pode ir. `service_role` **nunca** pode. A palavra "service_role" tambem aparece em comentario de SQL e em nota de resumo sem ser chave nenhuma - olhe o payload do JWT antes de concluir qualquer coisa.

O `.gitignore` do projeto exclui pelo menos `.vercel/` e `__pycache__/`.

E natural que `_original/` (o espelho cru do concorrente) va junto: e material de comparacao documentado no PRF, e o repositorio e privado.

---

## O que voce nao consegue verificar

Aparencia, animacao e comportamento de clique. **Diga isso explicitamente** ao entregar, e aponte o que o fundador precisa olhar. Afirmar que "esta funcionando" sem ter visto e o tipo de erro que custa confianca.
