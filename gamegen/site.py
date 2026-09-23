"""Site estático (GitHub Pages): cada jogo em html + downloads para bash/Windows + um índice."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .model import Game
from .output import write_target

_env = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
    undefined=StrictUndefined,
    autoescape=True,
)

_JEITO_RE = re.compile(r"^jeito-(\d+)$")


def _slug(stem: str) -> str:
    """No site publicado a URL é só o número (01.html), não o nome do arquivo de entrada.

    `jeito-1` -> `01`, `jeito-2` -> `02`, ... Um nome de entrada que não siga esse padrão
    (por exemplo, ao gerar o site a partir de um JSON com outro nome) mantém o próprio stem.
    """
    m = _JEITO_RE.match(stem)
    return f"{int(m.group(1)):02d}" if m else stem


def build_site(games: list[tuple[Path, Game]], out_dir: Path) -> list[Path]:
    """Gera <NN>.html (jogar), <NN>.sh (baixar) e index.html, um NN por entrada. Links relativos."""
    written: list[Path] = []
    cards = []
    for src, game in games:
        slug = _slug(src.stem)
        html = write_target(game, "html", out_dir / f"{slug}.html")
        sh = write_target(game, "bash", out_dir / f"{slug}.sh")
        written += [html, sh]
        cards.append({"subtitle": game.subtitle or src.stem, "html": html.name, "sh": sh.name})
    title = games[0][1].title
    index = out_dir / "index.html"
    index.write_text(_env.get_template("index.html.j2").render(title=title, cards=cards), encoding="utf-8")
    nojekyll = out_dir / ".nojekyll"  # o Pages não deve processar nada com Jekyll
    nojekyll.write_text("", encoding="utf-8")
    return written + [index, nojekyll]
