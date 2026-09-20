"""Exporta o jogo resolvido como dados simples (JSON) para os alvos que trazem um motor próprio.

O alvo bash compila cada nó em uma função; html e bat embutem estes dados e um
interpretador (`runtime/engine.js`, `runtime/engine.ps1`) que segue as mesmas regras.
"""

from __future__ import annotations

import json

from .model import DEFAULT_PROMPT, Game


def to_data(game: Game) -> dict:
    nodes = {}
    for n in game.nodes.values():
        nodes[n.id] = {
            "kind": n.kind,
            "label": n.label,
            "narrative": n.narrative,  # None = pendente, "" = silencioso
            "draft": n.draft,
            "art": n.art,
            "same": n.page == "same",
            "menu": n.menu_label,  # como o nó aparece quando é opção de menu
            "prompt": n.prompt,
            "mode": n.mode,
            "set": n.set,
            "ask": n.ask,
            "succ": [{"to": e.target, "when": e.when, "back": e.back} for e in n.succ],
            "calls": n.calls,
        }
    return {
        "title": game.title,
        "subtitle": game.subtitle,
        "start": game.start,
        "defaultPrompt": DEFAULT_PROMPT,
        "panelPrompt": "Qual caminho?",
        "persistent": game.persistent_vars(),
        "interp": game.interp_vars(),
        "nodes": nodes,
        "panels": {p.id: {"entries": p.entries} for p in game.panels.values()},
    }


def to_json(game: Game, *, indent: int | None = None) -> str:
    """JSON só com ASCII (acentos como \\uXXXX): imune a problemas de codificação do arquivo."""
    return json.dumps(to_data(game), ensure_ascii=True, indent=indent, separators=(",", ":") if indent is None else None)
