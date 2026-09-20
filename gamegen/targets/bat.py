"""Backend bat: um único .bat autocontido para Windows.

O .bat é um lançador fino que extrai de si mesmo um motor em PowerShell (já vem no Windows).
Assim textos, nomes e artes com acentos, aspas, %, !, & e ^ passam sem nenhum escape de cmd.exe.
O arquivo é só ASCII (os dados vão como JSON com \\uXXXX) e usa CRLF.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..export import to_json
from ..model import Game

EXTENSION = ".bat"
EXECUTABLE = False
EXPERIMENTAL = True  # em andamento: fora de `-t all` e do site até ser validado no Windows
NEWLINE = "\r\n"

_PKG = Path(__file__).resolve().parent.parent
_env = Environment(
    loader=FileSystemLoader(_PKG / "templates"),
    keep_trailing_newline=True,
    undefined=StrictUndefined,
    autoescape=False,
    trim_blocks=True,
)


def _ascii(s: str) -> str:
    return s.encode("ascii", "replace").decode("ascii")


def render(game: Game, script_name: str) -> str:
    data_json = to_json(game)
    # O JSON é uma única linha: nenhuma linha pode começar com '@ (fim do here-string do PowerShell).
    assert "\n" not in data_json and data_json.isascii()
    engine = (_PKG / "runtime" / "engine.ps1").read_text(encoding="utf-8")
    assert engine.isascii() and "#PS#" not in engine
    text = _env.get_template("launcher.bat.j2").render(
        source=_ascii(game.source),
        script_name=_ascii(script_name),
        data_json=data_json,
        engine_ps1=engine.replace("\r\n", "\n").rstrip("\n"),
    )
    assert "#PS#" in text and text.count("#PS#") == 1
    return text.replace("\r\n", "\n").replace("\n", NEWLINE)
