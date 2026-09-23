# Os Nós da Rotina — Roteiro (jeito 3: 3 ou 4 interações)

> Versão nova, escrita direto para 3 ou 4 pontos de interação. Diferente do [roteiro.md](roteiro.md)
> original (que veio do Miro e gerou `jeito-1.json`/`jeito-2.json`), este daqui não passou pelo
> board — foi escrito à mão e virou [`jeito-3.json`](jeito-3.json) diretamente. Onde o texto abaixo
> deixava uma decisão em aberto, listei a escolha que fiz em **Decisões da implementação**, no fim.

## PRÓLOGO (fica fora do loop)

Você é Jorge e recentemente começou o emprego como motorista de ônibus na sua cidade. Seu trabalho
é monótono, porém muito importante. Os horários precisam ser cumpridos à risca, pois muitas pessoas
dependem da sua pontualidade. Na sua casa, você vai dormir cedo porque sabe que terá um longo dia
pela frente amanhã.

## NA EMPRESA

Na manhã do dia seguinte, após o tradicional café da manhã de pão com ovo e muito café preto, Jorge
chega na garagem da empresa para entrar no ônibus e iniciar mais um dia de trabalho.

## DENTRO DO ONIBUS

Já dentro do ônibus, com mais um cafézinho na mão, Jorge conduz o veículo para fora da garagem. Uma
memória então lhe vem à cabeça, o curso preparatório da empresa. *[INÍCIO LEMBRANÇA B]*

**PARADA 1** — Pessoas aleatórias entram no ônibus.

**PARADA 2** — Carla entra no ônibus.

> Se tem atração (LBB: 1):
>
> Você percebe Y entrando no ônibus. Uma visão alegre para o seu dia. Ela parece mais linda do que
> da outra vez que vocês se viram. Ela esbanja um lindo sorriso, claramente muito feliz em lhe ver.
>
> - **Opção 1.** Sorrir de volta para Y. *(Ela senta pertinho de você.)*
> - **Opção 2.** Fingir indiferença. Estou em horário de trabalho e não posso perder tempo. *(Ela
>   senta no meio do ônibus para não incomodar)*

> Se não tem atração (LBB: 0):
>
> Você percebe Y entrando no ônibus. Ela nota você e imediatamente faz cara de desprezo, e vocês
> dois instantaneamente se lembram que tudo poderia ter sido diferente se você não tivesse sido um
> babaca da última vez que vocês se viram. Ela passa por você vagarosamente, quase como se
> esperasse que você dissesse algo.
>
> - **Opção 1.** Foi mal pela outra vez. Eu estava nervoso. *(Ela acha escroto igual, mas senta no
>   meio do ônibus.)*
> - **Opção 2.** Tá olhando o que? *(Ela fica furiosa e vai para o fundo do ônibus)*
> - **Opção 3.** Dizer nada. *(Ela vai para o fundo do ônibus)*

**PARADA 3** — Pessoas aleatórias entram no ônibus. Um homem entrou sem pagar no fundo do ônibus e
você não viu.

> Se Y sentou no fundo do ônibus:
>
> Visivelmente frustrado, você não percebe que alguém entrou pela porta traseira do ônibus, e está
> ali incomodando os passageiros. Você nota, através do seu espelho, que Y está sendo incomodada
> por essa pessoa.
>
> - **Opção 1.** "Vou parar o ônibus e tirar esse cara daqui." *(Y agradece e vai sentar no meio do
>   ônibus)*
> - **Opção 2.** "Vou é fazer nada. Ela que se vire." *(O cara estranho incomoda Y até ela tomar
>   uma atitude por conta própria, dando um tiro no homem. Seu ônibus virou uma cena do crime e o
>   dia acaba aqui. = **Final Trágico 1**)*

**PARADA 4** — Cadeirante.

> Se sabe usar o elevador:
>
> Você enxerga que na próxima parada tem um cadeirante esperando para entrar no ônibus. Você
> prestou atenção no treinamento, mas sabe que isso vai custar um pouco de tempo no dia de seus
> passageiros.
>
> - **Opção 1.** Parar o ônibus e operar o elevador. *(Os passageiros compreendem, e se LBB = 1 Y
>   fica ainda mais apaixonada = **Final Feliz 1**)*
> - **Opção 2.** Ignorar a parada do cadeirante *(Os passageiros reclamam da injustiça com o
>   cadeirante, e se LBB = 0, você é denunciado para a empresa de motorista = **Final trágico 2**)*

> Se não sabe usar o elevador:
>
> Você enxerga que na próxima parada tem um cadeirante esperando para entrar no ônibus. Uma gota de
> suor frio pinga da sua testa, porque você claramente não sabe operar o elevador do ônibus. Isso
> estava no curso de formação em algum momento?
>
> - **Opção 1.** Tentar operar o elevador de qualquer forma *(Você demora 15 minutos para subir o
>   cadeirante, e machuca sua mão no processo.)*
> - **Opção 2.** Ignorar a parada do cadeirante *(Os passageiros reclamam da injustiça com o
>   cadeirante, e se LBB = 0, você é denunciado para a empresa de motorista = **Final trágico 2**)*

**PARADA 5** — Mais pessoas aleatórias.

- Se Y gosta de ti, operou bem o elevador = **Final feliz 1**
- Se Y não gosta de ti, mas tá salva e operou bem o elevador = **Final feliz 2**
- Se Y não gosta de ti, mas tá salva e você não operou bem o elevador = **Final trágico 3**

## FINAIS

**Final feliz 1**

