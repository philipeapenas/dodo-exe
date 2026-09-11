"""
Confere se todas as classes usadas no HTML existem no CSS compilado.

O CSS veio do Tailwind com purga: classe que o site original nao usava
simplesmente nao esta la. Escrever HTML novo com uma classe podada gera
elemento sem estilo, e nada no navegador avisa. Este script avisa.

Uso:
    python tools/conferir_classes.py site
"""

import re
import sys
from pathlib import Path


def classes_do_css(pasta_css: Path) -> set[str]:
    disponiveis: set[str] = set()
    for css in pasta_css.glob("*.css"):
        texto = css.read_text(encoding="utf-8")
        # Seletor de classe, com os escapes que o Tailwind usa (\: \/ \[ \] \.)
        for bruto in re.findall(r"\.((?:[\w-]|\\.)+)", texto):
            disponiveis.add(re.sub(r"\\(.)", r"\1", bruto))
    return disponiveis


def classes_do_html(arquivo: Path) -> set[str]:
    texto = arquivo.read_text(encoding="utf-8")
    usadas: set[str] = set()
    for valor in re.findall(r'class="([^"]*)"', texto):
        usadas.update(c for c in valor.split() if c)
    return usadas


def main() -> int:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    disponiveis = classes_do_css(base / "_next" / "static" / "css")
    print(f"{len(disponiveis)} classes disponiveis no CSS compilado\n")

    faltando_total = 0
    for html in sorted(base.glob("*.html")):
        usadas = classes_do_html(html)
        faltando = sorted(usadas - disponiveis)
        marca = "OK" if not faltando else f"{len(faltando)} SEM ESTILO"
        print(f"  {html.name:<18} {len(usadas):>3} classes usadas  ->  {marca}")
        for c in faltando:
            print(f"      falta: {c}")
        faltando_total += len(faltando)

    print()
    if faltando_total:
        print(f"ERRO: {faltando_total} classe(s) sem regra no CSS.")
        return 1
    print("Todas as classes usadas existem no CSS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
