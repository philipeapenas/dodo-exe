# Playbook da Nota Operacional

**Versao:** 1.0 | **Data:** 16/08/2026 | **Owner:** assistente-expert
**Origem:** o fundador determinou que o formato de uma nota mestre que deu certo vira o padrao de **toda** nota operacional do vault.

Toda operacao tem **uma** nota mestre: `Operações/OP <Nome>/Tudo sobre <Nome> DD-MM-AA.md`.
Ela e o documento que responde "o que e essa operacao" sem que ninguem precise perguntar.

O modelo em branco vive no vault, em `Recursos/Documentos/Modelo de nota operacional.md`.

---

## O esqueleto, na ordem

1. **Proposito Definido** - por que a operacao existe, alem de dinheiro
2. **Objetivo da Operacao** - o que ela precisa alcancar
3. **Identidade** *(OP propria)* ou **Quem e** *(OP de cliente)* - ver a regra abaixo
4. **Equipe** - quem faz o que
5. **Metas** - tres horizontes, ver a regra abaixo
6. **Esteira de Produtos** - o que se vende, do primeiro ao ultimo degrau
7. **Publico alvo**
8. **Promessa** - a frase que o cliente le
9. **Mecanismo unico** - ver a regra abaixo
10. **O que vem no produto** - a lista de entregavel, separada do mecanismo
11. **Prova**
12. **Garantia**
13. **Funil** - prospeccao ativa e passiva
14. **Ofertas / Entregas** - cada oferta com preco e o que inclui
15. **Escopo de entrega** - quem faz, o que esta incluso, e **onde termina**
16. **Economia da oferta** - quanto sobra por venda e onde esta o custo real
17. **FAQ**
18. **Planos**
19. **Decisoes Estrategicas** - com link pra nota de cada uma
20. **Projetos** - com o caminho de cada um
21. **Decisoes em aberto**
22. **Pendencias** - tabela `O que | De quem depende`

---

## As tres regras que o fundador travou

### Metas: cada horizonte e de um tipo diferente

| Horizonte | Tipo | Por que |
| --- | --- | --- |
| **Curto prazo** (semana) | **Processo** - so depende de nos | No comeco nao existe dado de conversao. Cobrar de si um numero que nao se controla so gera frustracao |
| **Medio prazo** (mes) | **Resultado** - depende do mercado | E aqui que numero de venda aparece |
| **Longo prazo** (6 meses) | **Estrutura** - o que roda sem o fundador | O que a operacao sabe fazer sozinha |

> **Meta de curto prazo NUNCA e numero de venda.** Se aparecer "vender X essa semana", esta errada.

### Mecanismo unico: responde por que NOS conseguimos e o concorrente nao

Deriva do **Proposito Definido** da operacao. Se o proposito e automatizar processo, o mecanismo
explica como essa mesma automacao derruba o custo e o prazo aqui dentro.

**Nao e lista de entregavel.** "Domínio incluso, funciona no celular, botao de WhatsApp" e o que
o cliente **recebe** - isso vai na secao 10, separada. O mecanismo e o que torna possivel
entregar aquilo por aquele preco naquele prazo.

### Identidade: depende de quem e a operacao

- **Operacao de CLIENTE** -> bloco **Quem e** (quem e o negocio, o que faz, historico).
- **Operacao da propria Dodo** -> **Identidade** (marca, endereco na internet, WhatsApp, tom de
  voz) **mais Equipe**. O padrao "Quem e" nao se aplica.

O resto do esqueleto e igual nos dois casos.

---

## Ao escrever

- **Regra de Ouro 13 vale aqui**: objetiva, linguagem de negocio, sem caminho de arquivo nem
  nome de funcao. A excecao da Regra 16 e so pra nota de tarefa.
- **Sem emoji** (Regra 11).
- Secao ainda nao definida fica com `(a definir)` explicito, **nao sai da nota**. A lacuna
  visivel e informacao: mostra ao fundador o que falta decidir.
- A nota nasce em `Tarefas/<Mes>/` enquanto a tarefa esta aberta, e **muda pra
  `Operações/OP <Nome>/` no encerramento** - preservando o nome do arquivo, senao quebra
  wikilink.

## Relacionados

- `vault_structure.md` - onde a nota mora
- `auto_archive_protocol.md` - o encerramento que move a nota pra pasta da operacao
