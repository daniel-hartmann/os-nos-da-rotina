import json
import shutil
import subprocess
from pathlib import Path

import pytest

from gamegen.model import GameError, load, missing_texts
from gamegen.targets import TARGETS

ROOT = Path(__file__).resolve().parent.parent
MINI = ROOT / "tests" / "fixtures" / "mini.json"
BASH = shutil.which("bash")


def build(tmp_path: Path, src: Path) -> Path:
    game = load(src)
    out = tmp_path / (src.stem + ".sh")
    out.write_text(TARGETS["bash"].render(game, out.name), encoding="utf-8")
    return out


def play(script: Path, stdin: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, str(script), *args], input=stdin, capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("name", ["jeito-1.json", "jeito-2.json"])
def test_real_inputs_load(name):
    game = load(ROOT / name)
    assert game.start == "n01"
    assert any(e.back for n in game.nodes.values() for e in n.succ), "esperava laços de volta ao início do dia"
    assert all(len(p.entries) >= 1 for p in game.panels.values())
    assert game.persistent_vars() == ["nome"]


@pytest.mark.parametrize("name", ["jeito-1.json", "jeito-2.json"])
def test_real_games_finish_in_auto_mode(tmp_path, name):
    script = build(tmp_path, ROOT / name)
    for seed in range(1, 30):
        r = play(script, "", "--auto", "--seed", str(seed))
        assert r.returncode == 0, r.stderr
        assert "— Fim —" in r.stdout
        assert "[erro]" not in r.stderr


def test_conditional_branch_and_quoting(tmp_path):
    script = build(tmp_path, MINI)
    r = play(script, "Ana\n1\n")
    assert r.returncode == 0
    # texto do jogo sai literal: nada é expandido pelo shell
    assert "UM $HOME `date` 100% \\n Ana" in r.stdout
    assert "FIM-UM" in r.stdout


def test_conditional_else_and_no_transition(tmp_path):
    script = build(tmp_path, MINI)
    r = play(script, "Bob\n2\n")
    assert "OUTRO" in r.stdout and "UM $HOME" not in r.stdout
    assert "nenhuma transição válida" in r.stderr  # n06 não tem 'senão'


def test_player_input_is_not_evaluated(tmp_path):
    script = build(tmp_path, MINI)
    r = play(script, "a'b\"c$(echo hi)`id`\n1\n")
    assert "a'b\"c$(echo hi)`id`" in r.stdout
    assert "uid=" not in r.stdout


def test_unknown_placeholder_is_rejected(tmp_path):
    doc = json.loads(MINI.read_text(encoding="utf-8"))
    doc["nodes"][4]["narrative"] = "oi {ninguem}"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(GameError, match="ninguem"):
        load(bad)


def test_missing_vs_silent_narrative():
    game = load(ROOT / "jeito-1.json")
    pending, _ = missing_texts(game)
    ids = {n.id for n in pending}
    assert "n09" in ids  # sem texto ainda
    assert "n13" not in ids  # narrative "" = silencioso de propósito
