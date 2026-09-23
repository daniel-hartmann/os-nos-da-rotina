"""Motor JS (alvo html): mesmas regras do bash, testado com uma interface de mentira em node."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from gamegen.export import to_json
from gamegen.model import load
from tests.invariants import problems, problems3

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "tests" / "engine_harness.js"
FIX = ROOT / "tests" / "fixtures"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node não encontrado")


def run(tmp_path: Path, src: Path, mode: str, arg: str) -> dict:
    data = tmp_path / (src.stem + ".data.json")
    data.write_text(to_json(load(src)), encoding="utf-8")
    r = subprocess.run([NODE, str(HARNESS), str(data), mode, arg], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def kinds(res: dict) -> list[str]:
    return [e[0] for e in res["events"]]


@pytest.mark.parametrize("jeito", [1, 2])
def test_real_games_are_coherent_in_auto_mode(tmp_path, jeito):
    src = ROOT / f"jeito-{jeito}.json"
    data = tmp_path / "d.json"
    data.write_text(to_json(load(src)), encoding="utf-8")
    seen: set[str] = set()
    for seed in range(1, 121):
        r = subprocess.run([NODE, str(HARNESS), str(data), "auto", str(seed)], capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout)
        assert res["error"] is None
        assert res["events"][-1] == ["end"]
        assert problems(jeito, res["trace"]) == [], f"seed {seed}"
        seen.update(res["trace"])
    expected = {n.id for n in load(src).nodes.values()}
    assert expected - seen == set(), "nós que nunca rodaram"


def test_jeito3_reaches_every_ending_and_stays_coherent(tmp_path):
    # jeito-3 não tem "memória A/B por sorteio": é sempre a mesma Lembrança B, e o jogo termina
    # num dos 5 "Final ..." (2 deles são saídas imediatas, sem passar pela Parada 5).
    src = ROOT / "jeito-3.json"
    game = load(src)
    data = tmp_path / "d.json"
    data.write_text(to_json(game), encoding="utf-8")
    seen: set[str] = set()
    endings: dict[str, int] = {}
    for seed in range(1, 301):
        r = subprocess.run([NODE, str(HARNESS), str(data), "auto", str(seed)], capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout)
        assert res["error"] is None
        assert res["events"][-1] == ["end"]
        seen.update(res["trace"])
        last = game.nodes[res["trace"][-1]]
        ended = last.label.startswith("Final ")
        assert problems3(last.label, ended, res["vars"]) == [], f"seed {seed}: {last.label} {res['vars']}"
        endings[last.label] = endings.get(last.label, 0) + 1
    assert {n.id for n in game.nodes.values()} - seen == set(), "nós que nunca rodaram"
    assert len(endings) == 5, f"esperava os 5 finais, veio {endings}"


def test_pages_wait_and_clear(tmp_path):
    # PRIMEIRA (com o título) -> Enter -> limpa -> SEGUNDA + TERCEIRA (page: same) + menu -> escolha
    res = run(tmp_path, FIX / "pages.json", "script", "|1")
    ev = res["events"]
    assert kinds(res) == ["clear", "banner", "text", "continue", "clear", "text", "text", "menu", "clear", "text", "end"]
    assert [e[1] for e in ev if e[0] == "text"] == ["PRIMEIRA", "SEGUNDA", "TERCEIRA", "FIM-UM"]
    assert ev[7][2] == ["UM", "DOIS"]


def test_art_goes_before_text_on_the_same_page(tmp_path):
    res = run(tmp_path, FIX / "art.json", "script", "|")
    art = (FIX / "arte" / "gato.txt").read_text(encoding="utf-8").rstrip("\n")
    assert kinds(res) == ["clear", "banner", "art", "text", "continue", "clear", "text", "end"]
    assert res["events"][2][1] == art


def test_conditional_else_no_transition_and_interpolation(tmp_path):
    ok = run(tmp_path, FIX / "mini.json", "script", "Ana|1|")
    texts = [e[1] for e in ok["events"] if e[0] == "text"]
    assert texts[0].startswith("Olá, ''")  # o texto do nó vem antes do ask: o nome ainda não existe
    assert "UM $HOME `date` 100% \\n Ana" in texts and "FIM-UM" in texts  # depois, interpola; nada é expandido
    els = run(tmp_path, FIX / "mini.json", "script", "Bob|2")
    assert "OUTRO" in [e[1] for e in els["events"] if e[0] == "text"]
    assert any(e[0] == "error" and "nenhuma transição" in e[1] for e in els["events"])


def test_name_survives_in_state(tmp_path):
    src = ROOT / "jeito-2.json"
    data = tmp_path / "d.json"
    data.write_text(to_json(load(src)), encoding="utf-8")
    res = json.loads(subprocess.run([NODE, str(HARNESS), str(data), "auto", "7"], capture_output=True, text=True).stdout)
    assert res["vars"]["nome"] == "X"
