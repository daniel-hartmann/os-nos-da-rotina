# gamegen — Os Nós da Rotina

Gera um jogo de texto interativo a partir de um grafo narrativo. `jeito-1.json` e `jeito-2.json`
vieram do board do Miro; `jeito-3.json` é um roteiro novo, escrito à mão diretamente no formato do
grafo (sem Miro por trás — veja `source` dentro do próprio arquivo). Os três seguem o mesmo schema
`narrative-flow/v1` e passam pelo mesmo gerador. Alvos: **bash** e **html**. O alvo **bat** (Windows)
está em andamento e fora do `-t all`, do site e do workflow. Novos alvos entram como módulos em
`gamegen/targets/`.

O roteiro-base (o texto original, antes de virar grafo) está em [roteiro.md](roteiro.md); o do
jeito-3 está em [roteiro-jeito-3.md](roteiro-jeito-3.md).

Dependências controladas por [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Uso

```bash
uv run python -m gamegen jeito-1.json            # gera dist/jeito-1.sh
uv run python -m gamegen jeito-2.json -o jogo.sh
uv run python -m gamegen jeito-1.json --check -v # só valida e lista os textos que faltam
uv run python -m gamegen jeito-1.json jeito-2.json jeito-3.json -t all   # bash + html em dist/
uv run python -m gamegen --site _site jeito-1.json jeito-2.json jeito-3.json   # site completo (o que o Pages publica)
uv run pytest                                    # testes
```

O script gerado é autocontido (bash 3.2+, roda no macOS sem instalar nada):

```bash
./dist/jeito-1.sh              # jogar
./dist/jeito-1.sh --auto       # joga sozinho, escolhendo ao acaso (testar o grafo)
./dist/jeito-1.sh --seed 7     # sorteios reprodutíveis
./dist/jeito-1.sh --no-pause   # sem "Enter para continuar" e sem limpar a tela (logs, testes)
./dist/jeito-1.sh --debug      # mostra id e rótulo de design de cada nó
```

Durante o jogo: número para escolher, `q` para sair.

## Páginas

O jogo é dividido em **páginas**: a pessoa lê, aperta Enter e a tela é limpa antes da próxima.
Cada `narrative` abre uma página nova; menus e perguntas (`ask`) aparecem na página do texto que
vem antes deles. Para juntar dois textos na mesma página, use `"page": "same"` no segundo. Se não
houver página aberta (por exemplo, logo depois de um menu), `same` abre uma página nova.
A tela só é limpa em terminal de verdade; com saída redirecionada ou `--auto`/`--no-pause` não sai
nenhum código de escape.

## Onde escrever os textos

Direto nos nós do JSON. Tudo é opcional; o que faltar aparece no jogo como
`[texto pendente] <rótulo do Miro>` (com o `draft`, se houver).

| campo       | para quê                                                                                   |
|-------------|--------------------------------------------------------------------------------------------|
| `narrative` | texto exibido ao entrar no nó. String ou lista de parágrafos. `""` = silencioso de propósito |
| `choice`    | texto do nó quando ele aparece como opção de menu (padrão: rótulo do Miro)                  |
| `prompt`    | pergunta do menu quando o nó ramifica (padrão: "O que você faz?")                           |
| `art`       | nome de uma arte em `arte/<nome>.txt`, exibida antes do texto (veja Artes ASCII)             |
| `page`      | `"new"` (padrão) abre página nova; `"same"` continua na página atual                        |
| `draft`     | nota de design; só aparece junto do aviso de texto pendente                                 |
| `set`       | `{"var": "valor"}` aplicado ao entrar no nó (estado do jogo)                                |
| `ask`       | `{"var": "nome", "prompt": "Digite seu nome:", "default": "X"}` lê uma resposta do jogador |
| `mode`      | como escolher entre vários sucessores: `choice` (jogador), `random` (sorteio), `conditional` |

Nas arestas: `when` (`{"var": "valor"}`) condiciona a aresta. `""`/`null` significa "ainda não definida".
Nos textos, `{nome}` é substituído pela variável `nome`.

## Regras de execução (iguais para todos os alvos)

* Nó com vários sucessores: por padrão o jogador escolhe. Se alguma aresta tem `when`, vira
  `conditional` (primeira que vale; a sem `when` é o "senão"). `random` sorteia entre as arestas
  cujo `when` vale.
* Aresta **para um painel** (Lembranças) = chamada de subfluxo: roda o subfluxo e volta. Se o painel
  tem mais de uma entrada, escolhe a entrada ainda não visitada (jogador ou sorteio, conforme `mode`).
  Arestas que *saem* de um painel são só anotação visual e são ignoradas.
* Aresta que volta a um nó anterior (final → "Na manhã do dia seguinte") pergunta se quer recomeçar.
  Recomeçar zera o estado, menos as respostas de `ask` (o nome).
* Textos e nomes nunca são interpretados pelo shell (`$`, crases e aspas saem literais).

## Estrutura

```
gamegen/model.py           lê/valida o JSON e resolve a semântica (independente do alvo)
gamegen/targets/bash.py    backend bash        gamegen/templates/bash.sh.j2
gamegen/cli.py             linha de comando
tests/                     pytest (inclui rodar os scripts gerados)
```

## Artes ASCII

A arte fica em arquivos de texto puro em `arte/<nome>.txt` (ao lado do JSON), sem escapes: `\`, aspas
e `$` saem exatamente como no arquivo. O nó só a referencia:

```json
{"id": "n03", "art": "onibus", "narrative": "DENTRO DO ONIBUS"}
```

A arte aparece no topo da página do nó, seguida de uma linha em branco e do texto. É embutida no
script na hora de gerar, então o jogo continua sendo um único arquivo. Um nó pode ter só a arte
(`"narrative": ""`). Dicas: até 78 colunas (o gerador avisa se passar), só ASCII, indentação faz
parte do desenho (linhas vazias no começo e no fim são ignoradas). Outra pasta: `--art-dir`.

Hoje tem quatro: `arte/onibus.txt` (o ônibus, em "DENTRO DO ÔNIBUS"), `arte/empresa.txt` (o prédio
da empresa) e `arte/garagem.txt` (a garagem com as baias), as duas em "NA EMPRESA", e
`arte/festa.txt` (a festa de aniversário), na LEMBRANÇA A — essa última só existe no jeito-1, que é
o único com essa lembrança; `jeito-3.json` também usa `onibus`/`empresa`/`garagem`, do mesmo jeito.
Quando um nó tem `art`, o texto dele entra na mesma página da arte por padrão; para encadear mais de
uma arte antes do texto, veja como `artEmpresa`/`artGaragem` fazem isso nos três `jeito-N.json` (nós
só de arte, com `"page": "same"` no nó seguinte).

## HTML e GitHub Pages

O alvo `html` gera um único arquivo (dados + motor JS + estilo). Enter/Espaço continuam, `1`-`9`
escolhem, e as artes ASCII vão em `<pre class="art">`. Todo texto entra por `textContent`, então
nomes digitados nunca viram HTML. Parâmetros úteis na URL: `?seed=7`, `?auto=1`, `?debug=1`.

`.github/workflows/pages.yml` roda os testes, gera o site (`--site`) e publica no GitHub Pages a cada
push em `main`. Configuração única: Settings > Pages > Source: **GitHub Actions**. O workflow fica na
raiz deste projeto, então ele só roda se `trabalho-01` for a raiz do repositório.

## Windows (.bat): pendente

`gamegen/targets/bat.py` gera um `.bat` que embute um motor em PowerShell (`runtime/engine.ps1`).
Foi executado com `pwsh` no Linux e passou nos testes manuais (jogo completo, entrada com caracteres
especiais, menu, `q`, fim de entrada), mas **não** foi validado no Windows nem em escala (400 partidas).
Gere com `-t bat`.
