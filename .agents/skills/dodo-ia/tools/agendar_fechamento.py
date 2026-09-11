# -*- coding: utf-8 -*-
"""Agenda o fechamento do dia pra 30 minutos depois do fim da cascata.

DECISAO DELE (07/09/2026): "o fechar_dia deve ser feito adaptado no horario
final do dia + 30 min pra garantir que eu finalizei mesmo. 01h21 e o final do
dia de hoje, as 01h51 ele deve rodar, e isso adaptado por dia."

O HORARIO NAO E FIXO, ELE NASCE DA CASCATA
O fim do dia e o ultimo horario do bloco do dia (hoje, o inicio de "Descansar").
Quando ele declara a hora real que acordou, o `recalcular_dia.py` reescreve a
cascata inteira e o fim do dia se move - entao este script e chamado no fim do
`criar_autopsia.py` E no fim do `recalcular_dia.py`, reescrevendo a tarefa.

A ARMADILHA DA VIRADA DE MEIA-NOITE
01h21 pertence ao dia SEGUINTE, nao a 01h21 da manha do proprio dia. Se isso
for lido errado a tarefa dispara antes do dia comecar e fecha um dia vazio.
Regra usada: se o ultimo horario e MENOR que a hora de acordar, ele esta do
outro lado da meia-noite e a data avanca um dia.

POR QUE XML E NAO `schtasks /SC ONCE /ST`
A linha de comando do schtasks interpreta data no formato do locale do Windows
(pt-BR usa DD/MM/AAAA). Passar data por ali e depender do idioma da maquina.
O XML usa ISO 8601 sempre, e e onde da pra ligar StartWhenAvailable - que e o
que faz a tarefa rodar quando ele ligar o PC, se estava desligado na hora.

Uso:
  python agendar_fechamento.py --mostrar        # so calcula, nao agenda
  python agendar_fechamento.py                  # agenda pra hoje
  python agendar_fechamento.py --dia 2026-09-07
"""
import argparse
import io
import os
import re
import subprocess
import sys
import tempfile
import datetime as dt

import cofre

TAREFA = u"Dodo.IA - Fechar o dia"
MINUTOS_DE_FOLGA = 30

# Hora de relogio vem SEMPRE depois do fecha-parenteses: `(4h -> ): 11h20`.
# Sem ancorar no `):` o regex pegaria `4h` da duracao e o fim do dia sairia
# errado por horas.
RX_HORA_RELOGIO = re.compile(r"\)\s*:\s*(\d{1,2})\s*h\s*(\d{2})?")
RX_ACORDAR = re.compile(r"^>\s*Acordar\s*:\s*(\d{1,2})\s*h\s*(\d{2})?", re.IGNORECASE)

XML = u"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Fecha o dia: devolve as secoes da autopsia para a nota da semana e arquiva os insights. Horario recalculado a cada mudanca da cascata por agendar_fechamento.py.</Description>
    <URI>\\%(tarefa)s</URI>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>%(quando)s</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>%(python)s</Command>
      <Arguments>"%(script)s" --dia %(iso)s</Arguments>
      <WorkingDirectory>%(pasta)s</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def horarios_do_bloco(corpo):
    """([(h, m) na ordem do bloco], (h, m) do 'Acordar' ou None)."""
    marcados, acordar = [], None
    for linha in corpo:
        m = RX_ACORDAR.match(linha.strip())
        if m:
            acordar = (int(m.group(1)), int(m.group(2) or 0))
            continue
        achado = RX_HORA_RELOGIO.search(linha)
        if achado:
            marcados.append((int(achado.group(1)), int(achado.group(2) or 0)))
    return marcados, acordar


def quando_fechar(dia):
    """(datetime do disparo, texto explicando) ou (None, motivo)."""
    caminho, corpo = cofre.bloco_do_dia(dia)
    if not corpo:
        return None, u"nao achei o bloco do dia %s (nem na autopsia, nem na semana)" \
            % dia.strftime("%d/%m/%y")

    marcados, acordar = horarios_do_bloco(corpo)
    if not marcados:
        return None, u"o bloco do dia nao tem nenhum horario de relogio"

    fim_h, fim_m = marcados[-1]
    ref_h, ref_m = acordar or marcados[0]
    data = dia
    virou = (fim_h, fim_m) < (ref_h, ref_m)
    if virou:
        data = dia + dt.timedelta(days=1)

    disparo = dt.datetime(data.year, data.month, data.day, fim_h, fim_m) \
        + dt.timedelta(minutes=MINUTOS_DE_FOLGA)
    explica = u"fim do dia %02dh%02d%s, mais %d min" % (
        fim_h, fim_m,
        u" (ja do dia seguinte)" if virou else u"",
        MINUTOS_DE_FOLGA)
    return disparo, u"%s | bloco lido de %s" % (explica, os.path.basename(caminho))


def python_do_sistema():
    """python.exe, nunca pythonw: a tarefa espelha a 'Criar autopsia do dia'."""
    caminho = sys.executable
    if caminho.lower().endswith("pythonw.exe"):
        candidato = caminho[:-len("pythonw.exe")] + "python.exe"
        if os.path.isfile(candidato):
            return candidato
    return caminho


def agendar(disparo, dia):
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fechar_dia.py")
    conteudo = XML % {
        "tarefa": TAREFA,
        "quando": disparo.strftime("%Y-%m-%dT%H:%M:%S"),
        "python": python_do_sistema(),
        "script": script,
        "pasta": os.path.dirname(script),
        "iso": dia.strftime("%Y-%m-%d"),
    }
    # o schtasks so aceita o XML em UTF-16; em UTF-8 ele recusa sem explicar
    alvo = os.path.join(tempfile.gettempdir(), "dodoia_fechar_dia.xml")
    with io.open(alvo, "w", encoding="utf-16") as fh:
        fh.write(conteudo)
    proc = subprocess.Popen(
        ["schtasks", "/Create", "/TN", TAREFA, "/XML", alvo, "/F"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    saida = proc.communicate()[0]
    try:
        os.remove(alvo)
    except OSError:
        pass
    return proc.returncode, saida.decode("cp1252", "replace").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    ap.add_argument("--mostrar", action="store_true", help="so calcula, nao agenda")
    args = ap.parse_args()

    dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date() if args.dia else dt.date.today()
    disparo, nota = quando_fechar(dia)

    if disparo is None:
        print(u"nao agendei: %s" % nota)
        return 1

    print(u"dia:      %s (%s)" % (dia.strftime("%d/%m/%y"), cofre.nome_do_dia(dia)))
    print(u"leitura:  %s" % nota)
    print(u"disparo:  %s" % disparo.strftime("%d/%m/%Y as %H:%M"))

    if disparo <= dt.datetime.now():
        print(u"")
        print(u"AVISO: esse horario ja passou. A tarefa e criada mesmo assim, mas o")
        print(u"       agendador nao dispara gatilho vencido. Se o dia ja acabou,")
        print(u"       rode:  python fechar_dia.py --dia %s" % dia.strftime("%Y-%m-%d"))

    if args.mostrar:
        print(u"")
        print(u"--mostrar: a tarefa nao foi criada.")
        return 0

    codigo, saida = agendar(disparo, dia)
    print(u"")
    if codigo == 0:
        print(u"tarefa '%s' agendada." % TAREFA)
    else:
        print(u"FALHOU ao agendar (codigo %d):" % codigo)
    if saida:
        print(u"  %s" % saida)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
