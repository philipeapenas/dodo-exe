"""
Carimba uma versao no nome dos arquivos estaticos que a gente edita a mao.

POR QUE ISSO EXISTE
-------------------
Num build de verdade do Next, cada arquivo em _next/static nasce com o hash do
proprio conteudo no nome. Por isso e seguro servir com "immutable": mudou o
conteudo, mudou o nome, e o navegador busca de novo sozinho.

Aqui o site e um espelho editado a mao: o conteudo muda e o nome fica igual.
Com o cabecalho "immutable" isso vira armadilha - o navegador guarda o arquivo
por um ano e NEM PERGUNTA se mudou. O visitante recebe o HTML novo com o
JavaScript velho, e na hidratacao o React reescreve a pagina com o conteudo
antigo.

Este script devolve a garantia que o cabecalho "immutable" pressupoe: o nome
do arquivo passa a depender do conteudo. Roda antes de todo deploy.

COMO FUNCIONA
-------------
1. Tira o carimbo antigo dos nomes e das referencias (volta ao estado base).
2. Calcula um carimbo unico a partir do conteudo de TODOS os arquivos.
3. Insere o carimbo nos nomes e em toda referencia a eles.

E deterministico: rodar duas vezes seguidas nao muda nada. So muda o carimbo
quando algum arquivo realmente mudou.

Uso:
    python tools/carimbar_versao.py site
"""

import hashlib
import re
import sys
from pathlib import Path

# Pastas cujo conteudo a gente edita. As fontes em media/ nunca sao editadas,
# entao mantem o nome original do build e seguem validas como immutable.
PASTAS = ["_next/static/chunks", "_next/static/css"]
EXTENSOES = {".js", ".css"}
# Sem ancora de fim de texto: este mesmo padrao precisa casar tanto com um
# nome de arquivo solto ("app.vabc12345.js") quanto com a referencia no meio
# do HTML ("...app.vabc12345.js\"). Com "$" no fim, ele so casava com o nome,
# os arquivos eram renomeados e as referencias ficavam apontando pro carimbo
# velho - o site subia sem CSS e sem JS.
CARIMBO = re.compile(r"\.v[0-9a-f]{8}(?=\.(?:js|css)(?![\w-]))")


def arquivos(base: Path) -> list[Path]:
    achados: list[Path] = []
    for pasta in PASTAS:
        alvo = base / pasta
        if alvo.is_dir():
            achados += [f for f in sorted(alvo.rglob("*")) if f.suffix in EXTENSOES]
    return achados


def texto_editavel(base: Path) -> list[Path]:
    return [f for f in sorted(base.rglob("*")) if f.suffix in {".html", ".js", ".css"}]


def sem_carimbo(nome: str) -> str:
    return CARIMBO.sub("", nome)


def main() -> int:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    estaticos = arquivos(base)
    if not estaticos:
        sys.exit(f"ERRO: nao achei arquivo estatico em {base}")

    # -- 1. voltar ao estado base, tirando carimbo de nome e de referencia
    renomeados: list[Path] = []
    for f in estaticos:
        limpo = f.with_name(sem_carimbo(f.name))
        if limpo != f:
            f.rename(limpo)
        renomeados.append(limpo)

    for doc in texto_editavel(base):
        original = doc.read_text(encoding="utf-8")
        limpo = CARIMBO.sub("", original)
        if limpo != original:
            doc.write_text(limpo, encoding="utf-8")

    # -- 2. carimbo derivado do conteudo de todos eles somados
    resumo = hashlib.sha256()
    for f in sorted(renomeados):
        resumo.update(f.name.encode("utf-8"))
        resumo.update(f.read_bytes())
    carimbo = resumo.hexdigest()[:8]
    print(f"carimbo desta versao: v{carimbo}\n")

    # -- 3. aplicar nos nomes e em toda referencia
    trocas = {f.name: f"{f.stem}.v{carimbo}{f.suffix}" for f in renomeados}

    alterados = 0
    for doc in texto_editavel(base):
        original = doc.read_text(encoding="utf-8")
        novo = original
        for antigo, atual in trocas.items():
            novo = novo.replace(antigo, atual)
        if novo != original:
            doc.write_text(novo, encoding="utf-8")
            alterados += 1
            print(f"  referencias atualizadas em {doc.relative_to(base)}")

    for f in renomeados:
        f.rename(f.with_name(trocas[f.name]))
    print(f"\n{len(renomeados)} arquivo(s) renomeado(s), {alterados} documento(s) atualizado(s).")

    # -- conferencia: nenhuma referencia pode apontar pra nome sem carimbo
    pendentes = []
    for doc in texto_editavel(base):
        conteudo = doc.read_text(encoding="utf-8")
        for antigo in trocas:
            if re.search(re.escape(antigo).replace(r"\.", r"\.(?!v[0-9a-f]{8}\.)"), conteudo):
                pendentes.append((doc.name, antigo))
    if pendentes:
        for onde, qual in pendentes:
            print(f"  SOBROU referencia sem carimbo: {onde} -> {qual}")
        return 1

    print("Toda referencia aponta para o nome carimbado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
