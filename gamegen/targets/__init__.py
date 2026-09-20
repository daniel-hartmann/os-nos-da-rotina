"""Backends. Cada alvo é um módulo com `EXTENSION`, `EXECUTABLE` e `render(game, script_name) -> str`.

Para adicionar um alvo (windows, html...), crie o módulo e registre-o aqui.
"""

from . import bash

TARGETS = {
    "bash": bash,
}
