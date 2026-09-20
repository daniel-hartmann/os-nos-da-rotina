/* Motor do jogo (alvo html). Segue as mesmas regras do alvo bash: veja gamegen/model.py.
 *
 * createGame(data, ui, opts) -> { play() }
 *   data  o JSON exportado por gamegen/export.py
 *   ui    interface assíncrona (o navegador implementa com DOM; os testes, com um roteiro):
 *           clear(), banner(title), art(text), text(text), pending(label, draft), info(text),
 *           error(msg), end(), debug?(id, kind, label), autoMenu?(prompt, labels, idx),
 *           async waitContinue(), async menu(prompt, labels) -> idx,
 *           async ask(prompt, def) -> string, async confirmRestart(label) -> bool
 *   opts  { rng: () => [0,1), auto: bool, nopause: bool }
 */
function createGame(data, ui, opts) {
  opts = opts || {};
  const rng = opts.rng || Math.random;
  const auto = !!opts.auto;
  const nopause = auto || !!opts.nopause;

  let vars = {};
  let visited = {};
  let pageOpen = false; // há texto na tela que a pessoa ainda não "passou adiante"
  let fresh = true; //     a tela acabou de ser limpa
  let hold = false; //     a próxima página se junta à atual (título + primeira página)

  const pick = (n) => Math.floor(rng() * n);
  const val = (k) => (vars[k] === undefined ? "" : vars[k]);
  const matches = (when) => Object.keys(when).every((k) => val(k) === when[k]);

  function interp(text) {
    let s = text;
    for (const v of data.interp) s = s.split("{" + v + "}").join(val(v));
    return s;
  }

  // ---------------------------------------------------------------- páginas
  function clearScreen() {
    ui.clear();
    fresh = true;
  }

  async function newPage() {
    if (hold) {
      hold = false;
      return;
    }
    if (pageOpen) {
      if (!nopause) await ui.waitContinue();
      pageOpen = false;
    }
    if (!fresh) clearScreen();
  }

  function beforeInput() {
    if (!pageOpen && !fresh) clearScreen();
    fresh = false;
  }

  async function show(kind, same, ...args) {
    if (!same || !pageOpen) await newPage();
    ui[kind](...args);
    pageOpen = true;
    fresh = false;
  }

  // ------------------------------------------------------------ interações
  async function menu(prompt, labels) {
    beforeInput();
    pageOpen = false;
    if (auto) {
      const idx = pick(labels.length);
      if (ui.autoMenu) ui.autoMenu(prompt, labels, idx);
      return idx;
    }
    return ui.menu(prompt, labels);
  }

  async function askVar(name, prompt, def) {
    beforeInput();
    let ans;
    if (auto) {
      ans = def || "X";
      if (ui.autoAsk) ui.autoAsk(prompt, ans);
    } else {
      for (;;) {
        ans = (await ui.ask(prompt, def)) || def;
        if (ans) break;
      }
    }
    vars[name] = ans;
    pageOpen = false;
  }

  function resetState() {
    const keep = {};
    for (const k of data.persistent) if (k in vars) keep[k] = vars[k];
    vars = keep;
    visited = {};
  }

  async function goBack(edge) {
    const label = data.nodes[edge.to].label;
    ui.info("↺ o fluxo volta para: " + label);
    fresh = false;
    pageOpen = false;
    if (auto) return "";
    if (await ui.confirmRestart(label)) {
      resetState();
      return edge.to;
    }
    return "";
  }

  const go = (edge) => (edge.back ? goBack(edge) : edge.to);

  function noTransition(id) {
    ui.error("[erro] nenhuma transição válida a partir de " + id + "; encerrando.");
    return "";
  }

  // --------------------------------------------------------------- painéis
  async function enterPanel(node, panelId) {
    const entries = data.panels[panelId].entries;
    let cands = entries.filter((e) => !visited[e]);
    if (cands.length === 0) cands = entries.slice();
    let chosen;
    if (cands.length === 1) {
      chosen = cands[0];
    } else if (node.mode === "random") {
      chosen = cands[pick(cands.length)];
    } else {
      const prompt = interp(node.prompt || data.panelPrompt);
      chosen = cands[await menu(prompt, cands.map((e) => interp(data.nodes[e].menu)))];
    }
    visited[chosen] = true;
    await runFrom(chosen);
  }

  // ------------------------------------------------------------------ nós
  async function runNode(id) {
    const n = data.nodes[id];
    if (ui.debug) ui.debug(id, n.kind, n.label);
    if (n.art) await show("art", n.same, n.art);
    const same = n.same || !!n.art;
    if (n.narrative === null) {
      if (n.kind === "process") await show("pending", same, n.label, n.draft);
    } else if (n.narrative) {
      await show("text", same, interp(n.narrative));
    }
    if (n.ask) await askVar(n.ask.var, interp(n.ask.prompt), n.ask.default);
    for (const k of Object.keys(n.set)) vars[k] = n.set[k];
    for (const p of n.calls) await enterPanel(n, p);

    const succ = n.succ;
    if (succ.length === 0) return "";
    if (n.mode === "conditional") {
      const hasWhen = succ.some((e) => e.when);
      const fallback = succ.find((e) => !e.when);
      for (const e of succ) if (e.when && matches(e.when)) return go(e);
      if (!hasWhen || fallback) return go(fallback);
      return noTransition(id);
    }
    if (n.mode === "random" && (succ.length > 1 || succ[0].when)) {
      const elig = succ.filter((e) => !e.when || matches(e.when));
      if (elig.length === 0) return noTransition(id);
      return go(elig[pick(elig.length)]);
    }
    if (succ.length === 1) return go(succ[0]);
    const idx = await menu(interp(n.prompt || data.defaultPrompt), succ.map((e) => interp(data.nodes[e.to].menu)));
    return go(succ[idx]);
  }

  async function runFrom(start) {
    let next = start;
    while (next) next = await runNode(next);
  }

  async function play() {
    clearScreen();
    ui.banner(data.title);
    fresh = false;
    hold = true;
    await runFrom(data.start);
    ui.end();
  }

  return { play, _state: () => ({ vars, visited }) };
}

if (typeof module !== "undefined" && module.exports) module.exports = { createGame };
