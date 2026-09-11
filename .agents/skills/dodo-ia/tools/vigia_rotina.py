# -*- coding: utf-8 -*-
"""Vigia a nota da semana e empurra o resto do dia sozinho.

Pedido do fundador em 07/09/2026: "pretendo ir atualizando durante o dia a
rotina, entao o ideal seria ate uma automacao pra atualizar automaticamente".

O QUE ELE FAZ: enquanto roda, observa a nota da semana que cobre HOJE. Quando
ela muda e depois fica parada, roda `recalcular_dia.py --dia <hoje> --empurrar`,
que reancora as tarefas ainda pendentes no fim da ultima tarefa concluida e
reconstroi os cabecalhos de janela.

O QUE ELE NAO FAZ, por decisao dele no mesmo dia: nao reescreve o horario de
tarefa JA marcada. Entre "empurrar o resto" e "realinhar tudo", ele escolheu
empurrar - a hora que ele digitou a mao e dado medido, e automacao que
sobrescreve dado medido apaga o unico registro de quando a coisa aconteceu.

AS DUAS TRAVAS, e por que cada uma existe:

1. SO AGE COM A NOTA PARADA (`--quieto`, padrao 20s). Escrever embaixo de quem
   esta digitando gera conflito de versao no Obsidian. Mudou? o relogio zera.
   So depois de 20 segundos sem toque nenhum e que ele mexe.

2. SO ESCREVE SE MUDAR ALGUMA COISA. O `--empurrar` e idempotente: rodar duas
   vezes no mesmo estado nao move nada e nao grava. E isso que impede o laco de
   a propria escrita do vigia disparar a proxima passada. Por seguranca, o mtime
   tambem e reancorado depois de cada passada.

SEM JANELA NA TELA. A tarefa do Windows o executa com `pythonw.exe`, que nao tem
console, e cada chamada ao recalcular_dia sai com CREATE_NO_WINDOW. Ele existe
so no Gerenciador de Tarefas e no arquivo de log. Exigencia dele em 07/09/2026:
"n quero que fique abrindo um terminal na minha tela a cada 20 seg".

Nao delega decisao nenhuma: e um relogio em cima de um comando que ja existia e
ja era rodado a mao. Se o vigia morrer, o comando continua valendo.

Uso:
  python vigia_rotina.py --uma-vez --dry-run     # confere sem escrever nada
  python vigia_rotina.py --uma-vez               # uma passada agora
  python vigia_rotina.py                         # fica vigiando (Ctrl+C encerra)
  python vigia_rotina.py --quieto 30 --intervalo 10
"""
import argparse
import codecs
import datetime as dt
import io
import os
import subprocess
import sys
import time

import cofre

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
SEMANA = os.path.join(VAULT, "Vida Pessoal", "Semana")
RECALCULAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recalcular_dia.py")

DIAS = (u"Segunda", u"Ter\u00e7a", u"Quarta", u"Quinta", u"Sexta", u"S\u00e1bado", u"Domingo")

# Preenchido por --log. Existe porque a tarefa do Windows roda em pythonw.exe,
# que nao tem console: sem arquivo, tudo que o vigia diz se perde.
ARQUIVO_LOG = None


def log(msg):
    linha = u"[%s] %s" % (dt.datetime.now().strftime("%d/%m %H:%M:%S"), msg)
    print(linha)
    try:
        sys.stdout.flush()
    except Exception:
        pass
    if not ARQUIVO_LOG:
        return
    try:
        with io.open(ARQUIVO_LOG, "a", encoding="utf-8") as fh:
            fh.write(linha + u"\n")
    except Exception:
        # Log que derruba o processo que ele deveria observar e pior que log nenhum.
        pass


def nota_de_hoje(hoje=None):
    """(caminho, nome_do_dia) do arquivo que e DONO do bloco do dia agora.

    O bloco viaja desde 07/09/2026: de manha ele sai da nota da semana e vai pra
    autopsia do dia, e volta no fechamento (ver `cofre.py`). Vigiar a semana num
    caminho fixo faria o vigia dormir o dia inteiro, porque o arquivo que ele
    edita seria o outro.

    O calculo da semana continua vindo da DATA, nunca do 'arquivo mais recente':
    em 07/09/2026 a busca por nome ordenado como texto elegeu a semana PASSADA,
    porque 'Semana 31-08-26' vem depois de 'Semana 07-09-26' no alfabeto.
    """
    hoje = hoje or dt.date.today()
    dia = DIAS[hoje.weekday()]
    try:
        dono = cofre.bloco_do_dia(hoje)[0]
    except Exception as erro:
        log(u"AVISO: nao consegui perguntar ao cofre onde esta o dia (%s). "
            u"Caindo pra nota da semana." % erro)
        dono = None
    if dono:
        return dono, dia
    segunda = hoje - dt.timedelta(days=hoje.weekday())
    return os.path.join(SEMANA, u"Semana %s.md" % segunda.strftime("%d-%m-%y")), dia


