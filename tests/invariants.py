"""Invariantes de lógica dos jogos reais, válidas para qualquer alvo (recebem só a trilha de nós).

Os ids vêm da extração do Miro; se o grafo mudar, atualize aqui.
"""

# jeito -> (estados da memória B, saídas do cadeirante, saídas da pessoa atraente,
#           personagens por rodada, entradas do painel)
SPEC = {
    1: dict(
        memB={"n52": ("nao", "sim"), "n53": ("sim", "sim"), "n54": ("nao", "nao"), "n55": ("sim", "nao")},
        cad={"n48": "nao", "n49": "sim", "n75": "nao", "n76": "sim", "n95": "nao", "n96": "sim"},
        pa={"n50": "nao", "n51": "sim", "n77": "nao", "n78": "sim", "n97": "nao", "n98": "sim"},
        kids_set={"n20": "1", "n21": "2", "n22": "3"},
        kids_out={"n45": "1", "n46": "2", "n47": "3", "n72": "1", "n73": "2", "n74": "3", "n92": "1", "n93": "2", "n94": "3"},
        chars=[["n28", "n66", "n86"], ["n29", "n67", "n87"], ["n30", "n68", "n88"]],
        panel_entries=["n04", "n05"],
    ),
    2: dict(
        memB={"n37": ("nao", "sim"), "n38": ("sim", "sim"), "n39": ("nao", "nao"), "n40": ("sim", "nao")},
        cad={"n28": "nao", "n29": "sim", "n53": "nao", "n54": "sim"},
        pa={"n30": "nao", "n31": "sim", "n55": "nao", "n56": "sim"},
        kids_set={},
        kids_out={},
        chars=[["n17", "n49"], ["n18", "n50"]],
        panel_entries=["n04"],
    ),
}


def problems(jeito: int, trace: list[str]) -> list[str]:
    spec, out, state = SPEC[jeito], [], {}
    for nid in trace:
        if nid in spec["memB"]:
            state["elevador"], state["atracao"] = spec["memB"][nid]
        if nid in spec["kids_set"]:
            state["la"] = spec["kids_set"][nid]
        if nid in spec["cad"] and state.get("elevador") != spec["cad"][nid]:
            out.append(f"{nid}: resultado do cadeirante não bate com elevador={state.get('elevador')}")
        if nid in spec["pa"] and state.get("atracao") != spec["pa"][nid]:
            out.append(f"{nid}: resultado da pessoa atraente não bate com atracao={state.get('atracao')}")
        if nid in spec["kids_out"] and state.get("la") != spec["kids_out"][nid]:
            out.append(f"{nid}: resultado das crianças não bate com la={state.get('la')}")
    for ids in spec["chars"]:
        if sum(trace.count(i) for i in ids) > 1:
            out.append(f"personagem repetido: {ids}")
    for e in spec["panel_entries"]:
        if trace.count(e) > 1:
            out.append(f"memória repetida: {e}")
    return out


# jeito-3: sem posições do Miro (roteiro escrito à mão), então as invariantes são pelo
# rótulo final (data.nodes[id].label = "Final ...") e pelo estado (vars), não por id de nó.
def problems3(last_label: str, ended: bool, vars: dict) -> list[str]:
    out = []
    if not ended:
        return ["não terminou num nó 'Final ...'"]
    atracao, ok = vars.get("atracao"), vars.get("ajudou_cadeirante")
    expect = {
        "Final Trágico 2": atracao == "nao",
        "Final Feliz 1": atracao == "sim" and ok == "sim",
        "Final Feliz 2": atracao == "nao" and ok == "sim",
        "Final Trágico 3": ok == "nao",
    }
    if last_label in expect and not expect[last_label]:
        out.append(f"{last_label} incoerente com atracao={atracao} ajudou_cadeirante={ok}")
    return out
