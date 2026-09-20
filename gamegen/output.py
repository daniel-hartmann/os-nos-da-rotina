"""Escrita dos arquivos gerados, sem conversão de quebra de linha (o .bat precisa de CRLF, o .sh de LF)."""

from __future__ import annotations

from pathlib import Path

from .model import Game
from .targets import TARGETS


def write_target(game: Game, target_name: str, out: Path) -> Path:
    target = TARGETS[target_name]
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(target.render(game, out.name))
    if target.EXECUTABLE:
        out.chmod(0o755)
    return out
