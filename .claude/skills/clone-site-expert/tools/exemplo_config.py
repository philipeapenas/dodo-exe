#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Esqueleto de configuracao de limpeza. Copie para tools/ do projeto, renomeie
para limpar_<projeto>.py e preencha com os alvos daquele site.

O metodo (simular de verdade, falhar alto, conferir no fim) vive no
motor_limpeza.py e nao se reescreve. Aqui so entra o que muda de site pra site.

Uso, sempre nesta ordem:
    python tools/limpar_<projeto>.py --origem _original --destino site --conferir
    python tools/limpar_<projeto>.py --origem _original --destino site

Os alvos abaixo sao os de uma LP real feita em Atomicat + VTurb, deixados de
proposito como exemplo funcionando em vez de placeholder vazio. So a identidade
do dono original foi trocada por marcador <...>: preencha com o que o
diagnostico achar no site que voce baixou.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor_limpeza import QUALQUER, Config, Residuo, Troca, cli  # noqa: E402

# ---------------------------------------------------------------------------
# 1. Identidade do dono original. Sai do diagnostico, nunca de memoria.
# ---------------------------------------------------------------------------

PAGE_ID = "<id da pagina no construtor>"
PAGE_NAME = "<nome interno do funil do dono>"
PAGE_DOMAIN = "<dominio do dono>"

MARCADOR_SITE = "{{SITE_URL}}"
MARCADOR_TITULO = "{{TITULO}}"
MARCADOR_DESCRICAO = "{{DESCRICAO}}"

HTML = "**/*.html"
JS_PROPRIO = "**/<pasta-do-front>/js/*.js"

# ---------------------------------------------------------------------------
# 2. A configuracao
# ---------------------------------------------------------------------------

CONFIG = Config(
    nome="LP de exemplo (Atomicat + VTurb)",

    # None preserva a arvore inteira. Use o nome da pasta de dominio quando o
    # espelho tiver um dominio so e voce quiser que ele vire a raiz publicavel.
    raiz_do_site=None,

    lixo_dirs={
        "hts-cache",
        "media.atomicatmedia.net",  # og:image do dono, orfa depois da troca
    },
    lixo_files={
        "hts-log.txt",
        "backblue.gif",
        "fade.gif",
        "index.html",
        "<pagina>-duplicata.html",  # duplicata que o HTTrack gera: so o comentario difere
    },
    podar=[],

    trocas=[
        Troca(
            "A: comentario Mirrored from do HTTrack",
            re.compile(r"<!--\s*Mirrored from .*?-->\s*", re.S),
            "", 2, HTML,
        ),
        Troca(
            "B: carregador do atomicpixel.js",
            re.compile(
                r"<script[^>]*>(?:(?!</script>).)*?atomicpixel(?:(?!</script>).)*?</script>",
                re.S,
            ),
            "", 1, HTML,
        ),
        Troca(
            "C: og:url corrompido pelo HTTrack",
            re.compile(r'<meta property="og:url" content="[^"]*">'),
            f'<meta property="og:url" content="{MARCADOR_SITE}">', 1, HTML,
        ),
        Troca(
            "C: og:image no CDN do dono",
            re.compile(r'<meta property="og:image" content="[^"]*">'),
            f'<meta property="og:image" content="{MARCADOR_SITE}/og.png">', 1, HTML,
        ),
        Troca(
            "C: placeholder de title deixado pelo dono",
            re.compile(r"<title>.*?</title>", re.S),
            f"<title>{MARCADOR_TITULO}</title>", 1, HTML,
        ),
        Troca(
            "C: placeholder de description deixado pelo dono",
            re.compile(r'<meta name="description" content="[^"]*">'),
            f'<meta name="description" content="{MARCADOR_DESCRICAO}">', 1, HTML,
        ),
        # A identidade tambem mora nos atributos do body. Este alvo escapou da
        # lista inicial na primeira vez e so a conferencia final pegou.
        Troca(
            "C: identidade Atomicat nos atributos do body",
            re.compile(
                r'(<body[^>]*?)\s*data-page-version="[^"]*"'
                r'(.*?)\s*data-variant="[^"]*"'
                r'(.*?)\s*data-page="[^"]*"',
                re.S,
            ),
            r"\1\2\3", 1, HTML,
        ),
        # Beacon de erro: preserva o nome exportado, esvazia o corpo. Quem
        # chamar continua chamando e nada e enviado.
        Troca(
            "B: beacon de erro Atomicat",
            re.compile(r"!function\(\)\{try\{const t=\{pageId:.*?\}\(\);\s*$", re.S),
            '!function(){"undefined"!=typeof window&&'
            '(window.atomiReportError=function(){})}();',
            1, JS_PROPRIO,
        ),
    ],

    # Se qualquer um sobrar na versao limpa, o motor derruba a execucao.
    # Nao liste aqui o que voce decidiu MANTER: nesta LP o player VTurb fica,
    # por decisao do fundador, entao converteai e vturb estao fora da lista.
    residuos=[
        Residuo("pageId do dono", PAGE_ID),
        Residuo("nome interno do funil", PAGE_NAME),
        Residuo("dominio do dono", PAGE_DOMAIN),
        Residuo("rastreador atomicpixel", "atomicpixel"),
        Residuo("endpoint de telemetria Atomicat", "apido.atomicat-api.com"),
        Residuo("comentario do HTTrack", "Mirrored from"),
        Residuo("rodape do HTTrack", "Added by HTTrack"),
    ],
)


if __name__ == "__main__":
    sys.exit(cli(CONFIG))
