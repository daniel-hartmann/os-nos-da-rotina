// Roda o motor JS (gamegen/runtime/engine.js) com uma interface de mentira.
//   node engine_harness.js DADOS.json auto SEED     -> joga sozinho; imprime {trace, events, vars}
//   node engine_harness.js DADOS.json script a|b|c  -> responde às interações na ordem (a "|" separa)
const fs = require("fs");
const path = require("path");
const { createGame } = require(path.join(__dirname, "..", "gamegen", "runtime", "engine.js"));

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const [, , file, mode, arg] = process.argv;
const data = JSON.parse(fs.readFileSync(file, "utf8"));
const events = [];
const trace = [];
const answers = mode === "script" ? arg.split("|") : [];
const next = () => {
  if (!answers.length) throw new Error("acabaram as respostas do roteiro");
  return answers.shift();
};

const ui = {
  clear: () => events.push(["clear"]),
  banner: (t) => events.push(["banner", t]),
  art: (t) => events.push(["art", t]),
  text: (t) => events.push(["text", t]),
  pending: (l, d) => events.push(["pending", l, d]),
  info: (t) => events.push(["info", t]),
  error: (t) => events.push(["error", t]),
  end: () => events.push(["end"]),
  debug: (id) => trace.push(id),
  autoMenu: (p, labels, i) => events.push(["menu", p, labels, i]),
  autoAsk: (p, a) => events.push(["ask", p, a]),
  waitContinue: async () => { events.push(["continue"]); next(); },
  menu: async (p, labels) => { events.push(["menu", p, labels]); return parseInt(next(), 10) - 1; },
  ask: async (p) => { events.push(["ask", p]); return next(); },
  confirmRestart: async () => { events.push(["restart?"]); return next() === "s"; },
};

(async () => {
  const opts = mode === "auto" ? { auto: true, rng: mulberry32(parseInt(arg, 10)) } : {};
  const game = createGame(data, ui, opts);
  let error = null;
  try { await game.play(); } catch (e) { error = String(e.message || e); }
  console.log(JSON.stringify({ trace, events, vars: game._state().vars, error }));
})();
