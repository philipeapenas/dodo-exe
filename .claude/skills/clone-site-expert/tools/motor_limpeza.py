#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Motor de higienizacao de site baixado. Implementa o METODO; cada projeto
escreve so a CONFIGURACAO.

O metodo, conforme memory/higienizacao_playbook.md:

  1. Modo --conferir simula de verdade: aplica as trocas em memoria, valida as
     contagens e NAO escreve nada. Erro de padrao aparece antes de tocar arquivo.
  2. Toda troca declara a contagem esperada. Se nao bater, o motor para e nao
     escreve. Troca que casa zero vezes e rastreador que ficou.
  3. Conferencia final varre o resultado atras dos rastros do dono. E ela que
     autoriza dizer "limpo".

Para usar, escreva um script de projeto que monta uma Config e chama cli().
Copie `exemplo_config.py` como ponto de partida.

Historico: nasceu da refatoracao do antigo `limpar_httrack.py`, que estava
amarrado ao primeiro site clonado e cujo modo --conferir pulava todas as etapas
de limpeza, nunca chegando a validar padrao nenhum.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Contagem esperada: um numero exato, ou uma destas palavras.
QUALQUER = "qualquer"   # pelo menos uma ocorrencia
OPCIONAL = "opcional"   # pode nao existir, mas se existir e trocada


@dataclass
class Troca:
    """Uma substituicao, com a contagem que se espera dela.

    padrao aceita str (tratada como literal) ou re.Pattern.
    onde e um glob relativo a raiz do site (ex: "**/*.html").
    """

    rotulo: str
    padrao: object
    substituto: str
    esperado: object = QUALQUER
    onde: str = "**/*.html"

    def compilado(self) -> re.Pattern:
        if isinstance(self.padrao, re.Pattern):
            return self.padrao
        return re.compile(re.escape(str(self.padrao)))


@dataclass
class Residuo:
    """Algo do dono original que nao pode sobrar na versao limpa."""

    rotulo: str
    agulha: str


@dataclass
class Config:
    nome: str

    # Pasta de dominio que vira a raiz publicavel. None preserva a arvore
    # inteira, que e o certo quando o espelho tem CDN em pasta separada.
    raiz_do_site: str | None = None

    lixo_dirs: set = field(default_factory=set)
    lixo_files: set = field(default_factory=set)

    # Globs de arquivos a descartar depois da copia (peso morto).
    podar: list = field(default_factory=list)

    trocas: list = field(default_factory=list)
    residuos: list = field(default_factory=list)

    # Extensoes varridas na conferencia final.
    extensoes_texto: set = field(
        default_factory=lambda: {".html", ".htm", ".js", ".css", ".json", ".txt"}
    )


class Relatorio:
    def __init__(self, conferir: bool):
        self.conferir = conferir
        self.linhas: list[str] = []
        self.erros: list[str] = []
        self.bytes_removidos = 0

    def ok(self, msg: str) -> None:
        self.linhas.append(f"  [ok]   {msg}")

    def erro(self, msg: str) -> None:
        self.erros.append(msg)
        self.linhas.append(f"  [ERRO] {msg}")

    def imprimir(self, titulo: str) -> None:
        print(f"\n{titulo}")
        for linha in self.linhas:
            print(linha)
        if self.bytes_removidos:
            print(f"\n  Peso descartado: {self.bytes_removidos / 1024:.1f} KB")


def _domain_dirs(origem: Path, cfg: Config) -> list[Path]:
    return [
        d for d in sorted(origem.iterdir())
        if d.is_dir() and d.name not in cfg.lixo_dirs
    ]