def mtime(caminho):
    try:
        return os.path.getmtime(caminho)
    except OSError:
        return None


def passada(caminho, dia, dry_run):
    """Roda o --empurrar do dia. True quando a nota foi alterada."""
    # SEM --semana, de proposito. Passar o nome da semana FORCA o recalcular_dia
    # a procurar o bloco la dentro; sem ele, o proprio script pergunta ao cofre
    # onde o dia esta agora - que e a unica resposta certa depois que o bloco
    # passou a viajar entre a semana e a autopsia (07/09/2026).
    cmd = [sys.executable, RECALCULAR, "--dia", dia, "--empurrar"]
    if dry_run:
        cmd.append("--dry-run")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    # NENHUMA JANELA, nunca. O vigia roda a cada poucos segundos: um console
    # piscando na tela dele a cada passada tornaria a automacao inutilizavel.
    # CREATE_NO_WINDOW garante isso mesmo se o vigia for lancado pelo python.exe
    # de um terminal, e nao pelo pythonw.exe da tarefa agendada.
    criacao = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=env, creationflags=criacao)
    saida = r.stdout.decode("utf-8", "replace").strip()

    if r.returncode != 0:
        log(u"ERRO no recalcular_dia (codigo %d):" % r.returncode)
        for l in saida.splitlines():
            log(u"    %s" % l)
        return False

    mudou = u"Nota atualizada." in saida
    if mudou or dry_run:
        for l in saida.splitlines():
            log(u"    %s" % l)
    return mudou


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intervalo", type=float, default=5.0,
                    help=u"segundos entre uma olhada e outra no arquivo (padrao 5)")
    ap.add_argument("--quieto", type=float, default=20.0,
                    help=u"segundos de nota parada antes de mexer nela (padrao 20)")
    ap.add_argument("--uma-vez", dest="uma_vez", action="store_true",
                    help=u"roda uma passada agora e sai, sem ficar vigiando")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true")
    ap.add_argument("--log", help=u"arquivo pra guardar o que o vigia disser. Obrigatorio "
                                  u"quando ele roda pela tarefa do Windows, que nao tem console")
    a = ap.parse_args()

    if a.log:
        global ARQUIVO_LOG
        ARQUIVO_LOG = a.log

    if a.intervalo <= 0 or a.quieto < 0:
        raise SystemExit(u"--intervalo tem que ser maior que zero e --quieto nao pode ser negativo.")
    if not os.path.isfile(RECALCULAR):
        raise SystemExit(u"Nao achei o recalcular_dia.py em %s" % RECALCULAR)

    if a.uma_vez:
        caminho, dia = nota_de_hoje()
        if mtime(caminho) is None:
            raise SystemExit(u"A nota da semana de hoje ainda nao existe: %s" % caminho)
        log(u"passada unica em %s, dia %s" % (os.path.basename(caminho), dia))
        passada(caminho, dia, a.dry_run)
        return 0

    log(u"vigiando. intervalo %gs, age depois de %gs de nota parada. Ctrl+C encerra."
        % (a.intervalo, a.quieto))

    ultimo = None
    marcado_em = None
    avisou_sumido = False
    caminho_ant = None

    while True:
        try:
            time.sleep(a.intervalo)
            caminho, dia = nota_de_hoje()

            # O dia virou (ou a semana): reancora sem agir, senao a primeira
            # passada do dia novo dispararia so por o arquivo ser outro.
            if caminho != caminho_ant:
                caminho_ant = caminho
                ultimo = mtime(caminho)
                marcado_em = None
                avisou_sumido = False
                log(u"acompanhando %s, dia %s" % (os.path.basename(caminho), dia))

            agora = mtime(caminho)
            if agora is None:
                if not avisou_sumido:
                    log(u"a nota da semana de hoje nao existe ainda: %s" % os.path.basename(caminho))
                    avisou_sumido = True
                continue
            avisou_sumido = False

            if agora != ultimo:
                ultimo = agora
                marcado_em = time.time()
                continue

            if marcado_em is None or (time.time() - marcado_em) < a.quieto:
                continue

            marcado_em = None
            if passada(caminho, dia, a.dry_run):
                log(u"dia %s reancorado." % dia)
            # A nossa propria escrita nao pode contar como mudanca dele.
            ultimo = mtime(caminho)

        except KeyboardInterrupt:
            log(u"encerrado.")
            return 0
        except Exception as erro:
            # Um erro nao pode matar o vigia: ele roda o dia inteiro em segundo
            # plano e ninguem esta olhando pra reiniciar.
            log(u"AVISO: %s: %s" % (type(erro).__name__, erro))
            marcado_em = None


if __name__ == "__main__":
    sys.exit(main())
