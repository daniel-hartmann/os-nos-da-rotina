"""Site estático (GitHub Pages): cada jogo em html + downloads para bash/Windows + um índice."""

from __future__ import annotations

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


def build_site(games: list[tuple[Path, Game]], out_dir: Path) -> list[Path]:
    """Gera <jogo>.html (jogar), <jogo>.sh e <jogo>.bat (baixar) e index.html. Links relativos."""
    written: list[Path] = []
    cards = []
    for src, game in games:
        stem = src.stem
        html = write_target(game, "html", out_dir / f"{stem}.html")
        sh = write_target(game, "bash", out_dir / f"{stem}.sh")
        bat = write_target(game, "bat", out_dir / f"{stem}.bat")
        written += [html, sh, bat]
        cards.append({"subtitle": game.subtitle or stem, "html": html.name, "sh": sh.name, "bat": bat.name})
    title = games[0][1].title
    index = out_dir / "index.html"
    index.write_text(_env.get_template("index.html.j2").render(title=title, cards=cards), encoding="utf-8")
    nojekyll = out_dir / ".nojekyll"  # o Pages não deve processar nada com Jekyll
    nojekyll.write_text("", encoding="utf-8")
    return written + [index, nojekyll]
