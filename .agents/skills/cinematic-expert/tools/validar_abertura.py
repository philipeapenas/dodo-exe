# ═══════════════════════════════════════════════════════════
#  validar_abertura.py - confere a leitura do texto da abertura
#  cinematografica SOBRE A IMAGEM, nos dois formatos.
#
#  POR QUE ESTA FERRAMENTA EXISTE
#  Na abertura, o texto nao assenta em cor chapada: assenta em foto, e em foto
#  que MUDA (a cena avanca conforme a rolagem). Auditor de paleta nao serve
#  aqui, porque ele mede cor contra cor e o que vale e a cor real da imagem
#  naquela altura, coberta pelo que estiver entre ela e a letra.
#
#  AS TRES REGRAS QUE ELA CARREGA, todas vindas de erro real no primeiro site
#  cinematografico entregue:
#
#  1. MEDE ONDE O TEXTO ESTA. Quando o bloco de texto mudou de lugar e a
#     ferramenta continuou medindo o centro, ela passou a REPROVAR medindo o
#     pedaco onde o texto nao estava mais. Mentira com cara de reprovacao
#     legitima. Por isso a faixa de amostragem e declarada POR FORMATO, e sai da
#     conta do layout.
#  2. SEQUENCIA SE MEDE PELO PIOR QUADRO, nunca pela media. Fundo que se mexe
#     nao pode viver na margem: um subtitulo em 4.52:1 contra o minimo de 4.5
#     passa no papel e falha na tela.
#  3. QUANDO NAO CONSEGUE MEDIR, AVISA E NAO APROVA. Conferencia que se cala
#     quando falha e pior do que conferencia nenhuma.
#
#  COMO USAR
#      python validar_abertura.py [caminho/do/projeto]
#
#  O projeto precisa ter um `abertura.json` na raiz. Veja o exemplo no fim
#  deste arquivo.
#
#  As cores podem ser hex literal ("#B03E63") ou o nome de uma variavel do CSS
#  do projeto ("--azul-fundo") - assim a paleta nao vive em dois lugares.
# ═══════════════════════════════════════════════════════════

import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    print('FALTA a biblioteca Pillow. Instale com:  pip install pillow')
    sys.exit(2)


# ── Contraste (WCAG) ───────────────────────────────────────
def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(cor):
    v = [x / 255 for x in cor]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def razao(a, b):
    la, lb = luminancia(a), luminancia(b)
    claro, escuro = (la, lb) if la > lb else (lb, la)
    return (claro + 0.05) / (escuro + 0.05)


def empilhar(base, camadas):
    """Cobre a cor da imagem com as camadas que existem entre ela e a letra.

    A ORDEM IMPORTA e e sempre de baixo pra cima: imagem -> vidro do botao ->
    sombra da propria letra. Medir so a primeira da um numero pior do que a tela
    entrega; medir so a ultima, melhor.
    """
    for cor, cobertura in camadas:
        base = tuple(round(cobertura * cor[i] + (1 - cobertura) * base[i]) for i in range(3))
    return base


# ── Amostragem ─────────────────────────────────────────────
# Grade em vez de media: um assunto escuro atras de duas palavras nao move a
# media da faixa inteira, mas derruba a leitura naquele pedaco. Vale o PIOR.
COLUNAS, LINHAS = 8, 3


