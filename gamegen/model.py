"""Modelo intermediário do jogo, independente do alvo (bash, windows, html...).

Lê um arquivo `narrative-flow/v1` (o grafo exportado do Miro) e resolve a semântica
de execução que todos os backends compartilham:

* nós `process`/`decision` formam o fluxo; arestas seguem a direção do grafo;
* aresta que aponta para um `panel` é uma *chamada de subfluxo*: o jogo executa o
  subfluxo (entrando por um dos nós de entrada do painel), volta e continua;
* arestas que *saem* de um painel são só anotações visuais e são ignoradas;
* aresta que volta para um nó já percorrido no fluxo principal é um *laço de volta*
  (no board: "Fim de jogo" / final -> "Na manhã do dia seguinte").

Campos opcionais que os redatores podem adicionar aos nós do JSON:

    narrative  texto exibido ao entrar no nó (string, ou lista de parágrafos).
               Ausente = texto pendente (o jogo avisa); "" = nó silencioso de propósito.
               Aceita {var} para interpolar uma variável (ex.: {nome}).
    art        nome de uma arte ASCII em `arte/<nome>.txt` (ao lado do JSON), exibida no topo
               da página do nó, antes do texto. Texto puro: sem escapes, sem JSON.
    page       "new" (padrão): o texto abre uma página nova (espera Enter e limpa a tela);
               "same": continua na página atual, logo abaixo do texto anterior
    draft      rascunho/nota de design; aparece junto do aviso de texto pendente
    choice     texto exibido quando o nó é uma opção de menu (padrão: `text`)
    prompt     pergunta do menu quando o nó ramifica (padrão: "O que você faz?")
    mode       como escolher entre vários sucessores: "choice" (jogador escolhe,
               padrão), "random" (sorteio entre as arestas cujo `when` vale) ou
               "conditional" (primeira aresta cujo `when` vale; a aresta sem
               `when` é o "senão"). Num nó que chama painel, "random" sorteia a
               entrada do painel (entre as ainda não visitadas) e o resto pergunta.
    set        {"var": "valor"} aplicado ao entrar no nó
    ask        {"var": "nome", "prompt": "Digite seu nome:", "default": "X"}: lê uma
               resposta do jogador. A variável sobrevive ao recomeço do dia.

e às arestas:

    when       {"var": "valor"} condição (igualdade) para a aresta valer;
               valor "" ou null = variável ainda não definida

No topo do arquivo: `game_title` (senão `title`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA = "narrative-flow/v1"
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ART_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
MAX_ART_COLUMNS = 78
VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
MODES = ("choice", "random", "conditional")
DEFAULT_PROMPT = "O que você faz?"


class GameError(Exception):
    """Entrada inválida; a mensagem é pensada para ser mostrada ao usuário."""


@dataclass
class Edge:
    target: str
    when: dict[str, str] | None = None
    back: bool = False


@dataclass
class Node:
    id: str
    kind: str  # "process" | "decision"
    label: str  # texto do bloco no Miro (rascunho de design, não é texto de jogo)
    x: int
    y: int
    inside: str | None = None  # id do painel que contém o nó
    narrative: str | None = None  # None = pendente, "" = silencioso
    draft: str = ""
    art: str = ""  # conteúdo da arte (já lido do arquivo)
    page: str = "new"
    choice: str = ""
    prompt: str = ""
    mode: str = "choice"
    set: dict[str, str] = field(default_factory=dict)
    ask: dict[str, str] | None = None
    succ: list[Edge] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)  # ids de painéis chamados

    @property
    def menu_label(self) -> str:
        return self.choice or self.label


@dataclass
class Panel:
    id: str
    label: str
    x: int
    entries: list[str] = field(default_factory=list)


@dataclass
class Game:
    title: str
    source: str
    start: str
    nodes: dict[str, Node]
    panels: dict[str, Panel]
    warnings: list[str] = field(default_factory=list)
    subtitle: str = ""  # ex.: "Jeito 1: 5 ou 6 pontos de interação"

    def variables(self) -> list[str]:
        """Todas as variáveis de estado (`set`, `when`, `ask`), em ordem estável."""
        names: set[str] = set()
        for n in self.nodes.values():
            names.update(n.set)
            if n.ask:
                names.add(n.ask["var"])
            for e in n.succ:
                names.update(e.when or {})
        return sorted(names)

    def persistent_vars(self) -> list[str]:
        """Variáveis que não são zeradas quando o dia recomeça (respostas do jogador)."""
        return sorted({n.ask["var"] for n in self.nodes.values() if n.ask})

    def interp_vars(self) -> list[str]:
        """Variáveis referenciadas como {var} em algum texto."""
        used: set[str] = set()
        for n in self.nodes.values():
            for t in (n.narrative, n.choice, n.prompt):
                used.update(PLACEHOLDER_RE.findall(t or ""))
        return sorted(used)


def _text(value: object, where: str) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip("\n")
    if isinstance(value, list) and all(isinstance(p, str) for p in value):
        return "\n\n".join(p.strip("\n") for p in value)
    raise GameError(f"{where}: esperava texto (string ou lista de strings)")


def _vars(value: object, where: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise GameError(f"{where}: esperava um objeto {{variável: valor}}")
    out = {}
    for k, v in value.items():
        if not VAR_RE.match(k):
            raise GameError(f"{where}: nome de variável inválido {k!r}")
        if v is None:
            v = ""
        elif isinstance(v, bool):
            v = "1" if v else "0"
        elif not isinstance(v, (str, int, float)):
            raise GameError(f"{where}: valor inválido para {k!r}")
        out[k] = str(v)
    return out


def _ask(value: object, where: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or not VAR_RE.match(str(value.get("var", ""))):
        raise GameError(f'{where}: "ask" precisa de {{"var": nome_valido, "prompt": ..., "default": ...}}')
    return {
        "var": value["var"],
        "prompt": _text(value.get("prompt", ""), where) or "?",
        "default": _text(value.get("default", ""), where),
    }


def _read_art(name: str, art_dir: Path, where: str, warnings: list[str]) -> str:
    if not isinstance(name, str) or not ART_NAME_RE.match(name):
        raise GameError(f"{where}: nome de arte inválido {name!r} (use letras, números, - e _)")
    file = art_dir / f"{name}.txt"
    try:
        raw = file.read_text(encoding="utf-8")
    except OSError as exc:
        raise GameError(f"{where}: arte {name!r} não encontrada em {file}") from exc
    lines = [ln.expandtabs(4).rstrip() for ln in raw.splitlines()]
    art = "\n".join(lines).strip("\n")  # só tira linhas vazias; a indentação é do desenho
    if not art:
        raise GameError(f"{where}: a arte {file} está vazia")
    width = max(len(ln) for ln in art.split("\n"))
    if width > MAX_ART_COLUMNS:
        warnings.append(f"arte {name!r} tem {width} colunas (cabem {MAX_ART_COLUMNS} em terminal de 80)")
    return art


def load(path: str | Path, start: str | None = None, art_dir: str | Path | None = None) -> Game:
    path = Path(path)
    art_dir = Path(art_dir) if art_dir else path.parent / "arte"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GameError(f"não consegui ler {path}: {exc}") from exc
    if raw.get("schema") != SCHEMA:
        raise GameError(f"{path}: schema {raw.get('schema')!r}, esperado {SCHEMA!r}")

    nodes: dict[str, Node] = {}
    panels: dict[str, Panel] = {}
    warnings: list[str] = []
    for rn in raw.get("nodes", []):
        nid = rn.get("id", "")
        if not ID_RE.match(nid):
            raise GameError(f"id de nó inválido: {nid!r}")
        if nid in nodes or nid in panels:
            raise GameError(f"id de nó duplicado: {nid}")
        kind = rn.get("type")
        if kind == "panel":
            panels[nid] = Panel(nid, rn.get("text", ""), rn.get("x", 0))
            continue
        if kind not in ("process", "decision"):
            raise GameError(f"nó {nid}: tipo desconhecido {kind!r}")
        where = f"nó {nid}"
        node = Node(
            id=nid,
            kind=kind,
            label=rn.get("text", ""),
            x=rn.get("x", 0),
            y=rn.get("y", 0),
            inside=rn.get("inside"),
            narrative=None if rn.get("narrative") is None else _text(rn["narrative"], where),
            draft=_text(rn.get("draft"), where),
            choice=_text(rn.get("choice"), where),
            prompt=_text(rn.get("prompt"), where),
            set=_vars(rn.get("set"), where),
            ask=_ask(rn.get("ask"), where),
        )
        if rn.get("art") is not None:
            node.art = _read_art(rn["art"], art_dir, where, warnings)
        page = rn.get("page", "new")
        if page not in ("new", "same"):
            raise GameError(f'{where}: page {page!r} inválido (use "new" ou "same")')
        node.page = page
        mode = rn.get("mode")
        if mode is not None and mode not in MODES:
            raise GameError(f"{where}: mode {mode!r} inválido (use {', '.join(MODES)})")
        node.mode = mode or ""
        nodes[nid] = node
    for n in nodes.values():
        if n.inside is not None and n.inside not in panels:
            raise GameError(f"nó {n.id}: 'inside' aponta para {n.inside!r}, que não é um painel")

    ignored_from_panel = 0
    for re_ in raw.get("edges", []):
        a, b = re_.get("from"), re_.get("to")
        for end in (a, b):
            if end not in nodes and end not in panels:
                raise GameError(f"aresta {a} -> {b}: nó {end!r} não existe")
        if a in panels:
            ignored_from_panel += 1
            continue
        if b in panels:
            if nodes[a].inside:
                warnings.append(f"chamada de painel dentro de painel ignorada ({a} -> {b})")
            elif b not in nodes[a].calls:
                nodes[a].calls.append(b)
            continue
        if nodes[a].inside != nodes[b].inside:
            raise GameError(f"aresta {a} -> {b} atravessa o limite de um painel")
        nodes[a].succ.append(Edge(b, _vars(re_.get("when"), f"aresta {a} -> {b}") or None))
    if ignored_from_panel:
        warnings.append(f"{ignored_from_panel} aresta(s) saindo de painel tratada(s) como anotação")

    # Ordem estável e legível dos sucessores/chamadas: esquerda -> direita no board.
    for n in nodes.values():
        n.succ.sort(key=lambda e: (nodes[e.target].x, nodes[e.target].y))
        n.calls.sort(key=lambda p: panels[p].x)
        if not n.mode:
            n.mode = "conditional" if any(e.when for e in n.succ) else "choice"
        if n.mode == "choice" and any(e.when for e in n.succ):
            raise GameError(f"nó {n.id}: 'when' não vale em modo choice (use random ou conditional)")
        uncond = [e for e in n.succ if not e.when]
        if n.mode == "conditional" and len(uncond) > 1:
            raise GameError(f"nó {n.id}: mais de uma aresta sem 'when' em modo conditional")

    has_incoming = {e.target for n in nodes.values() for e in n.succ}
    for p in panels.values():
        p.entries = sorted(
            (n.id for n in nodes.values() if n.inside == p.id and n.id not in has_incoming),
            key=lambda i: nodes[i].x,
        )
        if not p.entries:
            raise GameError(f"painel {p.id} ({p.label!r}) não tem nó de entrada")

    if start is None:
        roots = [n.id for n in nodes.values() if not n.inside and n.id not in has_incoming]
        if len(roots) != 1:
            raise GameError(
                f"esperava exatamente 1 nó inicial, achei {len(roots)}: {roots}. Use --start."
            )
        start = roots[0]
    elif start not in nodes or nodes[start].inside:
        raise GameError(f"--start {start!r} não é um nó do fluxo principal")

    _mark_back_edges(nodes, panels, start)

    reachable = _reachable(nodes, panels, start)
    for nid in nodes:
        if nid not in reachable:
            warnings.append(f"nó {nid} ({nodes[nid].label!r}) é inalcançável a partir de {start}")

    defined = set()
    game_probe = Game("", "", start, nodes, panels)
    defined.update(game_probe.variables())
    unknown = sorted(set(game_probe.interp_vars()) - defined)
    if unknown:
        raise GameError(f"textos usam {{{', '.join(unknown)}}}, mas nenhum nó define essas variáveis")

    title = raw.get("game_title") or raw.get("title") or path.stem
    return Game(
        title=title,
        source=path.name,
        start=start,
        nodes=nodes,
        panels=panels,
        warnings=warnings,
        subtitle=raw.get("title", ""),
    )


def _mark_back_edges(nodes: dict[str, Node], panels: dict[str, Panel], start: str) -> None:
    """Marca arestas que voltam a um ancestral (DFS). Só são aceitas no fluxo principal."""

    def dfs(root: str) -> None:
        state: dict[str, int] = {}  # 1 = na pilha, 2 = concluído
        stack = [(root, iter(nodes[root].succ))]
        state[root] = 1
        while stack:
            nid, it = stack[-1]
            for edge in it:
                s = state.get(edge.target)
                if s == 1:
                    if nodes[nid].inside:
                        raise GameError(f"ciclo dentro de painel ({nid} -> {edge.target}) não é suportado")
                    edge.back = True
                elif s is None:
                    state[edge.target] = 1
                    stack.append((edge.target, iter(nodes[edge.target].succ)))
                    break
            else:
                state[nid] = 2
                stack.pop()

    dfs(start)
    for p in panels.values():
        for entry in p.entries:
            dfs(entry)


def _reachable(nodes: dict[str, Node], panels: dict[str, Panel], start: str) -> set[str]:
    seen: set[str] = set()
    todo = [start]
    while todo:
        nid = todo.pop()
        if nid in seen:
            continue
        seen.add(nid)
        n = nodes[nid]
        todo.extend(e.target for e in n.succ)
        for p in n.calls:
            todo.extend(panels[p].entries)
    return seen


def menu_targets(game: Game) -> set[str]:
    """Nós que aparecem como opção num menu (precisam de `choice` escrito)."""
    out: set[str] = set()
    for n in game.nodes.values():
        if n.mode == "choice" and len(n.succ) > 1:
            out.update(e.target for e in n.succ)
        for p in n.calls:
            if len(game.panels[p].entries) > 1 and n.mode != "random":
                out.update(game.panels[p].entries)
    return out


def missing_texts(game: Game) -> tuple[list[Node], list[Node]]:
    """(process sem `narrative`, opções de menu sem `choice`), em ordem de leitura."""
    order = sorted(game.nodes.values(), key=lambda n: (n.inside or "", n.y, n.x))
    no_narrative = [n for n in order if n.kind == "process" and n.narrative is None]
    targets = menu_targets(game)
    no_choice = [n for n in order if n.id in targets and not n.choice]
    return no_narrative, no_choice
