#!/usr/bin/env python3
"""dpfr.py — Deploy Push Fast Release

Faz push automatico do branch main nos dois repositorios:
  1. origin/main  → https://github.com/cunhagd/radiantev2.git (codigo fonte)
  2. radiante-final/main-poc → Amplify domain https://radiante.emaster.info/

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
TARGET_REMOTE_NAME = "radiante-final"
TARGET_REMOTE_URL = "https://github.com/cunhagd/radiante-final.git"
TARGET_BRANCH = "main-poc"
SOURCE_BRANCH = "main"


def _run(cmd: list[str], dry_run: bool = False) -> subprocess.CompletedProcess:
    if dry_run:
        print(f"[DRY-RUN] {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 0, stdout=b"", stderr=b"")
    return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)


def _check_git() -> bool:
    """Verifica se estamos em um repositorio git."""
    r = _run(["git", "rev-parse", "--git-dir"])
    if r.returncode != 0:
        print("ERRO: Diretorio atual nao e um repositorio git.", file=sys.stderr)
        return False
    return True


def _ensure_target_remote(dry_run: bool = False) -> bool:
    """Verifica/adiciona o remote radiante-final."""
    r = _run(["git", "remote", "get-url", TARGET_REMOTE_NAME])
    if r.returncode == 0 and r.stdout.strip() == TARGET_REMOTE_URL:
        return True

    if r.returncode == 0:
        # URL diferente, atualiza
        print(f"Atualizando remote {TARGET_REMOTE_NAME} ...")
        r2 = _run(["git", "remote", "set-url", TARGET_REMOTE_NAME, TARGET_REMOTE_URL], dry_run)
        if r2.returncode != 0:
            print(f"ERRO: Falha ao atualizar remote: {r2.stderr}", file=sys.stderr)
            return False
        return True

    # Remote nao existe, cria
    print(f"Adicionando remote {TARGET_REMOTE_NAME} -> {TARGET_REMOTE_URL} ...")
    r2 = _run(["git", "remote", "add", TARGET_REMOTE_NAME, TARGET_REMOTE_URL], dry_run)
    if r2.returncode != 0:
        print(f"ERRO: Falha ao adicionar remote: {r2.stderr}", file=sys.stderr)
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


def _push(remote: str, branch: str, dry_run: bool = False) -> bool:
    print(f"Push {remote}/{branch} ...")
    r = _run(["git", "push", remote, branch], dry_run)
    if r.returncode != 0:
        print(f"ERRO: Push para {remote}/{branch} falhou: {r.stderr}", file=sys.stderr)
        return False
    # Extrai linhas de resumo (ex: "-> main", "-> main-poc")
    for line in r.stdout.split("\n"):
        line = line.strip()
        if "->" in line or "main" in line.lower():
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

    if not _ensure_target_remote(args.dry_run):
        print("\nDica: Se nao tiver acesso ao remote radiante-final, execute:")
        print("  git remote add radiante-final https://github.com/cunhagd/radiante-final.git")
        print("  git remote set-url radiante-final https://<seu-token>@github.com/cunhagd/radiante-final.git")
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

    # ── Push para os dois remotes ───────────────────────────────────
    ok = True

    # 1. origin/main — repositorio fonte
    print()
    if not _push(ORIGIN_REMOTE, SOURCE_BRANCH, args.dry_run):
        ok = False

    # 2. radiante-final/main-poc — Amplify
    print()
    if not _push(TARGET_REMOTE_NAME, f"{SOURCE_BRANCH}:{TARGET_BRANCH}", args.dry_run):
        print(f"\nAVISO: Push para {TARGET_REMOTE_NAME}/{TARGET_BRANCH} falhou.", file=sys.stderr)
        print("Isso pode acontecer se voce nao tiver permissao de escrita no", file=sys.stderr)
        print("repositorio radiante-final. O deploy no Amplify sera ignorado.", file=sys.stderr)
        # Nao falha — o push principal ja foi feito

    print(f"\n{'=' * 55}")
    if ok:
        print(" Deploy concluido com sucesso!")
        print(f" - {ORIGIN_REMOTE}/{SOURCE_BRANCH}")
        print(f" - {TARGET_REMOTE_NAME}/{TARGET_BRANCH} (Amplify)")
    else:
        print(" Deploy concluido com erros parciais. Verifique as mensagens acima.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
