# Os Nós da Rotina — Roteiro

Por

Angelo
Daniel
Luis

Setembro, 2026

---

> Este é o roteiro-base do jogo, do jeito que a equipe escreveu no documento de design.
> Dele nascem os dois fluxos jogáveis, [`jeito-1.json`](jeito-1.json) (5 ou 6 pontos de
> interação, com as duas lembranças) e [`jeito-2.json`](jeito-2.json) (3 ou 4 pontos, com
> só uma lembrança sorteada). Onde uma cena tem mais de um resultado possível, o texto
> definitivo de cada resultado já está escrito nos dois JSONs; aqui ficam o rascunho e as
> notas de estado entre parênteses/colchetes, do jeito que a equipe as escreveu. Para ver
> o que ainda está pendente em cada fluxo, rode `uv run python -m gamegen jeito-1.json --check -v`.

## Abertura

> Digite seu nome: **X**

## NA EMPRESA

Na manhã do dia seguinte, após o tradicional café da manhã de pão com ovo e muito café
preto, X chega na garagem da empresa para entrar no ônibus e iniciar mais um dia de
trabalho.

## DENTRO DO ÔNIBUS

Você se lembra da interação com as crianças no aniversário do seu sobrinho *[LEMBRANÇA A]*

**Parada 1: pessoas aleatórias**

*[LEMBRANÇA B]*

**Parada 2: crianças**

- **LA1.** As crianças são suas amigas, vc sabe os nomes e elas sentam perto
- **LA2.** As crianças têm medo de vcs e sentam no fundo
- **LA3.** As crianças tentam ser suas amigas, sentam perto por 1 parada e depois vão pro meio

**Parada 3: cadeirante**

Você pára o ônibus e:

- Desce do ônibus
  - **LB1.** cadeirante
  - **LB2.** consequência física ou demora demais
- **PB1.** Pára e não desce. Alguma criança tenta ajudar e morre. Fim do dia. *[Vai para o início]*
- **PB2.** Não pára. Alguém no ônibus te odeia.

**Parada 4: pessoa atraente**

- Se LB2, a pessoa atraente te xinga.
- Se LB1, a pessoa atraente é simpática.
- Se PB2, ...

**Parada 5: pessoa estranha entra pela porta de trás sem pagar**

Se LA2, você vê pelo espelho que a pessoa estranha está muito perto das crianças. Por
mais que você não goste de crianças, fica preocupado com elas. Por algumas quadras fica
verificando a situação pelo espelho retrovisor. Até que em uma sinaleira não percebe o
sinal vermelho em tempo, quando percebe freia, mas é tarde demais. O ônibus encosta no
carro da frente, causando um pequeno dano. Hora de voltar para a garagem. *[Volta para o
início]*

---

## LEMBRANÇA A

### CASA DA SUA IRMÃ, ANIVERSÁRIO DE CRIANÇA

Você lembra que sua irmã está grávida e logo vai ser tio. Imagina uma festa de
aniversário de criança em um futuro não tão distante. Crianças de todas idades correndo
pela casa, muitas brincadeiras e comidas totalmente baseadas em açúcar. A mistura
perfeita para a maior gritaria e agitação que já presenciou.

- **LA1.** — Criança é tudo de bom. *[gosta de criança]*
- **LA2.** — Tomara que essa criança demore pra nascer. *[não gosta de criança]*
- **LA3.** — Vou comer muitos brigadeiros nos próximos anos. *[indiferente]*

*[FIM DA LEMBRANÇA A]*

---

## LEMBRANÇA B

### ESCRITÓRIO DA EMPRESA DE ÔNIBUS, CURSO PREPARATÓRIO

Você lembra de uma pessoa atraente que conheceu na capacitação profissional da empresa
de transportes Viação Rapidão. Vocês estavam juntos em um curso, quando você percebeu
ela te olhando.

- **LB1.** Dar um oi simpático.
- **LB2.** Dar uma cantada.
- **LB3.** Finge indiferença e presta atenção na aula.

**LB1.** A pessoa atraente te chama pra sentar do lado dela.

- **LB1.A.** Aceitar.
- **LB1.B.** Prestar atenção na aula. Eu falo com ela depois.

> **LB1.A.** Você e a pessoa atraente começam a conversar por horas a fio. Vocês
> descobrem que têm muito em comum um com o outro. É amor à primeira vista. *(Não sabe
> usar o elevador, tem atração mútua)*
>
> **LB1.B.** Você presta atenção no curso para evitar agitar a aula, e quando percebe,
> Daniela saiu da sala. Você a perde de vista. *(Sabe usar o elevador, tem atração mútua)*

**LB2.** Daniela fica puta e faz escândalo na sala de aula.

- **LB2.A.** Pedir desculpa e voltar a prestar atenção na aula
- **LB2.B.** Fazer um escândalo e dizer que é culpa dela que deu moral.

> **LB2.A.** Você fica mal visto com a pessoa atraente e termina o curso. *(Sabe usar o
> elevador, sem atração)*
>
> **LB2.B.** Você é expulso do curso. *(Não sabe usar o elevador, sem atração)*

**LB3.** Você completa o curso *(Sabe usar o elevador, sem atração)*

*[FIM DA LEMBRANÇA B]*
