#!/usr/bin/env python3
"""dpfr.py — Deploy Push Fast Release

Faz push automatico do branch main nos branches que disparam o CI/CD:
  1. origin/main       → repositorio fonte (codigo)
  2. origin/main-poc   → mesmo repo, dispara auto-build do Amplify
                         (dominio: https://radiante.emaster.info/)

Uso:
  python dpfr.py                  # Commita, push em ambos e dispara CI/CD
  python dpfr.py --no-commit      # Apenas push (sem criar novo commit)
  python dpfr.py -m "mensagem"    # Commit com mensagem personalizada
  python dpfr.py --dry-run        # Mostra o que seria feito sem executar
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent
ORIGIN_REMOTE = "origin"
MAIN_BRANCH = "main"
POC_BRANCH = "main-poc"


def _run(cmd: list[str], dry_run: bool = False) -> subprocess.CompletedProcess:
    if dry_run:
        print(f"[DRY-RUN] {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 0, stdout=b"", stderr=b"")
    return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)


def _check_git() -> bool:
    r = _run(["git", "rev-parse", "--git-dir"])
    if r.returncode != 0:
        print("ERRO: Diretorio atual nao e um repositorio git.", file=sys.stderr)
        return False
    return True


def _has_uncommitted_changes() -> bool:
    r = _run(["git", "status", "--porcelain"])
    return bool(r.stdout.strip())


def _commit_all(message: str, dry_run: bool = False) -> bool:
    print(f"Commiting all changes: \"{message}\" ...")
    r1 = _run(["git", "add", "-A"], dry_run)
    if r1.returncode != 0:
        print(f"ERRO: git add falhou: {r1.stderr}", file=sys.stderr)
        return False

    r2 = _run(["git", "commit", "-m", message], dry_run)
    if r2.returncode != 0:
        if "nothing to commit" in r2.stderr or "nothing to commit" in r2.stdout:
            print("  Nada novo para commitar.")
            return True
        print(f"ERRO: git commit falhou: {r2.stderr}", file=sys.stderr)
        return False

    print(f"  Commit criado: {r2.stdout.strip()}")
    return True


def _push(remote: str, refspec: str, dry_run: bool = False, force: bool = False) -> bool:
    cmd = ["git", "push"]
    if force:
        cmd.append("--force")
    cmd.extend([remote, refspec])
    print(f"Push {remote}/{refspec} ...")
    r = _run(cmd, dry_run)
    if r.returncode != 0:
        print(f"ERRO: Push falhou: {r.stderr}", file=sys.stderr)
        return False
    output = r.stdout
    if isinstance(output, bytes):
        output = output.decode("utf-8")
    for line in output.split("\n"):
        line = line.strip()
        if line:
            print(f"  {line}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Push Fast Release")
    parser.add_argument("--no-commit", action="store_true",
                        help="Pular etapa de commit (apenas push)")
    parser.add_argument("-m", "--message", type=str, default="",
                        help="Mensagem de commit personalizada")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simular sem executar")
    args = parser.parse_args()

    if not _check_git():
        sys.exit(1)

    print(f"\n{'=' * 55}")
    print(" dpfr.py — Deploy Push Fast Release")
    print(f"{'=' * 55}\n")

    has_changes = _has_uncommitted_changes()

    # ── Commit ──────────────────────────────────────────────────────
    if not args.no_commit and has_changes:
        message = args.message if args.message else "deploy: atualizacao automatica dpfr"
        if not _commit_all(message, args.dry_run):
            sys.exit(1)
    elif not has_changes:
        print("Nenhuma alteracao para commitar.")

    if args.no_commit and has_changes:
        print("Alteracoes nao commitadas serao incluidas no push.")
        r = _run(["git", "add", "-A"], args.dry_run)
        if r.returncode != 0:
            print(f"ERRO: git add falhou: {r.stderr}", file=sys.stderr)
            sys.exit(1)

    # ── Push ────────────────────────────────────────────────────────
    ok = True

    # 1. origin/main — repositorio fonte (sem force)
    print()
    if not _push(ORIGIN_REMOTE, MAIN_BRANCH, args.dry_run, force=False):
        ok = False

    # 2. origin/main:main-poc — mesmo repo, branch que o Amplify escuta
    #    Usa force para espelhar exatamente a main (o main-poc e apenas
    #    um espelho de deploy, nao importa historico divergente)
    print()
    if not _push(ORIGIN_REMOTE, f"{MAIN_BRANCH}:{POC_BRANCH}", args.dry_run, force=True):
        print(f"\nAVISO: Push para {ORIGIN_REMOTE}/{POC_BRANCH} falhou.", file=sys.stderr)
        ok = False

    print(f"\n{'=' * 55}")
    if ok:
        print(" Deploy concluido com sucesso!")
        print(f" - {ORIGIN_REMOTE}/{MAIN_BRANCH}")
        print(f" - {ORIGIN_REMOTE}/{POC_BRANCH} (Amplify — https://radiante.emaster.info/)")
    else:
        print(" Deploy concluido com erros parciais. Verifique as mensagens acima.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
