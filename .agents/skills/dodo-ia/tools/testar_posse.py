# -*- coding: utf-8 -*-
"""Conferencia de ida e volta da posse de secoes, em copia do cofre.

POR QUE ISSO EXISTE
`tomar_posse` e `devolver_posse` recortam texto das notas vivas do fundador.
Se o par nao for exatamente reversivel, o estrago aparece dias depois, ja
sincronizado no celular, e sem como saber qual linha sumiu. Entao a regra e:
a nota da semana depois de tomar+devolver tem que ser IDENTICA a de antes.

Roda sobre uma COPIA em pasta temporaria. Nunca toca o cofre de verdade.

Uso:
  python testar_posse.py                 # conferencia completa
  python testar_posse.py --manter        # nao apaga a copia, pra inspecionar
"""
import argparse
import datetime as dt
import io
import os
import shutil
import sys
import tempfile

import cofre


FALHAS = []


def checar(condicao, descricao, detalhe=u""):
    marca = u"ok  " if condicao else u"FALHA"
    print(u"  [%s] %s" % (marca, descricao))
    if not condicao:
        if detalhe:
            print(u"        %s" % detalhe)
        FALHAS.append(descricao)
    return condicao


def montar_copia(base):
    """Espelha a fatia do cofre que o motor toca, com um dia de teste dentro."""
    rotina = os.path.join(base, "Vida Pessoal", "Rotina", "Setembro")
    semana = os.path.join(base, "Vida Pessoal", "Semana")
    insights = os.path.join(base, "Insights")
    for pasta in (rotina, semana, insights):
        os.makedirs(pasta)

    dia = dt.date(2026, 9, 7)  # segunda
    nota_semana = os.path.join(semana, u"Semana 07-09-26.md")
    with io.open(nota_semana, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(SEMANA_FALSA)
    nota_aut = os.path.join(rotina, u"Autopsia das intencoes 07-09-26.md")
    with io.open(nota_aut, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(AUTOPSIA_FALSA)
    with io.open(os.path.join(insights, u"Insights Geral.md"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write(INSIGHTS_FALSO)
    return dia, nota_semana, nota_aut


SEMANA_FALSA = u"""# Semana 07-09-26

### Metas:

#### Semana - por prioridade
- [ ] 1. Loja: MVP do site

#### Segunda
- Meta operacional:
\t- Loja: desenho das telas

- Meta pessoal: <preencher>

> Acordar: 09h

##### 09h-11h (Inercia do Sono) - Foco: Espiritual

- [x] Reprogramacao mental (5m -> 5m): 09h #espiritual
- [ ] Conexao com Deus #espiritual

##### 01h-09h (Restauracao)

- [ ] Descansar (7h30 -> ): 01h21 #fisico

#### Terca
- Meta operacional:
\t- Loja: construcao do MVP

> Acordar: 05h

##### 05h-07h (Inercia do Sono) - Foco: Espiritual

- [ ] Reprogramacao mental (15m -> ): 05h #espiritual

### Pendencias:
- OP Loja:
\t- Site:
\t\t- [ ] Corrigir o formulario_de_contato
\t\t- [ ] Ajustar a automacao dos insights

- Consultoria:
\t- [ ] Definir a economia do projeto

### Desejos:
- Criar painel do conteudo do obsidian

- Livros pra ler:
\t- Flow

### Ideias:
- Loja:
\t- Programa de indicacao

### Perguntas:
- Qual e a idade da razao?

### Resolucao de Problemas:
- Segunda:
- Terca:
- Quarta:
"""

AUTOPSIA_FALSA = u"""# Tarefa: Autopsia das intencoes

### Data: Segunda - 07/09/26

[[Identidade]] . [[Ativos]] . [[Semana 07-09-26]] . [[Insights Geral]]

![[Identidade#Proposito]]

### Metas:
![[Semana 07-09-26#Semana - por prioridade]]

### Rotina e tarefas de hoje:
![[Semana 07-09-26#Segunda]]

### Pendencias:

### Perguntas:

### Desejos:

### Ideias:

### Resolucao de Problemas:

### Insights:
"""

INSIGHTS_FALSO = u"""## Mente humana:
30/07/26:
- Tudo e possivel

## Auto Conhecimento:

### Dev
01/08/26:
- Codigo bom e codigo legivel

## Financeiro:
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manter", action="store_true",
                    help="nao apaga a copia temporaria no fim")
    args = ap.parse_args()

    base = tempfile.mkdtemp(prefix="teste_posse_")
    print(u"copia de teste em: %s" % base)
    dia, nota_semana, nota_aut = montar_copia(base)

    # aponta o motor pra copia, nunca pro cofre de verdade
    cofre.VAULT = base
    cofre.PESSOAL = os.path.join(base, "Vida Pessoal")
    cofre.ROTINA = os.path.join(cofre.PESSOAL, "Rotina")
    cofre.SEMANA = os.path.join(cofre.PESSOAL, "Semana")
    cofre.INSIGHTS_GERAL = os.path.join(base, "Insights", "Insights Geral.md")
    cofre.BACKUP = os.path.join(base, "_backup")

    semana_antes, _ = cofre.ler(nota_semana)

    print(u"\n1. tomar posse")
    codigo, relato = cofre.tomar_posse(dia)
    for linha in relato:
        print(u"     %s" % linha)
    checar(codigo == 0, u"tomar_posse terminou sem erro")

    aut, _ = cofre.ler(nota_aut)
    sem, _ = cofre.ler(nota_semana)

    rotina = cofre.corpo_da_secao(aut, u"Rotina e tarefas de hoje")
    checar(rotina is not None and any(u"Descansar" in l for l in rotina),
           u"a rotina inteira foi pra autopsia (chegou ate 'Descansar')")
    checar(rotina is not None and any(u"##### 09h-11h" in l for l in rotina),
           u"as janelas '#####' vieram junto, nao viraram fronteira")
    # a nota de teste nasce no formato ANTIGO, com o embed na secao da rotina:
    # a primeira tomada de posse tem que enxergar aquilo como vazio e migrar
    checar(rotina is not None and not any(cofre.eh_embed(l) for l in rotina),
           u"o embed antigo foi substituido pelo texto de verdade (migracao)")
    checar(not any(u"Descansar" in l for l in sem),
           u"a rotina saiu da semana")
    checar(any(cofre.eh_ponteiro(l) for l in sem),
           u"a semana ficou com o ponteiro pro dia")
    checar(u"#### Terca" in sem, u"o bloco de terca nao foi tocado")

    pend = cofre.corpo_da_secao(aut, u"Pendencias")
    checar(pend is not None and any(u"formulario_de_contato" in l for l in pend),
           u"Pendencias foi pra autopsia")
    checar(pend is not None and any(l.startswith(u"\t\t- [ ]") for l in pend),
           u"a indentacao de Pendencias foi preservada")

    ideias = cofre.corpo_da_secao(aut, u"Ideias")
    checar(ideias is not None and any(u"indicacao" in l for l in ideias),
           u"Ideias foi pra autopsia")

    checar(cofre.dia_esta_aberto(dia), u"o dia e reconhecido como aberto")

    caminho, corpo = cofre.bloco_do_dia(dia)
    checar(caminho == nota_aut,
           u"bloco_do_dia acha a rotina na AUTOPSIA depois do recorte",
           u"achou em %s" % caminho)

    print(u"\n2. o fundador escreve durante o dia")
    aut, fim = cofre.ler(nota_aut)
    corpo_res = [u"- O agendamento nao rodava porque a virada de meia-noite"]
    aut = cofre.substituir_secao(aut, cofre.SEC_RESOLUCAO, corpo_res)
    rotina_editada = [l.replace(u"- [ ] Conexao com Deus",
                                u"- [x] Conexao com Deus")
                      for l in cofre.corpo_da_secao(aut, u"Rotina e tarefas de hoje")]
    aut = cofre.substituir_secao(aut, u"Rotina e tarefas de hoje", rotina_editada)
    pend_nova = cofre.corpo_da_secao(aut, u"Pendencias") + [u"\t- [ ] Item novo do dia"]
    aut = cofre.substituir_secao(aut, u"Pendencias", pend_nova)
    cofre.gravar(nota_aut, aut, fim)
    print(u"     marcou um checkbox, escreveu 1 resolucao e 1 pendencia nova")

    print(u"\n3. devolver posse")
    codigo, relato = cofre.devolver_posse(dia)
    for linha in relato:
        print(u"     %s" % linha)
    checar(codigo == 0, u"devolver_posse terminou sem conflito")

    sem, _ = cofre.ler(nota_semana)
    aut, _ = cofre.ler(nota_aut)

    checar(any(u"- [x] Conexao com Deus" in l for l in sem),
           u"o checkbox marcado voltou pra semana")
    checar(any(u"Item novo do dia" in l for l in sem),
           u"a pendencia nova voltou pra semana")
    checar(any(u"\t- O agendamento nao rodava" in l for l in sem),
           u"a resolucao voltou reindentada sob '- Segunda:'")
    checar(not any(cofre.eh_ponteiro(l) for l in sem),
           u"nenhum ponteiro sobrou na semana")
    checar(not cofre.dia_esta_aberto(dia), u"o dia e reconhecido como fechado")

    print(u"\n4. ida e volta sem edicao e identidade exata")
    # segundo par, agora sem ninguem escrever no meio: tem que voltar igualzinho
    antes, _ = cofre.ler(nota_semana)
    cofre.tomar_posse(dia)
    cofre.devolver_posse(dia)
    depois, _ = cofre.ler(nota_semana)
    igual = antes == depois
    detalhe = u""
    if not igual:
        import difflib
        detalhe = u" | ".join(list(difflib.unified_diff(antes, depois, lineterm=""))[:8])
    checar(igual, u"a semana volta byte a byte igual depois de tomar+devolver", detalhe)

    checar(cofre.corpo_da_secao(antes, u"Segunda") is not None,
           u"o titulo '#### Segunda' continua existindo na semana")

    print(u"\n5. conflito: a semana ganha conteudo com a secao fora")
    cofre.tomar_posse(dia)
    sem, fim = cofre.ler(nota_semana)
    sem = cofre.substituir_secao(sem, u"Perguntas", [u"- Escrita a mao com a secao fora"])
    cofre.gravar(nota_semana, sem, fim)
    codigo, relato = cofre.devolver_posse(dia)
    conflitou = any(u"CONFLITO" in l for l in relato)
    checar(conflitou and codigo == 2,
           u"o conflito e detectado e a devolucao daquela secao aborta")
    sem, _ = cofre.ler(nota_semana)
    checar(any(u"Escrita a mao" in l for l in sem),
           u"o texto escrito na semana NAO foi sobrescrito")
    aut, _ = cofre.ler(nota_aut)
    checar(any(u"idade da razao" in l for l in
               (cofre.corpo_da_secao(aut, u"Perguntas") or [])),
           u"o texto da autopsia tambem foi preservado - nada se perdeu")

    print(u"")
    if FALHAS:
        print(u"%d FALHA(S): %s" % (len(FALHAS), u"; ".join(FALHAS)))
    else:
        print(u"Todas as conferencias passaram.")
    if not args.manter:
        shutil.rmtree(base, ignore_errors=True)
    else:
        print(u"copia mantida em %s" % base)
    return 1 if FALHAS else 0


if __name__ == "__main__":
    sys.exit(main())