def resolver_raiz(origem: Path, cfg: Config, rel: Relatorio) -> Path:
    """Decide o que vira a raiz do site copiado.

    Sem raiz_do_site declarada, preserva a arvore inteira. Espelho com mais de
    uma pasta de dominio e o normal, nao a excecao: qualquer pagina que carregue
    player ou imagem de outro servidor vem assim.
    """
    if cfg.raiz_do_site is None:
        pastas = _domain_dirs(origem, cfg)
        rel.ok(
            f"raiz: arvore inteira preservada "
            f"({len(pastas)} pasta(s) de dominio: {', '.join(d.name for d in pastas)})"
        )
        return origem

    raiz = origem / cfg.raiz_do_site
    if not raiz.is_dir():
        disponiveis = ", ".join(d.name for d in _domain_dirs(origem, cfg)) or "(nenhuma)"
        rel.erro(
            f"raiz_do_site '{cfg.raiz_do_site}' nao existe em {origem}. "
            f"Pastas disponiveis: {disponiveis}"
        )
        return origem
    rel.ok(f"raiz do site: {cfg.raiz_do_site}/ (vira a raiz publicavel)")
    return raiz


def _rel_posix(caminho: Path, raiz: Path) -> str:
    return str(caminho.relative_to(raiz)).replace("\\", "/")


def casa(relativo: str, glob: str) -> bool:
    """Casamento de glob em que '**/' aceita ZERO pastas.

    No fnmatch puro, '**/*.html' exige ao menos uma pasta no caminho e por isso
    NAO casa com um 'index.html' na raiz. Numa configuracao com raiz_do_site,
    onde a pasta de dominio vira a raiz, isso faria a pagina principal escapar
    de todas as trocas em silencio - o pior modo de falhar.
    """
    if fnmatch.fnmatch(relativo, glob):
        return True
    if glob.startswith("**/"):
        return fnmatch.fnmatch(relativo, glob[3:])
    return False


def _descarte(caminho: Path, raiz: Path, cfg: Config) -> str | None:
    """Motivo pelo qual o arquivo nao entra na versao limpa, ou None se entra."""
    relativo = caminho.relative_to(raiz)
    if any(parte in cfg.lixo_dirs for parte in relativo.parts):
        return "pasta de lixo"
    if caminho.name in cfg.lixo_files:
        return "lixo do HTTrack"
    if any(casa(_rel_posix(caminho, raiz), g) for g in cfg.podar):
        return "peso morto"
    return None


def sobreviventes(raiz: Path, cfg: Config) -> list[Path]:
    """Os arquivos que entram na versao limpa.

    Uma unica fonte de verdade para a copia E para as trocas. Sem isso as duas
    etapas divergem: as trocas contam ocorrencias em arquivo que a copia
    descartou, e as contagens esperadas passam a acusar o dobro do real.
    """
    return [
        f for f in sorted(raiz.rglob("*"))
        if f.is_file() and _descarte(f, raiz, cfg) is None
    ]


def copiar_sem_lixo(raiz: Path, destino: Path, cfg: Config, rel: Relatorio) -> None:
    copiados = descartados = 0

    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file():
            continue
        relativo = caminho.relative_to(raiz)
        motivo = _descarte(caminho, raiz, cfg)

        if motivo:
            rel.bytes_removidos += caminho.stat().st_size
            descartados += 1
            if motivo != "pasta de lixo":  # a pasta e reportada inteira, abaixo
                rel.ok(f"{motivo}, fora: {relativo}")
            continue

        copiados += 1
        if not rel.conferir:
            alvo = destino / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(caminho, alvo)

    for pasta in sorted(cfg.lixo_dirs):
        if (raiz / pasta).exists():
            rel.ok(f"lixo do HTTrack, fora: {pasta}/ (pasta inteira)")

    rel.ok(f"arquivos copiados: {copiados}")
    rel.ok(f"arquivos descartados: {descartados}")


