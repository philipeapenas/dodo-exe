#!/usr/bin/env python3
"""
organizar_reels.py - Estagio de ORGANIZACAO/PUBLICACAO do motion-expert.

Depois que os videos do dia estao prontos, pega a versao FINAL de cada conta
(mais processada disponivel: _limpo/_caixinha > _limpo > output cru) e COPIA pra
pasta de Reels Limpos por conta, no dia de organizacao (default: hoje):

  <processos>/Ativos/Instagram/Material/Reels/Limpos/<Mes>/<DD MM AA>/Conta N/

Nao destrutivo: COPIA (o original fica no Motion). Pula o que ja existe no destino
(idempotente) - por isso contas ja organizadas manualmente (ex: Conta 1) sao
respeitadas. Mantem o nome do arquivo.

Uso:
  py organizar_reels.py --src-dia "05 07 26"                 # dest = hoje
  py organizar_reels.py --src-dia "05 07 26" --dest-dia "06 07 26"
  py organizar_reels.py --src-dia "05 07 26" --contas "Conta 2,Conta 3,Conta 4"
"""

import argparse
import shutil
import sys
import time
from datetime import date
from pathlib import Path

MESES = {1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril", 5: "Maio",
         6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro",
         11: "Novembro", 12: "Dezembro"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}


def _videos(folder: Path) -> list:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and p.suffix.lower() in VIDEO_EXTS)


def _final_dir(conta_output: Path, allow_cru: bool = False):
    """
    Escolhe a pasta com a versao mais processada da conta:
    _limpo/_caixinha (com caixinha) > _limpo (marca removida). O 'cru' (output, que
    tem a MARCA D'AGUA) so entra com allow_cru=True - senao a gente publicaria video
    com marca por engano. Retorna (pasta, rotulo) ou (None, None).

    Faz 1 retry apos pausa se nada aparecer: o Google Drive as vezes enumera a pasta
    vazia transitoriamente (visto na pratica), e cair pra versao errada e pior que
    esperar/avisar.
    """
    candidatos = [
        (conta_output / "_limpo" / "_caixinha", "caixinha"),
        (conta_output / "_limpo", "limpo"),
    ]
    if allow_cru:
        candidatos.append((conta_output, "cru"))
    for tentativa in range(2):
        for pasta, rotulo in candidatos:
            if _videos(pasta):
                return pasta, rotulo
        if tentativa == 0:
            time.sleep(1.5)   # mitiga enumeracao vazia transitoria do Drive
    return None, None


def _dia_hoje() -> str:
    t = date.today()
    return f"{t.day:02d} {t.month:02d} {t.year % 100:02d}"


def _mes_de(dia: str) -> str:
    partes = dia.split()
    if len(partes) != 3 or not partes[1].isdigit():
        sys.exit(f"[FATAL] dia invalido '{dia}' (use 'DD MM AA').")
    return MESES.get(int(partes[1]), "")


def main():
    ap = argparse.ArgumentParser(description="Organiza os reels prontos em Reels/Limpos por conta.")
    ap.add_argument("--src-dia", required=True, help="Dia de PRODUCAO no Motion (ex: '05 07 26').")
    ap.add_argument("--src-mes", default=None,
                    help="Mes da pasta de producao no Motion (default: deduzido do --src-dia). "
                         "Use '' pra layout antigo, sem nivel de mes.")
    ap.add_argument("--dest-dia", default=None, help="Dia de organizacao no destino (default: hoje).")
    ap.add_argument("--processos-root", required=True,
                    help="Raiz Processos da modelo (ex: .../Modelos/<Modelo>/Processos).")
    ap.add_argument("--contas", default="Conta 1,Conta 2,Conta 3,Conta 4",
                    help="Contas a organizar (separadas por virgula).")
    ap.add_argument("--move", action="store_true", help="Move em vez de copiar (default: copia).")
    ap.add_argument("--overwrite", action="store_true", help="Sobrescreve arquivos ja existentes no destino.")
    ap.add_argument("--allow-cru", action="store_true",
                    help="Permite usar o motion CRU (COM marca d'agua) se nao houver _limpo/_caixinha. "
                         "Off por default pra nao publicar video com marca.")
    args = ap.parse_args()

    processos = Path(args.processos_root)
    if not processos.is_dir():
        sys.exit(f"[FATAL] processos-root nao encontrado: {processos}")
    dest_dia = args.dest_dia or _dia_hoje()
    mes = _mes_de(dest_dia)
    contas = [c.strip() for c in args.contas.split(",") if c.strip()]

    # Producao: Ativos/Instagram/Skills/Motion Control/Motion/Material/<Mes>/<dia>.
    # O nivel de mes e recente: --src-mes "" volta pro layout antigo (sem mes).
    src_mes = _mes_de(args.src_dia) if args.src_mes is None else args.src_mes
    motion_material = (processos / "Ativos" / "Instagram" / "Skills" / "Motion Control"
                       / "Motion" / "Material")
    motion_base = (motion_material / src_mes / args.src_dia) if src_mes \
        else (motion_material / args.src_dia)
    dest_base = processos / "Ativos" / "Instagram" / "Material" / "Reels" / "Limpos" / mes / dest_dia
    print(f"Organizando {len(contas)} conta(s): producao '{args.src_dia}' -> destino '{mes}/{dest_dia}'")
    print(f"  origem:  {motion_base}")
    print(f"  destino: {dest_base}\n")

    total_copiados, total_pulados, avisos = 0, 0, []
    for conta in contas:
        conta_output = motion_base / conta / "output"
        fdir, rotulo = _final_dir(conta_output, args.allow_cru)
        if not fdir:
            avisos.append(f"{conta}: sem _limpo/_caixinha em {conta_output} "
                          f"(nao copiei o cru c/ marca; use --allow-cru se for intencional).")
            print(f"[{conta}] SEM VERSAO LIMPA (pulada)")
            continue
        vids = _videos(fdir)
        dest_conta = dest_base / conta
        dest_conta.mkdir(parents=True, exist_ok=True)
        print(f"[{conta}] versao '{rotulo}' ({len(vids)} video(s)) -> {conta}/")
        for v in vids:
            dst = dest_conta / v.name
            if dst.exists() and not args.overwrite:
                print(f"    - {v.name} JA EXISTE (pulado)")
                total_pulados += 1
                continue
            if args.move:
                shutil.move(str(v), str(dst))
            else:
                shutil.copy2(str(v), str(dst))
            print(f"    + {v.name}")
            total_copiados += 1

    print(f"\nResumo: {total_copiados} {'movidos' if args.move else 'copiados'}, "
          f"{total_pulados} ja existiam.")
    for a in avisos:
        print(f"  AVISO: {a}")


if __name__ == "__main__":
    main()