Pouco a pouco, os passageiros começam a descer do ônibus em seus destinos. Carla faz questão de
deixar o zap dela anotado em um pedaço de papel no bolso da sua jaqueta. Ela lhe dá uma piscadinha
e pede que você mande mensagem pra ela. Hoje foi um bom dia.

**Final feliz 2**

Pouco a pouco, os passageiros começam a descer do ônibus em seus destinos. Carla desce do ônibus
te dando um olhar pesado. Acho que vocês dois podem concordar que as coisas poderiam ter sido
diferentes em outros momentos.

**Final trágico 1**

Y tomou uma medida drástica ao se defender de um homem maníaco. Infelizmente isso inutiliza o
ônibus completamente, e traumatiza uma velhinha que assistiu toda a situação. Todos estão bem, mas
você precisa levar o ônibus de volta para a garagem.

**Final trágico 2**

Você recebe uma ligação da empresa no comunicador do ônibus. O seu chefe está furioso! Como assim
você ignorou uma parada com cadeirante? Que espécie de motorista você é? Você é ordenado a fechar a
linha e retornar imediatamente para a garagem. E é bom que isso não se repita amanhã! - Diz o chefe.

**Final trágico 3**

O peso do julgamento dos passageiros sobre a sua inaptidão no seu trabalho pesa cada vez mais alto
na sua consciência. Você frequentemente checa no espelho para ver se Carla dá a mínima para você,
mas você acaba perdendo a atenção e não percebe um sinal vermelho. O ônibus encosta no carro da
frente, causando um pequeno dano. Todos os passageiros são liberados, e você precisa levar o carro
de volta para a garagem.

## LEMBRANÇA B

### ESCRITÓRIO DA EMPRESA DE ÔNIBUS, CURSO PREPARATÓRIO

Jorge lembra de Carla, uma pessoa atraente que conheceu na capacitação profissional da empresa de
transportes Viação Rapidão. Vocês estavam juntos em um curso, quando você percebeu a presença. Em
algum instante, suas visões se cruzaram.

- **LB1.** Dar um oi simpático.
- **LB2.** Falar uma cantada.
- **LB3.** Finge indiferença e presta atenção na aula.

**LB1.A.** Carla te chama pra sentar do lado dela.

- **LB1.A.A.** Aceitar.
- **LB1.A.B.** Prestar atenção na aula. Eu falo com ela depois.

> **LB1.A.A.** Você e Carla começam a conversar por horas a fio. Vocês descobrem que têm muito em
> comum um com o outro. É amor à primeira vista. *(Não sabe usar o elevador, tem atração mútua)*
>
> **LB1.A.B.** Você presta atenção no curso para evitar agitar a aula, e quando percebe, Carla saiu
> da sala. Você a perde de vista. *(Sabe usar o elevador, tem atração mútua)*

**LB2.A.** Carla fica puta e faz escândalo na sala de aula.

- **LB2.A.A.** Pedir desculpa e voltar a prestar atenção na aula
- **LB2.A.B.** Fazer um escândalo e dizer que é culpa dela que deu moral.

> **LB2.A.A.** Você fica mal visto com Carla e termina o curso. *(Sabe usar o elevador, sem
> atração)*
>
> **LB2.A.B.** Você é expulso do curso. *(Não sabe usar o elevador, sem atração)*

**LB3.** Você completa o curso *(Sabe usar o elevador, sem atração)*

*[FIM DA LEMBRANÇA B]*

---

## Decisões da implementação

Coisas que o texto acima deixava em aberto e que eu precisei decidir para o jogo rodar. Estão
marcadas como `unmapped_notes` dentro do próprio [`jeito-3.json`](jeito-3.json):

- **Carla, no lugar de "Y"** — este roteiro já chama ela de Carla na Lembrança B inteira, no título
  da Parada 2 e nos dois Finais Feliz, mas ainda usa "Y" solto no resto (Parada 2/3, Parada 5 e no
  Final Trágico 1) — dá pra ver que é o mesmo nome ainda sendo espalhado pelo texto. Usei **Carla**
  em todo canto no jogo, inclusive nesses "Y" que sobraram, pra não ficar incoerente (uma hora com
  nome, outra sem). Se algum desses "Y" era pra ser outra coisa, me avisem.
- **2ª pessoa, não 3ª** — duas frases novas trocaram "você" por "Jorge" ("Jorge conduz o veículo...",
  "Jorge lembra de Carla..."), mas todo o resto do jogo (inclusive a frase logo depois, na mesma
  cena) fala na 2ª pessoa ("você conduz", "você percebeu"). Para não misturar as duas vozes no meio
  do texto, mantive "você" nessas duas frases também. Se for pra virar o jogo inteiro pra 3ª pessoa,
  aí sim eu troco tudo, não só essas duas.
- **Parada 4, opção "Ignorar", quando ela gosta de você** — o texto só diz o que acontece se ela
  *não* gosta de você (denúncia = Final trágico 2). Se ela gosta e mesmo assim você ignora o
  cadeirante, não fica um final imediato definido; assumi que o jogo segue pra Parada 5 do jeito
  normal, só que sem ter ajudado o cadeirante.
- **Parada 5, combinação que falta na tabela** — a tabela de finais cobre 3 das 4 combinações
  possíveis de (ela gosta de você) × (você ajudou o cadeirante). Falta "ela gosta de você, mas você
  não ajudou". Assumi que cai no Final Trágico 3 também (o texto dele não depende de gostar ou não
  gostar), mas é um chute meu.
