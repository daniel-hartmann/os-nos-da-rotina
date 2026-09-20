# gamegen — Os Nós da Rotina

Gera um jogo de texto interativo a partir do grafo narrativo (`jeito-1.json`, `jeito-2.json`),
exportado do Miro. Hoje há um alvo, **bash**; Windows e HTML entram como novos módulos em
`gamegen/targets/`.

Dependências controladas por [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Uso

```bash
uv run python -m gamegen jeito-1.json            # gera dist/jeito-1.sh
uv run python -m gamegen jeito-2.json -o jogo.sh
uv run python -m gamegen jeito-1.json --check -v # só valida e lista os textos que faltam
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
# os-nos-da-rotina