def aplicar_trocas(raiz: Path, cfg: Config, rel: Relatorio) -> dict[Path, str]:
    """Aplica as trocas EM MEMORIA e valida cada contagem.

    Roda igual em simulacao e em aplicacao: e isso que faz o --conferir valer.
    Devolve o texto final por arquivo; quem grava e o chamador.
    """
    textos: dict[Path, str] = {}

    vivos = sobreviventes(raiz, cfg)

    for troca in cfg.trocas:
        padrao = troca.compilado()
        alvos = [
            f for f in vivos
            if casa(_rel_posix(f, raiz), troca.onde)
        ]
        if not alvos:
            rel.erro(f"{troca.rotulo}: nenhum arquivo casa com '{troca.onde}'")
            continue

        total = 0
        for arquivo in alvos:
            if arquivo not in textos:
                try:
                    textos[arquivo] = arquivo.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
            achados = len(padrao.findall(textos[arquivo]))
            if achados:
                textos[arquivo] = padrao.sub(troca.substituto, textos[arquivo])
                total += achados

        if troca.esperado == QUALQUER:
            if total == 0:
                rel.erro(f"{troca.rotulo}: esperava pelo menos 1 ocorrencia, achei 0")
                continue
        elif troca.esperado == OPCIONAL:
            pass
        elif total != troca.esperado:
            rel.erro(
                f"{troca.rotulo}: esperava {troca.esperado} ocorrencia(s), achei {total}"
            )
            continue

        rel.ok(f"{troca.rotulo}: {total} trocada(s)")

    return textos


def conferir_residuos(site: Path, cfg: Config, rel: Relatorio) -> None:
    achados = []
    for caminho in sorted(site.rglob("*")):
        if not caminho.is_file() or caminho.suffix not in cfg.extensoes_texto:
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for residuo in cfg.residuos:
            if residuo.agulha in conteudo:
                achados.append(
                    f"{residuo.rotulo} ainda presente em {caminho.relative_to(site)}"
                )

    if achados:
        for item in achados:
            rel.erro(item)
    else:
        rel.ok(
            f"conferencia final: nenhum dos {len(cfg.residuos)} rastros do dono sobrou"
        )


def executar(cfg: Config, origem: Path, destino: Path, conferir: bool) -> int:
    rel = Relatorio(conferir)
    modo = "SIMULACAO (nada sera escrito)" if conferir else "APLICANDO"

    if not origem.is_dir():
        print(f"ERRO: origem nao existe: {origem}", file=sys.stderr)
        return 1

    raiz = resolver_raiz(origem, cfg, rel)
    if rel.erros:
        rel.imprimir(f"=== {cfg.nome} | {modo}: FALHOU ===")
        return 1

    if not conferir:
        if destino.exists():
            shutil.rmtree(destino)
        destino.mkdir(parents=True, exist_ok=True)

    copiar_sem_lixo(raiz, destino, cfg, rel)

    # As trocas rodam sobre a origem, para que a simulacao seja fiel.
    textos = aplicar_trocas(raiz, cfg, rel)

    if rel.erros:
        if not conferir and destino.exists():
            shutil.rmtree(destino)
        rel.imprimir(f"=== {cfg.nome} | {modo}: FALHOU ===")
        print(f"\n{len(rel.erros)} problema(s). Nada foi escrito.")
        return 1

    if conferir:
        rel.imprimir(f"=== {cfg.nome} | {modo}: OK ===")
        print("\nSimulacao passou limpa. Rode sem --conferir para aplicar.")
        return 0

    for arquivo, texto in textos.items():
        alvo = destino / arquivo.relative_to(raiz)
        if alvo.exists():
            alvo.write_text(texto, encoding="utf-8")

    conferir_residuos(destino, cfg, rel)

    if rel.erros:
        # Falha nao deixa resultado pela metade no disco: um site meio limpo,
        # ainda com rastro do dono, e um convite a publicar por engano.
        shutil.rmtree(destino)
        rel.imprimir(f"=== {cfg.nome} | {modo}: FALHOU NA CONFERENCIA FINAL ===")
        print("\nO destino foi descartado. Nada meio limpo fica no disco.")
        return 1

    rel.imprimir(f"=== {cfg.nome} | {modo}: OK ===")
    print(f"\nVersao limpa em: {destino}")
    return 0


def cli(cfg: Config, argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=f"Higienizacao: {cfg.nome}")
    p.add_argument("--origem", required=True, help="pasta crua do HTTrack")
    p.add_argument("--destino", required=True, help="pasta da versao limpa")
    p.add_argument("--conferir", action="store_true", help="simula, nao escreve nada")
    args = p.parse_args(argv)
    return executar(
        cfg, Path(args.origem).resolve(), Path(args.destino).resolve(), args.conferir
    )
