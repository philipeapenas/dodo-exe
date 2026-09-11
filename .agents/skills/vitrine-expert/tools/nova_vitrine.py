"""Gerador de esqueleto de vitrine (site de cliente montado em tempo fixo).

Recebe o briefing de um cliente em JSON e emite o projeto inteiro pronto para a
etapa de julgamento: pastas, bibliotecas de movimento, backup.bat, cronometro ja
rodando, e o index.html com os dados reais nos blocos deterministicos.

O que ele NAO faz, de proposito: a copy (mecanismo unico, dor, beneficios) e a
leitura da paleta a partir do logo. Essas duas dependem de julgamento e saem da
copywriter-expert e da frontend-expert. O gerador deixa o lugar marcado, nunca
inventa o texto.

O GABARITO e a primeira vitrine, montada a mao pela esteira. Dela saem o CSS, o
movimento.js, as bibliotecas e o backup.bat de todas as seguintes.

Uso:
    python nova_vitrine.py briefing.json --gabarito Projetos/Dominio/<primeira-vitrine>
    python nova_vitrine.py briefing.json --gabarito <...> --forcar  # sobrescreve projeto existente
    python nova_vitrine.py --exemplo > briefing.json  # cospe um briefing de exemplo
"""

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# A raiz do workspace: quatro niveis acima de .agents/skills/vitrine-expert/tools/
RAIZ = Path(__file__).resolve().parents[4]
# Definido pelo --gabarito em main(): a primeira vitrine que a esteira montou a mao.
GABARITO_PROJETO = None
MODELO_BACKUP = RAIZ / "Agente Orquestrador" / "tools" / "backup_projeto.bat"
GABARITO_TEMPLATES = Path(__file__).resolve().parent / "gabarito"
DESTINO_BASE = RAIZ / "Projetos" / "Dominio"

SVG_WHATSAPP = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2c-5.46 0-9.9 4.44-9.9 9.9 0 '
    '1.75.46 3.45 1.32 4.95L2.05 22l5.3-1.38a9.86 9.86 0 0 0 4.69 1.19c5.46 0 9.9-4.44 9.9-9.9S17.5 2 12.04 2Zm5.8 '
    '14c-.24.68-1.4 1.3-1.94 1.35-.5.05-1.13.07-1.82-.11-.42-.11-.96-.29-1.65-.59-2.9-1.25-4.8-4.17-4.94-4.36-.15-.2'
    '-1.18-1.57-1.18-3s.75-2.13 1.02-2.42c.27-.29.58-.36.78-.36h.56c.18 0 .42-.07.66.5.24.59.83 2.02.9 2.17.07.15.12'
    '.32.02.51-.1.2-.15.32-.29.49-.15.17-.31.38-.44.51-.15.15-.3.31-.13.6.17.29.76 1.25 1.63 2.02 1.12.99 2.06 1.3 '
    '2.35 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.7.8 1.99.95.29.15.48.22.55.34.07.13'
    '.07.71-.17 1.39Z"/></svg>'
)

# Icone neutro por servico. Nao ha desenho por nicho: escolher icone e julgamento
# visual, e o gerador nao faz julgamento. A frontend-expert troca depois.
SVG_SELO = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
    'stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/></svg>'
)

# Paleta neutra de partida. NAO e a paleta final: a real sai do logo do cliente,
# na etapa E3. Os nomes ficam iguais aos do gabarito para o CSS nao quebrar.
TEMA_PADRAO = {
    "fundo": "#F7F5F3",
    "marca": "#8A8A8A",
    "marca_escuro": "#5F5F5F",
    "marca_claro": "#E8E6E4",
    "texto": "#2C2C2C",
    "texto_claro": "#6A6A6A",
    "assinatura": "#9A9A9A",
    "display": "Fraunces",
    "corpo": "Karla",
    "url_fontes": (
        "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;"
        "1,9..144,300..500&family=Karla:wght@400;500;700&display=swap"
    ),
}

