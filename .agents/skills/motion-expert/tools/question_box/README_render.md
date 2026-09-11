# Caixinha de Pergunta (replica Instagram) - instrucoes de render/composicao

Entregavel do frontend-expert para o dev-expert. Visual = `question_box.html`.

## O que e
Replica fiel do sticker "Faca uma pergunta" do Instagram, em HTML/CSS, parametrizada
pelo texto da pergunta. Usada no estagio de edicao final do pipeline de motion content
para COBRIR a caixinha original (que o motion control distorce).

> ESCOPO: passo OPCIONAL. So aplicar quando o motion e nesse formato "pergunta".
> Quando o reel-base nao tem o sticker, pular (sem overlay).

## Parametros (via querystring)
- `?q=<texto urlencoded>`  -> injeta o texto da pergunta (deterministico: mesmo texto = mesmo PNG).
- `?export=1`              -> deixa o fundo da pagina transparente (sem backdrop de preview).
- `?w=<px>`                -> largura da caixa em px (default 620, sobre canvas 9:16 de 720 de largura).

O elemento a CAPTURAR e `#qbox` (so a caixa; nao a pagina).

## Render headless -> PNG transparente (recomendado: Playwright)
```
pip install playwright && playwright install chromium
```
```python
from playwright.sync_api import sync_playwright
import urllib.parse, pathlib

def render_box(texto, out_png, width=620):
    html = pathlib.Path(".agents/skills/motion-expert/tools/question_box/question_box.html").resolve().as_uri()
    url = f"{html}?export=1&w={width}&q={urllib.parse.quote(texto)}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(device_scale_factor=2)   # 2x = nitidez
        pg.goto(url)
        pg.locator("#qbox").screenshot(path=out_png, omit_background=True)  # PNG TRANSPARENTE
        b.close()
```
`omit_background=True` + capturar o `#qbox` = PNG so da caixa, com alpha. Deterministico.

> Alternativa sem Playwright: Chrome/Edge `--headless=new --screenshot` na pagina com
> `?export=1` e depois recortar a caixa. Playwright e mais limpo (captura o elemento direto).

## Composicao no video (ffmpeg) - integrar no finalize_video.py
- Overlay do PNG sobre o video do motion (2_Final/ ou 4_LipSync/).
- POSICAO = cobrir a caixinha distorcida do original. No material de hoje ela fica na faixa
  superior, ~centralizada na horizontal, topo a ~10-15% da altura. Expor `--box-pos`/`--box-scale`
  com default (ancorar topo-centro com offset Y), ajustavel por video.
- Estatica (nao animar).
- Texto DIGITADO POR VIDEO: flag tipo `--pergunta "<texto>"` (ausente = pula o overlay).
- Lote: uma pergunta por video, na ordem do dia.

## Fidelidade de emoji (DEFINIDO: Apple default, ambos selecionaveis)
Param `?emoji=apple|native` (default `apple`).
- `apple`  -> emoji estilo iPhone (IDENTICO ao original dos reels). Cada emoji vira <img>
             servido por emojicdn (`https://emojicdn.elk.sh/<emoji>?style=apple`), com
             fallback pro emoji nativo se a imagem falhar. Usa Intl.Segmenter (Chrome ok).
- `native` -> fonte do SO (Windows = Segoe UI Emoji).

ATENCAO (robustez producao): o modo `apple` depende de REDE (emojicdn) no momento do render.
- No headless, ESPERAR as imagens carregarem antes do screenshot (Playwright: `wait_until="networkidle"`
  ou aguardar os `img.emoji`). Com Chrome `--screenshot`, usar `--virtual-time-budget=5000`.
- Recomendado para producao: CACHEAR/VENDORIZAR os PNGs de emoji localmente (sao poucos por dia)
  e reapontar o `img.src` pro arquivo local, removendo a dependencia de rede.
```

## Modo STICKER FIEL (sem cobrir): validado 06/07/2026

Quando o motion cru NAO tem caixa pra cobrir (ex: reels monteiro, faceswap sem sticker),
nao usar full-width. Usar `--render-w` (largura de LAYOUT) MAIOR que `--w` (largura de
EXIBICAO): o texto se distribui no design maior e a fonte reduz no overlay, ficando
compacta e identica ao sticker do IG.

Receita validada pra motion cru **544x960** (aprovada pelo fundador):
```
--render-w 840 --w 373 --box-x 85 --box-y 133 --minh 50
```
Da uma caixa ~68% da largura, 2 linhas pra texto medio (1 linha pra texto curto), no
topo (~14% da altura). Ajustar `--render-w` pra cima = fonte menor / mais texto por linha.
Reproduzir o texto do reel VERBATIM, incluindo emoji de censura (ex: `lisi🌸a`).
