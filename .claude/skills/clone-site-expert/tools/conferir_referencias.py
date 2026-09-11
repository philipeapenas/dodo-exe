"""
Confere se todo arquivo citado no HTML existe de verdade no disco.

Nasceu de um erro real: na limpeza o polyfills.js foi apagado como peso morto,
mas a tag <script> que apontava pra ele ficou. Resultado, um 404 em toda carga
da home. Nao apareceu no teste da epoca porque a pagina respondia 200 - o que
ninguem conferiu foi se CADA arquivo citado por ela respondia.

Uso:
    python tools/conferir_referencias.py site
"""

import re
import sys
from pathlib import Path

# src= e href= apontando para arquivo local (ignora http, mailto, ancora)
REFERENCIA = re.compile(r'(?:src|href)="(?!https?:|mailto:|#|data:)([^"]+)"')
EXTENSOES = {".js", ".css", ".png", ".svg", ".woff2", ".jpg", ".webp", ".ico"}


def main() -> int:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    faltando: list[tuple[str, str]] = []
    total = 0

    for documento in sorted(base.rglob("*")):
        if documento.suffix not in {".html", ".css"}:
            continue
        texto = documento.read_text(encoding="utf-8")

        for bruto in REFERENCIA.findall(texto):
            caminho = bruto.split("?")[0].split("#")[0]
            if Path(caminho).suffix not in EXTENSOES:
                continue
            total += 1
            alvo = (base / caminho.lstrip("/")) if caminho.startswith("/") \
                else (documento.parent / caminho)
            if not alvo.exists():
                faltando.append((str(documento.relative_to(base)), bruto))

        # url(...) dentro de CSS
        if documento.suffix == ".css":
            for bruto in re.findall(r'url\(([^)]+)\)', texto):
                caminho = bruto.strip('\'"').split("?")[0]
                if caminho.startswith(("http", "data:")):
                    continue
                total += 1
                if not (documento.parent / caminho).exists():
                    faltando.append((str(documento.relative_to(base)), bruto))

    print(f"{total} referencias conferidas em {base}\n")
    for onde, qual in faltando:
        print(f"  QUEBRADA  {onde} -> {qual}")

    if faltando:
        print(f"\nERRO: {len(faltando)} referencia(s) apontam para arquivo que nao existe.")
        return 1
    print("Todo arquivo citado existe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