BRIEFING_EXEMPLO = {
    "negocio": "Studio Exemplo | Estética",
    "nome": "Studio Exemplo",
    "whatsapp": "11999990000",
    "cidade": "São Paulo, SP",
    "tipo_negocio": "salao",
    "modelo_negocio": "local",
    "instagram": "https://www.instagram.com/studio_exemplo/",
    "servicos": [
        "Corte e tratamento capilar",
        "Tratamento corporal",
        "Depilação",
        "Esmaltação",
    ],
    "logo": "<caminho do logo>.jpg",
    "tema": TEMA_PADRAO,
}

OBRIGATORIOS = ("negocio", "whatsapp", "servicos", "modelo_negocio")
MODELOS_VALIDOS = ("local", "movel", "ambos")


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------

def criar_slug(texto):
    """Nome de pasta seguro: sem acento, sem espaco (Regra de Ouro 9)."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = sem_acento.encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower()
    return re.sub(r"-{2,}", "-", limpo) or "cliente"


def escapar(texto):
    """Escapa o que vai para dentro de atributo ou corpo de HTML."""
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def marcar(texto):
    """Envolve texto de exemplo no marcador amarelo.

    Todo trecho que passa por aqui e visivel na pagina como pendencia e conta
    para o portao de publicacao: enquanto existir UM, o noindex e a barra de
    aviso ficam.
    """
    return '<span class="exemplo">{}</span>'.format(escapar(texto))


def numero_e164(whatsapp):
    """Normaliza para o formato que o wa.me aceita: 55 + DDD + numero."""
    digitos = re.sub(r"\D", "", str(whatsapp))
    if not digitos:
        raise ValueError("whatsapp sem digito nenhum")
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    if len(digitos) < 12 or len(digitos) > 13:
        raise ValueError(
            "whatsapp com {} digitos apos normalizar ({}); esperado 12 ou 13 "
            "no formato 55 + DDD + numero".format(len(digitos), digitos)
        )
    return digitos


def exibir_whatsapp(e164):
    """(21) 97669-0278 a partir de 5521976690278."""
    nacional = e164[2:]
    ddd, resto = nacional[:2], nacional[2:]
    return "({}) {}-{}".format(ddd, resto[:-4], resto[-4:])


def link_zap(e164, mensagem):
    return "https://wa.me/{}?text={}".format(e164, quote(mensagem))


def handle_instagram(url):
    """Extrai @handle de uma URL de perfil. Devolve None se nao der."""
    if not url:
        return None
    achado = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", str(url))
    if achado:
        return achado.group(1).strip("/")
    texto = str(url).strip().lstrip("@")
    return texto or None


# ---------------------------------------------------------------------------
# Geradores de bloco
# ---------------------------------------------------------------------------

def montar_servicos(servicos, e164):
    """Um cartao por servico do briefing, cada um com o seu proprio link."""
    partes = []
    for servico in servicos:
        titulo = escapar(servico)
        link = link_zap(e164, "Oi! Vim pelo site, queria saber sobre {}".format(servico))
        partes.append(
            '        <article class="card-servico">\n'
            '          <span class="selo-arco" aria-hidden="true">{selo}</span>\n'
            "          <h3>{titulo}</h3>\n"
            "          <p>{descricao}</p>\n"
            '          <a class="btn btn-contorno btn-bloco" href="{link}" data-zap>Ver horários</a>\n'
            "        </article>".format(
                selo=SVG_SELO,
                titulo=titulo,
                descricao=marcar("DESCREVER {} em 1 ou 2 frases".format(servico.upper())),
                link=link,
            )
        )
    return "\n".join(partes)


def montar_cards_simples(quantidade, rotulo):
    partes = []
    for indice in range(1, quantidade + 1):
        partes.append(
            '        <div class="card">\n'
            "          <h3>{titulo}</h3>\n"
            "          <p>{corpo}</p>\n"
            "        </div>".format(
                titulo=marcar("{} {}".format(rotulo, indice)),
                corpo=marcar("O que muda na vida do cliente. Transformacao, nunca funcionalidade."),
            )
        )
    return "\n".join(partes)


def montar_lista(quantidade, texto):
    return "\n".join(
        "          <li>{}</li>".format(marcar("{} {}".format(texto, i)))
        for i in range(1, quantidade + 1)
    )


def montar_galeria(quantidade=4):
    return "\n".join(
        '        <div class="vaga-foto">FOTO {}<br>trabalho real</div>'.format(i)
        for i in range(1, quantidade + 1)
    )


def montar_depoimentos(quantidade=3):
    partes = []
    for _ in range(quantidade):
        partes.append(
            '        <div class="depoimento">\n'
            "          <blockquote>{citacao}</blockquote>\n"
            "          <cite>{autor}</cite>\n"
            "        </div>".format(
                citacao=marcar("DEPOIMENTO DE EXEMPLO: substituir por elogio real de cliente"),
                autor=marcar("NOME DO CLIENTE: serviço feito"),
            )
        )
    return "\n".join(partes)


def montar_acordeao(itens):
    """itens: lista de (pergunta, resposta_html)."""
    return "\n".join(
        '        <details class="acordeao">\n'
        "          <summary>{}</summary>\n"
        "          <p>{}</p>\n"
        "        </details>".format(escapar(pergunta), resposta)
        for pergunta, resposta in itens
    )


def montar_objecoes(modelo):
    """A objecao de lugar muda conforme o negocio atende onde."""
    itens = [
        (
            "Nunca fui aí. E se eu não gostar do resultado?",
            marcar("RESPOSTA: como voce alinha a expectativa antes de comecar o servico."),
        ),
        (
            "Vou ter que esperar muito?",
            marcar("RESPOSTA: como funciona o horario marcado."),
        ),
    ]
    if modelo in ("local", "ambos"):
        itens.append((
            "É longe de mim?",
            marcar("ENDEREÇO COMPLETO + referência de bairro") + ". " +
            marcar("Adicionar link do mapa."),
        ))
    if modelo in ("movel", "ambos"):
        itens.append((
            "Vocês atendem na minha região?",
            marcar("LISTAR os bairros ou cidades atendidos."),
        ))
    return montar_acordeao(itens)


def montar_faq(modelo):
    itens = [
        ("Preciso marcar ou posso chegar?", marcar("RESPOSTA")),
        ("Como eu marco?", "Pelo WhatsApp. Você manda o que precisa e a gente acha o melhor dia."),
        ("Dá pra fazer mais de um serviço no mesmo dia?", marcar("RESPOSTA")),
        ("Quanto tempo demora?", marcar("RESPOSTA")),
        ("Quais as formas de pagamento?", marcar("CONFIRMAR: Pix, cartão, dinheiro")),
    ]
    if modelo in ("local", "ambos"):
        itens.insert(4, ("Qual o endereço?", marcar("ENDEREÇO COMPLETO")))
        itens.insert(5, ("Qual o horário de funcionamento?", marcar("HORÁRIO, dia a dia")))
    if modelo in ("movel", "ambos"):
        itens.insert(4, ("Como funciona o atendimento?", marcar("EXPLICAR o atendimento a distância ou no local do cliente")))
    return montar_acordeao(itens)


def montar_rodape_onde(modelo):
    linhas = []
    if modelo in ("local", "ambos"):
        linhas.append("        <p>{}</p>".format(marcar("ENDEREÇO COMPLETO")))
        linhas.append("        <p>{}</p>".format(marcar("HORÁRIO, dia a dia")))
    if modelo in ("movel", "ambos"):
        linhas.append("        <p>{}</p>".format(marcar("REGIÕES ATENDIDAS")))
    return "\n".join(linhas)


def montar_paragrafos(quantidade, texto, estilo_primeiro=True):
    partes = []
    for indice in range(quantidade):
        estilo = ' style="margin-top:1.5rem"' if indice == 0 and estilo_primeiro else ""
        partes.append("      <p{}>{}</p>".format(estilo, marcar(texto)))
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Escrita dos arquivos
# ---------------------------------------------------------------------------

def escrever_css(destino, tema):
    """Copia o CSS do gabarito trocando SO o bloco :root.

    O gabarito e a unica fonte de verdade do sistema visual. Regerar o CSS
    inteiro aqui criaria uma segunda copia que envelhece sozinha.
    """
    origem = GABARITO_PROJETO / "assets" / "css" / "style.css"
    css = origem.read_text(encoding="utf-8")

    substituicoes = {
        "--fundo": tema["fundo"],
        "--marca": tema["marca"],
        "--marca-escura": tema["marca_escuro"],
        "--marca-clara": tema["marca_claro"],
        "--texto": tema["texto"],
        "--texto-suave": tema["texto_claro"],
        "--assinatura": tema["assinatura"],
    }
    for token, valor in substituicoes.items():
        css = re.sub(
            r"(\n\s*{}\s*:\s*)#[0-9A-Fa-f]{{3,8}}\s*;".format(re.escape(token)),
            r"\g<1>{};".format(valor),
            css,
            count=1,
        )

    css = re.sub(r'(--display:\s*)"[^"]+"', r'\g<1>"{}"'.format(tema["display"]), css, count=1)
    css = re.sub(r'(--corpo:\s*)"[^"]+"', r'\g<1>"{}"'.format(tema["corpo"]), css, count=1)

    aviso = (
        "/* PALETA DE PARTIDA - TROCAR NA ETAPA E3.\n"
        "   Os valores abaixo vieram do briefing ou do padrao neutro do gerador.\n"
        "   A paleta real sai do LOGO do cliente, por julgamento da frontend-expert.\n"
        "   Reusar a paleta de outro cliente e erro (regra da vitrine-expert). */\n\n"
    )
    (destino / "assets" / "css" / "style.css").write_text(aviso + css, encoding="utf-8")


def escrever_html(destino, dados):
    template = (GABARITO_TEMPLATES / "index.template.html").read_text(encoding="utf-8")
    for chave, valor in dados.items():
        template = template.replace("{{%s}}" % chave, str(valor))

    sobrando = re.findall(r"\{\{([A-Z_]+)\}\}", template)
    if sobrando:
        raise RuntimeError(
            "template ficou com token nao substituido: {}".format(sorted(set(sobrando)))
        )
    (destino / "index.html").write_text(template, encoding="utf-8")


def escrever_backup_bat(destino, slug):
    origem = GABARITO_PROJETO / "tools" / "backup.bat"
    if not origem.exists():
        origem = MODELO_BACKUP
    if not origem.exists():
        return
    conteudo = origem.read_text(encoding="utf-8", errors="replace")
    conteudo = conteudo.replace(GABARITO_PROJETO.name, slug)
    (destino / "tools" / "backup.bat").write_text(conteudo, encoding="utf-8")


def escrever_json_projeto(destino, briefing, slug, agora):
    cronometro = {
        "cliente": briefing.get("negocio"),
        "nicho": briefing.get("tipo_negocio"),
        "modelo_negocio": briefing.get("modelo_negocio"),
        "data": agora.strftime("%Y-%m-%d"),
        "inicio": agora.isoformat(timespec="seconds"),
        "fim": None,
        "observacao": "Esqueleto gerado por nova_vitrine.py. O relogio conta do briefing 2 completo.",
        "etapas": [
            {"id": "E1", "nome": "Material do cliente", "responsavel": "vitrine-expert",
             "inicio": agora.isoformat(timespec="seconds"), "fim": None},
            {"id": "E2", "nome": "Copy", "responsavel": "copywriter-expert", "inicio": None, "fim": None},
            {"id": "E3", "nome": "Direcao visual", "responsavel": "frontend-expert", "inicio": None, "fim": None},
            {"id": "E4", "nome": "HTML e CSS", "responsavel": "frontend-expert", "inicio": None, "fim": None},
            {"id": "E5", "nome": "JS", "responsavel": "dev-expert", "inicio": None, "fim": None},
            {"id": "E6", "nome": "Deploy Vercel", "responsavel": "vercel-expert", "inicio": None, "fim": None},
            {"id": "E7", "nome": "Entrega", "responsavel": "vitrine-expert", "inicio": None, "fim": None},
        ],
    }
    mensagens = {
        "projeto": slug,
        "operacao": briefing.get("operacao") or "Vitrine",
        "briefing": briefing,
        "mensagens": [],
    }
    pasta = destino / "Resumo do projeto"
    (pasta / "cronometro.json").write_text(
        json.dumps(cronometro, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "mensagens.json").write_text(
        json.dumps(mensagens, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "registro_atividades.json").write_text(
        json.dumps({"projeto": slug, "trilhas": []}, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Orquestracao
# ---------------------------------------------------------------------------

def validar(briefing):
    faltando = [c for c in OBRIGATORIOS if not briefing.get(c)]
    if faltando:
        raise ValueError("briefing sem campo obrigatorio: {}".format(", ".join(faltando)))
    if briefing["modelo_negocio"] not in MODELOS_VALIDOS:
        raise ValueError(
            "modelo_negocio invalido: {!r}. Use um de {}".format(
                briefing["modelo_negocio"], MODELOS_VALIDOS)
        )
    if not isinstance(briefing["servicos"], list) or not briefing["servicos"]:
        raise ValueError("servicos precisa ser uma lista com pelo menos um item")


def gerar(briefing, forcar=False):
    validar(briefing)

    if GABARITO_PROJETO is None or not GABARITO_PROJETO.exists():
        raise RuntimeError(
            "gabarito nao encontrado ({}). Passe --gabarito com a pasta da primeira "
            "vitrine, montada a mao pela esteira.".format(GABARITO_PROJETO))

    slug = briefing.get("slug") or criar_slug(briefing["negocio"])
    destino = DESTINO_BASE / slug
    if destino.exists():
        if not forcar:
            raise RuntimeError(
                "{} ja existe. Use --forcar para sobrescrever "
                "(o conteudo atual sera perdido).".format(destino)
            )
        shutil.rmtree(destino)

    agora = datetime.now()
    e164 = numero_e164(briefing["whatsapp"])
    modelo = briefing["modelo_negocio"]
    tema = dict(TEMA_PADRAO)
    tema.update(briefing.get("tema") or {})

    for sub in ("assets/css", "assets/js/vendor", "assets/img", "tools", "Resumo do projeto"):
        (destino / sub).mkdir(parents=True, exist_ok=True)

    # Bibliotecas de movimento: copiadas do gabarito, nunca de CDN.
    for arquivo in (GABARITO_PROJETO / "assets" / "js" / "vendor").glob("*.js"):
        shutil.copy2(arquivo, destino / "assets" / "js" / "vendor" / arquivo.name)
    shutil.copy2(
        GABARITO_PROJETO / "assets" / "js" / "movimento.js",
        destino / "assets" / "js" / "movimento.js",
    )

    ext_logo = ".png"
    logo_origem = briefing.get("logo")
    logo_copiado = False
    if logo_origem and Path(logo_origem).exists():
        ext_logo = Path(logo_origem).suffix.lower() or ".png"
        shutil.copy2(logo_origem, destino / "assets" / "img" / ("logo" + ext_logo))
        logo_copiado = True

    escrever_css(destino, tema)
    escrever_backup_bat(destino, slug)
    escrever_json_projeto(destino, briefing, slug, agora)

    negocio = briefing["negocio"]
    cidade = briefing.get("cidade") or ""
    arroba = handle_instagram(briefing.get("instagram"))
    partes_marca = [p.strip() for p in re.split(r"[|\-–]", negocio) if p.strip()]
    marca_nome = partes_marca[0] if partes_marca else negocio
    marca_sub = partes_marca[1] if len(partes_marca) > 1 else (briefing.get("tipo_negocio") or "")

    linha_instagram = ""
    rodape_instagram = ""
    if arroba:
        linha_instagram = (
            '      <p style="text-align:center;margin-top:2rem">\n'
            '        Todo dia tem trabalho novo no <a href="https://www.instagram.com/{a}/" '
            'target="_blank" rel="noopener"><strong>@{a}</strong></a>.\n'
            "      </p>\n".format(a=escapar(arroba))
        )
        rodape_instagram = (
            '        <p><a href="https://www.instagram.com/{a}/" target="_blank" '
            'rel="noopener">@{a}</a></p>'.format(a=escapar(arroba))
        )

    dados = {
        "NEGOCIO": escapar(negocio),
        "CIDADE_SUFIXO": " - " + escapar(cidade) if cidade else "",
        "META_DESCRICAO": escapar(
            "{}{}. {}. Marque pelo WhatsApp.".format(
                negocio, " em " + cidade if cidade else "",
                ", ".join(briefing["servicos"][:4]))
        ),
        "URL_BASE": "https://{}.vercel.app".format(slug),
        "URL_FONTES": tema["url_fontes"],
        "EXT_LOGO": ext_logo,
        "MIME_LOGO": "image/jpeg" if ext_logo in (".jpg", ".jpeg") else "image/png",
        "COR_FUNDO": tema["fundo"],
        "MARCA_NOME": escapar(marca_nome),
        "MARCA_SUB": escapar(marca_sub),
        "SVG_WHATSAPP": SVG_WHATSAPP,
        "WHATSAPP_EXIBICAO": exibir_whatsapp(e164),
        "ZAP_TOPO": link_zap(e164, "Oi! Vim pelo site e queria marcar um horário"),
        "ZAP_VALORES": link_zap(e164, "Oi! Vim pelo site, queria saber os valores"),
        "ZAP_TRABALHOS": link_zap(e164, "Oi! Vi os trabalhos no site e queria marcar"),
        "ZAP_FINAL": link_zap(e164, "Oi! Quero marcar meu horário"),
        "ZAP_SIMPLES": "https://wa.me/{}".format(e164),
        "CTA_PRIMARIO": "Agendar no WhatsApp",
        "CTA_SECUNDARIO": "Quero marcar meu horário",
        "CTA_MICROCOPY": "Chama que a gente vê o melhor dia pra você.",
        "HEADLINE": marcar("HEADLINE: promessa específica, até 8 palavras (copywriter-expert)"),
        "SUBHEADLINE": marcar("SUBHEADLINE: o contexto que sustenta a headline"),
        "TITULO_ABERTURA": marcar("TÍTULO DA ABERTURA"),
        "ABERTURA_PARAGRAFOS": montar_paragrafos(3, "PARÁGRAFO DE ABERTURA: dor, solução, promessa"),
        "DOR_ITENS": montar_lista(5, "DOR"),
        "TITULO_MECANISMO": marcar("MECANISMO ÚNICO: por que aqui e não no concorrente"),
        "MECANISMO_PARAGRAFOS": montar_paragrafos(2, "PARÁGRAFO DO MECANISMO ÚNICO"),
        "BENEFICIOS_CARDS": montar_cards_simples(6, "BENEFÍCIO"),
        "GRADE_SERVICOS": "grade-4" if len(briefing["servicos"]) >= 4 else "grade-3",
        "SERVICOS_CARDS": montar_servicos(briefing["servicos"], e164),
        "TEXTO_PRECO": marcar(
            "TEXTO DE PREÇO: o valor depende de quê. Nunca publicar tabela sem o cliente pedir."),
        "GALERIA": montar_galeria(),
        "DEPOIMENTOS": montar_depoimentos(),
        "LINHA_INSTAGRAM": linha_instagram,
        "OBJECOES": montar_objecoes(modelo),
        "TITULO_COMPROMISSO": marcar("TÍTULO DO COMPROMISSO"),
        "COMPROMISSO_PARAGRAFOS": montar_paragrafos(2, "COMPROMISSO: como o risco volta pro prestador"),
        "FAQ": montar_faq(modelo),
        "CTA_FINAL_TITULO": marcar("CTA FINAL: o último empurrão"),
        "CTA_FINAL_TEXTO": marcar("TEXTO DO CTA FINAL"),
        "RODAPE_RESUMO": escapar(", ".join(briefing["servicos"][:4])),
        "RODAPE_ONDE_TITULO": "Onde" if modelo == "local" else "Atendimento",
        "RODAPE_ONDE": montar_rodape_onde(modelo),
        "RODAPE_INSTAGRAM": rodape_instagram,
    }
    escrever_html(destino, dados)

    return destino, slug, logo_copiado, arroba


def main():
    # No Windows o console usa cp1252 por padrao: sem isto, `--exemplo > b.json`
    # grava um arquivo que nao e UTF-8 e a propria ferramenta nao consegue reler.
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Gera o esqueleto de uma vitrine.")
    parser.add_argument("briefing", nargs="?", help="caminho do JSON do briefing")
    parser.add_argument("--forcar", action="store_true", help="sobrescreve projeto existente")
    parser.add_argument("--exemplo", action="store_true", help="imprime um briefing de exemplo")
    parser.add_argument("--gabarito", help="pasta da vitrine que serve de gabarito (ex: Projetos/Dominio/<primeira>)")
    args = parser.parse_args()

    global GABARITO_PROJETO
    if args.gabarito:
        GABARITO_PROJETO = Path(args.gabarito).resolve()

    if args.exemplo:
        print(json.dumps(BRIEFING_EXEMPLO, ensure_ascii=False, indent=2))
        return 0

    if not args.briefing:
        parser.error("informe o caminho do briefing, ou use --exemplo")

    caminho = Path(args.briefing)
    if not caminho.exists():
        print("Briefing nao encontrado: {}".format(caminho), file=sys.stderr)
        return 1

    try:
        briefing = json.loads(caminho.read_text(encoding="utf-8"))
        destino, slug, logo_copiado, arroba = gerar(briefing, forcar=args.forcar)
    except (ValueError, RuntimeError, OSError) as erro:
        print("ERRO: {}".format(erro), file=sys.stderr)
        return 1

    print("Projeto criado: {}".format(destino))
    print()
    print("O que o gerador ja resolveu:")
    print("  - estrutura de pastas, backup.bat e os 3 arquivos de Resumo do projeto")
    print("  - bibliotecas de movimento e movimento.js copiados do gabarito")
    print("  - CSS do gabarito com a paleta de partida aplicada")
    print("  - index.html com os {} servicos, os links de WhatsApp e os blocos "
          "do modelo '{}'".format(len(briefing["servicos"]), briefing["modelo_negocio"]))
    print("  - cronometro iniciado na etapa E1")
    if logo_copiado:
        print("  - logo copiado para assets/img/")
    print()
    print("O que FALTA, e depende de julgamento:")
    if not logo_copiado:
        print("  ! LOGO NAO COPIADO - sem ele nao ha direcao visual (E3)")
    if not arroba:
        print("  ! sem Instagram no briefing - a pagina perdeu a prova continua")
    print("  1. E2 copy: todo trecho marcado em amarelo (copywriter-expert)")
    print("  2. E3 paleta e tipografia tiradas do LOGO (frontend-expert)")
    print("  3. material do cliente: fotos de trabalho, depoimentos, endereco e horario")
    print()
    print("PORTAO DE PUBLICACAO: enquanto houver UM marcador amarelo, o noindex")
    print("e a barra de aviso do topo FICAM. Sair, saem os dois juntos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
