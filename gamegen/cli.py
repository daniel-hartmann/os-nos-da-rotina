"""Linha de comando: `uv run python -m gamegen ENTRADA.json [-t bash] [-o SAIDA]`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import GameError, load, missing_texts
from .targets import TARGETS


def _report(game, verbose: bool) -> None:
    no_narr, no_choice = missing_texts(game)
    drafts = sum(1 for n in no_narr if n.draft)
    print(
        f"{len(game.nodes)} nós, {len(game.panels)} painéis; "
        f"{len(no_narr)} sem texto (narrative), {drafts} deles com rascunho; "
        f"{len(no_choice)} opções de menu sem texto (choice)",
        file=sys.stderr,
    )
    if verbose:
        for n in no_narr:
            print(f"  narrative pendente  {n.id:<5} {n.label!r}", file=sys.stderr)
        for n in no_choice:
            print(f"  choice pendente     {n.id:<5} {n.label!r}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gamegen", description=__doc__)
    ap.add_argument("input", type=Path, help="arquivo narrative-flow/v1 (ex.: jeito-1.json)")
    ap.add_argument("-t", "--target", choices=sorted(TARGETS), default="bash")
    ap.add_argument("-o", "--output", type=Path, help="arquivo de saída (padrão: dist/<entrada><ext>)")
    ap.add_argument("--start", help="id do nó inicial (padrão: o único nó sem entrada)")
    ap.add_argument("--art-dir", type=Path, help="pasta das artes ASCII (padrão: arte/ ao lado da entrada)")
    ap.add_argument("--check", action="store_true", help="só valida e lista textos pendentes; não gera")
    ap.add_argument("-v", "--verbose", action="store_true", help="lista cada texto pendente")
    args = ap.parse_args(argv)

    try:
        game = load(args.input, start=args.start, art_dir=args.art_dir)
    except GameError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    for w in game.warnings:
        print(f"aviso: {w}", file=sys.stderr)
    _report(game, args.verbose or args.check)
    if args.check:
        return 0

    target = TARGETS[args.target]
    out = args.output or Path("dist") / (args.input.stem + target.EXTENSION)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(target.render(game, out.name), encoding="utf-8")
    if target.EXECUTABLE:
        out.chmod(0o755)
    print(f"gerado {out}", file=sys.stderr)
    return 0
