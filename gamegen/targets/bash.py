"""Backend bash: gera um único script executável e autocontido (bash 3.2+)."""

from __future__ import annotations

import shlex
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..model import DEFAULT_PROMPT, PLACEHOLDER_RE, Game

EXTENSION = ".sh"
EXECUTABLE = True

_env = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent.parent / "templates"),
    comment_start_string="<#",  # o padrão `{#` colide com `${#array[@]}` do bash
    comment_end_string="#>",
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
    undefined=StrictUndefined,
    autoescape=False,  # saída é bash, não HTML; o escape é feito por `sh`
)
_env.filters["sh"] = lambda s: shlex.quote(str(s))


def _txt(s: str) -> str:
    """Texto de jogo: cita para o bash e, se tiver {var}, passa por `interp` em tempo de execução."""
    quoted = shlex.quote(str(s))
    return f'"$(interp {quoted})"' if PLACEHOLDER_RE.search(str(s)) else quoted


_env.filters["txt"] = _txt


def render(game: Game, script_name: str) -> str:
    persistent = set(game.persistent_vars())
    reset_vars = [f"V_{v}" for v in game.variables() if v not in persistent] + [
        f"VIS_{e}" for p in game.panels.values() for e in p.entries
    ]
    return _env.get_template("bash.sh.j2").render(
        title=game.title,
        source=game.source,
        script_name=script_name,
        start=game.start,
        nodes=game.nodes,
        panels=game.panels,
        default_prompt=DEFAULT_PROMPT,
        reset_vars=reset_vars,
        interp_vars=game.interp_vars(),
    )