def pior_celula(imagem, y0, y1, x0f, x1f, tintas, camadas):
    """Celula de menor contraste da faixa. `tintas` e uma lista: a peca esta
    separada do fundo se QUALQUER uma delas contrastar o bastante (o caso de um
    botao com duas cores de borda)."""
    largura, altura = imagem.size
    x0, x1 = int(x0f * largura), int(x1f * largura)
    ya, yb = int(y0 * altura), int(y1 * altura)
    passo_x = max(1, (x1 - x0) // COLUNAS)
    passo_y = max(1, (yb - ya) // LINHAS)

    pior, cor_pior = None, None
    for cx in range(x0, x1, passo_x):
        for cy in range(ya, yb, passo_y):
            caixa = (cx, cy, min(cx + passo_x, x1), min(cy + passo_y, yb))
            if caixa[2] <= caixa[0] or caixa[3] <= caixa[1]:
                continue
            cor = imagem.crop(caixa).resize((1, 1), Image.LANCZOS).getpixel((0, 0))
            fundo = empilhar(cor, camadas)
            r = max(razao(fundo, t) for t in tintas)
            if pior is None or r < pior:
                pior, cor_pior = r, fundo
    return pior, cor_pior


def carregar_imagens(raiz, fonte, amostras):
    """Aceita um arquivo de imagem ou uma PASTA com a sequencia da cena.

    Numa pasta, pega `amostras` quadros espalhados do comeco ao fim - nao so o
    primeiro, que e justamente o quadro em que nada aconteceu ainda.
    """
    caminho = os.path.join(raiz, fonte)
    if os.path.isdir(caminho):
        nomes = sorted(n for n in os.listdir(caminho)
                       if n.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
        if not nomes:
            return None, 'a pasta %s esta vazia' % fonte
        if len(nomes) > amostras:
            passo = (len(nomes) - 1) / (amostras - 1)
            nomes = [nomes[round(i * passo)] for i in range(amostras)]
        return [Image.open(os.path.join(caminho, n)).convert('RGB') for n in nomes], None
    if os.path.exists(caminho):
        return [Image.open(caminho).convert('RGB')], None
    return None, 'nao encontrei %s' % fonte


# ── Paleta do proprio CSS ──────────────────────────────────
def ler_paleta(raiz, css_rel):
    """Le as variaveis de cor do CSS do projeto, pra paleta nao viver em dois
    lugares. Sem isso, mudar uma cor no CSS deixaria esta conferencia medindo a
    cor antiga e aprovando o que nao existe mais."""
    import re
    caminho = os.path.join(raiz, css_rel)
    if not os.path.exists(caminho):
        return {}
    texto = open(caminho, encoding='utf-8').read()
    return {m[0]: m[1] for m in re.findall(r'--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})', texto)}


def resolver(cor, paleta):
    """'--azul-fundo' vira a cor do CSS; '#B03E63' fica como esta."""
    if isinstance(cor, str) and cor.startswith('--'):
        nome = cor[2:]
        if nome not in paleta:
            raise KeyError('a variavel %s nao existe no CSS do projeto' % cor)
        return rgb(paleta[nome])
    return rgb(cor)


# ── Execucao ───────────────────────────────────────────────
def main():
    raiz = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    config_path = os.path.join(raiz, 'abertura.json')
    if not os.path.exists(config_path):
        print('Nao achei abertura.json em %s' % raiz)
        print('Ele descreve os formatos da abertura, as faixas de texto e o que')
        print('cobre cada uma. Veja o exemplo no fim de validar_abertura.py.')
        sys.exit(2)

    config = json.load(open(config_path, encoding='utf-8'))
    paleta = ler_paleta(raiz, config.get('css', 'assets/css/style.css'))

    reprovacoes = 0
    avisos = []

    for formato in config['formatos']:
        nome = formato['nome']
        imagens, erro = carregar_imagens(raiz, formato['fonte'], formato.get('amostras', 9))
        if imagens is None:
            avisos.append('%s NAO foi medido: %s. Este e o fundo real da '
                          'abertura nesse formato - sem medir, nada aqui prova nada.'
                          % (nome, erro))
            print('\n== %s ==  PULADO (ver aviso no fim)' % nome)
            continue

        x0f, x1f = formato['coluna']
        quantos = ', %d quadros' % len(imagens) if len(imagens) > 1 else ''
        print('\n== %s ==  (faixa em x: %.2f a %.2f%s)' % (nome, x0f, x1f, quantos))

        for faixa in formato['faixas']:
            tintas = [resolver(t, paleta) for t in faixa['tintas']]
            camadas = [(resolver(c[0], paleta), c[1]) for c in faixa.get('camadas', [])]
            minimo = faixa.get('minimo', 4.5)
            y0, y1 = faixa['y']

            # Com mais de uma imagem, vale o PIOR quadro.
            pior, cor_pior = None, None
            for imagem in imagens:
                r, cor = pior_celula(imagem, y0, y1, x0f, x1f, tintas, camadas)
                if pior is None or r < pior:
                    pior, cor_pior = r, cor

            passou = pior >= minimo
            if not passou:
                reprovacoes += 1
            cobertura = ' + '.join('%.0f%%' % (c[1] * 100) for c in camadas) or 'sem cobertura'
            print('  %s %5.2f:1 (min %.1f)  %-10s  pior pedaco #%02X%02X%02X  (%s)'
                  % ('OK   ' if passou else 'FALHA', pior, minimo, faixa['nome'],
                     cor_pior[0], cor_pior[1], cor_pior[2], cobertura))

    for aviso in avisos:
        print('\n!! %s' % aviso)

    if reprovacoes == 0 and not avisos:
        print('\nTUDO PASSA na leitura do texto sobre a imagem')
    elif reprovacoes == 0:
        print('\nO que foi medido passa, MAS ha formato sem medir - nao trate como aprovado')
    else:
        print('\n%d REPROVACAO(OES) na leitura do texto sobre a imagem' % reprovacoes)

    # Formato sem medir tambem sai diferente de zero: aprovar em silencio o que
    # nao foi conferido e o unico erro que esta ferramenta nao pode cometer.
    sys.exit(1 if (reprovacoes or avisos) else 0)


if __name__ == '__main__':
    main()


# ═══════════════════════════════════════════════════════════
#  EXEMPLO DE abertura.json
#
#  {
#    "css": "assets/css/style.css",
#    "formatos": [
#      {
#        "nome": "computador - cena",
#        "fonte": "assets/img/hero-cena",
#        "amostras": 9,
#        "coluna": [0.10, 0.63],
#        "faixas": [
#          { "nome": "headline",  "y": [0.27, 0.40], "tintas": ["--azul-fundo"],
#            "camadas": [["#FFFFFF", 0.55]] },
#          { "nome": "botao", "y": [0.56, 0.65], "tintas": ["#FFFFFF"],
#            "camadas": [["#A93058", 0.68], ["#3B0F1F", 0.35]] }
#        ]
#      }
#    ]
#  }
#
#  COMO ESCOLHER OS NUMEROS, que e onde se erra:
#
#  `coluna`  faixa HORIZONTAL onde o texto assenta, em fracao da largura. Sai da
#            conta do layout, nao de tentativa. Ex: wrap de 1120 centrado em
#            tela de 1440 abre o texto em 182 (=0.126), e um teto de 24ch em
#            fonte de ~50px termina perto de 902 (=0.626).
#            Bloco centralizado costuma ser [0.24, 0.76].
#
#  `y`       faixa VERTICAL de cada peca, em fracao da altura. Sai do print
#            real da pagina, proporcionalizado. Refaca quando a altura da secao
#            ou o tamanho do texto mudar - senao a ferramenta mede o lugar
#            errado e "reprova" o que esta certo.
#
#  `camadas` tudo que fica ENTRE a imagem e a letra, de baixo pra cima:
#            - texto com halo  -> [["#FFFFFF", 0.55]]  (a cobertura equivalente
#              do text-shadow; se mexer no CSS, mexa aqui junto)
#            - botao de vidro  -> [[cor do vidro, cobertura], [cor da sombra da
#              letra, cobertura]]
#            Estes numeros sao LEITURA DO CSS, nunca alvo independente.
# ═══════════════════════════════════════════════════════════
