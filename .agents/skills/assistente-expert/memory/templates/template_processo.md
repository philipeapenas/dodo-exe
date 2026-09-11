# Template - Nota de processo

Formato da nota em `Vault/Processos/<Area ou OP>/<Nome do processo> DD-MM-AA.md`.

**A nota de processo e o registro de como um processo foi feito, pra nunca ser esquecido.** Quem
escreve e o time, no fim de cada processo rodado com o fundador: ele nao escreve mais a mao. O
padrao e o dele; o que muda e quem digita.

---

## O que esta nota E, e o que ela NAO E

E isso que decide o tamanho da nota: **o objetivo nao e ter especificacao tecnica de como cada
coisa foi feita.** Quem sabe fazer cada coisa com excelencia sao as skills especializadas, pelo
treinamento que receberam.

| A nota de processo carrega | Nao carrega |
|---|---|
| O fluxo: quais passos, em que ordem | Como cada passo e executado por dentro |
| Quem faz cada passo, quando nao for obvio | Comando, caminho de arquivo, nome de funcao, parametro |
| Quanto tempo levou | Justificativa de decisao tecnica |
| O que precisa estar pronto antes de comecar | Diagnostico de erro |

**A tecnica mora na `memory/` da skill que executa, nao aqui.** Se a nota de processo comecar
a explicar COMO fazer, o conhecimento passa a existir em dois lugares e um dos dois envelhece.
Quando faltar tecnica, o destino e treinamento da skill responsavel via `skill-expert`, nao
paragrafo nesta nota.

---

## O esqueleto, tirado das notas dele

```
# Processo de <nome do processo>:

> <uma linha de contexto, so quando muda como o processo roda>

1. <passo, na linguagem dele>
2. <passo>
3. <passo>

Qnt tempo p fazer: <tempo real>
```

**Tamanho alvo: 3 a 6 passos.** A mediana das notas operacionais dele em 28/08/2026 era de
cerca de 300 bytes. As notas longas da pasta `Dev/` sao tutorial que ele escreveu pra si
mesmo, nao o padrao de processo de operacao. Nao use elas de modelo.

Exemplo real, escrito por ele, que e o alvo de concisao:

```
Processo de criação dos reels da semana:

> Estilo: Motion control

1. Ter video original na pasta repertorio no drive
2. Fazer faceswap com capa do video p cada conta ativa
3. Fazer motion p cada conta ativa
```

---

## Regras de escrita

**Na linguagem dele, nao na nossa.** "Fazer faceswap com capa do video p cada conta ativa", nao
"executar a rotina de substituicao facial sobre o frame de capa". A nota e pra ele reconhecer o
processo em dois segundos.

**A linha de tempo entra sempre que houver tempo real.** `Qnt tempo p fazer: 1h15`. E o formato
dele e e o que faz o processo virar orcamento na hora de montar o dia. **Nunca invente o tempo**
- se ele nao cronometrou, a linha nao entra (ver a regra de nao preencher tempo por ele).

**Quando o fluxo atravessa varias skills, nomeie quem faz o passo.** E o que liga a nota de
processo ao catalogo de fluxos da `dodo-ia`. Um passo executado por uma skill so nao precisa de
nome: fica implicito.

**Sem emoji e sem travessao** (Regras de Ouro 11 e 21).

---

## Criar nova ou nutrir a que existe

**Padrao: nutrir a que existe.** Abra a pasta da area, procure processo com o mesmo proposito,
e atualize os passos que mudaram.

**Nota nova, com data nova, so quando o fluxo mudou a ponto de ser outro processo.** Nota que
so evolui fica sem data e vai sendo atualizada; quando o jeito de fazer muda de verdade, nasce
uma segunda com data, ao lado da primeira. Ao criar a segunda, linke a primeira numa linha, pra o historico nao
sumir.

**Onde:** `Vault/Processos/<Area ou OP>/`. Area nova so nasce quando o processo nao couber em nenhuma, e conferir a
pasta no disco antes de criar (`vault_structure.md`).

---

## Quando escrever

No **encerramento da sessao**, dentro do `auto_archive_protocol.md`, junto da nota de entrega.
E o passo que transforma o que a sessao fez em coisa repetivel.

**Nem toda sessao gera nota de processo.** So gera quando a sessao rodou um processo que vai se
repetir. Sessao de conversa, de decisao ou de correcao pontual nao gera. O criterio e o mesmo
da Regra de Ouro 20: se repete, ganha registro.
