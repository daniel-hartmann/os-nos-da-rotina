"""Backend html: um único .html autocontido (dados + motor JS + estilo). Artes ASCII vão em <pre>."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..export import to_json
from ..model import Game

EXTENSION = ".html"
EXECUTABLE = False

_PKG = Path(__file__).resolve().parent.parent
_env = Environment(
    loader=FileSystemLoader(_PKG / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
    undefined=StrictUndefined,
    autoescape=True,  # título/subtítulo entram no HTML; dados e motor são injetados já seguros (|safe)
)


def _json_for_script(game: Game) -> str:
    # Já é só ASCII; só falta impedir que o texto feche a tag <script> ou abra um comentário HTML.
    return to_json(game).replace("</", "<\\/").replace("<!--", "<\\!--")


def render(game: Game, script_name: str) -> str:
    engine = (_PKG / "runtime" / "engine.js").read_text(encoding="utf-8")
    assert "</script" not in engine.lower()
    return _env.get_template("game.html.j2").render(
        title=game.title,
        subtitle=game.subtitle,
        data_json=_json_for_script(game),
        engine_js=engine,
    )
