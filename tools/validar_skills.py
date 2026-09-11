# -*- coding: utf-8 -*-
"""Confere o cabecalho de cada skill contra o padrao Agent Skills.

O Claude Code tolera cabecalho torto; o Codex e o Antigravity podem simplesmente
nao carregar a skill. Rode depois de criar ou editar qualquer SKILL.md.

Regras conferidas:
  * o cabecalho YAML entre --- abre sem erro
  * `name` existe, e igual ao nome da pasta e usa so a-z, 0-9 e hifen
  * `description` existe e tem no maximo 1024 caracteres

Dica: description longa ou com ": " no meio vai em bloco dobrado, que aceita
qualquer texto:
    description: >-
      Texto da descricao, com dois pontos: sem problema.

Uso:
  python tools/validar_skills.py              confere .agents/skills
  python tools/validar_skills.py <pasta>      confere outra pasta de skills
"""
import io
import os
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

try:
    import yaml
except ImportError:
    print("Este validador precisa do PyYAML: pip install pyyaml")
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RX_CABECALHO = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
RX_NOME = re.compile(r"[a-z0-9-]+")
LIMITE_DESCRICAO = 1024


def problemas_da_skill(pasta_skill):
    nome = os.path.basename(pasta_skill)
    arquivo = os.path.join(pasta_skill, "SKILL.md")
    if not os.path.isfile(arquivo):
        return ["sem SKILL.md"]
    m = RX_CABECALHO.match(io.open(arquivo, encoding="utf-8").read())
    if not m:
        return ["sem cabecalho entre ---"]
    try:
        dados = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as erro:
        return ["YAML invalido: %s" % str(erro).splitlines()[0]]
    problemas = []
    if dados.get("name") != nome:
        problemas.append("name %r diferente da pasta" % dados.get("name"))
    if not RX_NOME.fullmatch(nome):
        problemas.append("nome da pasta fora do padrao a-z, 0-9 e hifen")
    descricao = str(dados.get("description") or "")
    if not descricao:
        problemas.append("sem description")
    elif len(descricao) > LIMITE_DESCRICAO:
        problemas.append("description com %d caracteres (limite %d)" % (len(descricao), LIMITE_DESCRICAO))
    return problemas


def main():
    pasta = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RAIZ, ".agents", "skills")
    if not os.path.isdir(pasta):
        print("Pasta nao encontrada: %s" % pasta)
        return 2
    com_problema = 0
    for nome in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, nome)
        if not os.path.isdir(caminho):
            continue
        problemas = problemas_da_skill(caminho)
        if problemas:
            com_problema += 1
            print("%-24s %s" % (nome, "; ".join(problemas)))
    if com_problema:
        print("\n%d skill(s) com cabecalho que o Codex e o Antigravity podem recusar." % com_problema)
        return 1
    print("Todas as skills com cabecalho valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
