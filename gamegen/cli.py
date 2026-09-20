"""Linha de comando: `uv run python -m gamegen ENTRADA.json... [-t bash|bat|html|all] [-o SAIDA]`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import Game, GameError, load, missing_texts
from .output import write_target
from .site import build_site
from .targets import TARGETS


def _report(game: Game, verbose: bool) -> None:
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
    ap.add_argument("inputs", type=Path, nargs="+", metavar="input", help="arquivos narrative-flow/v1 (ex.: jeito-1.json)")
    ap.add_argument(
        "-t", "--target", action="append", choices=[*sorted(TARGETS), "all"],
        help="alvo(s) a gerar; repita para vários, ou use 'all' (padrão: bash; 'all' não inclui alvos experimentais como bat)",
    )
    ap.add_argument("-o", "--output", type=Path, help="arquivo de saída (só com uma entrada e um alvo)")
    ap.add_argument("--out-dir", type=Path, default=Path("dist"), help="pasta de saída (padrão: dist)")
    ap.add_argument("--site", type=Path, metavar="DIR", help="gera o site estático (html + downloads + índice) em DIR")
    ap.add_argument("--start", help="id do nó inicial (padrão: o único nó sem entrada)")
    ap.add_argument("--art-dir", type=Path, help="pasta das artes ASCII (padrão: arte/ ao lado de cada entrada)")
    ap.add_argument("--check", action="store_true", help="só valida e lista textos pendentes; não gera")
    ap.add_argument("-v", "--verbose", action="store_true", help="lista cada texto pendente")
    args = ap.parse_args(argv)

    targets = args.target or ["bash"]
    if "all" in targets:
        targets = sorted(n for n, t in TARGETS.items() if not getattr(t, "EXPERIMENTAL", False))
    if args.output and (len(args.inputs) > 1 or len(targets) > 1 or args.site):
        ap.error("-o só vale com uma entrada e um alvo; use --out-dir")

    games: list[tuple[Path, Game]] = []
    for src in args.inputs:
        try:
            game = load(src, start=args.start, art_dir=args.art_dir)
        except GameError as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1
        print(f"{src}:", file=sys.stderr)
        for w in game.warnings:
            print(f"  aviso: {w}", file=sys.stderr)
        _report(game, args.verbose or args.check)
        games.append((src, game))
    if args.check:
        return 0

    if args.site:
        for path in build_site(games, args.site):
            print(f"gerado {path}", file=sys.stderr)
        return 0
    for src, game in games:
        for name in targets:
            out = args.output or args.out_dir / (src.stem + TARGETS[name].EXTENSION)
            print(f"gerado {write_target(game, name, out)}", file=sys.stderr)
    return 0
