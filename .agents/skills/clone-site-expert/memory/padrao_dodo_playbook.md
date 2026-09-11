# Playbook do Padrao Dodo e do Time

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** clone-site-expert

Como decidir o que reconstruir, e quem faz o que.

---

## 1. Nao existe refatorar bundle minificado

O fundador pediu que o codigo do clone ficasse no padrao da casa. Dito de forma direta: **num bundle React de 170 KB numa linha so, isso e impossivel.** Nao tem funcao pra extrair, nome pra melhorar nem responsabilidade pra separar.

Isso nao anula o pedido - **desloca** ele. O padrao Dodo se aplica ao que voce **reescreve**, e a decisao de reescrever passa a ser uma etapa formal do processo, com criterio.

---

## 2. Criterio de reconstruir ou manter, por PAGINA

| Situacao da pagina | Decisao | Quem |
| --- | --- | --- |
| Tem formulario, ou vai receber logica nova | **Reconstroi limpa** | dev-expert |
| Copy presa dentro do bundle (FAQ, textos de card) | **Reconstroi limpa** | dev-expert |
| So conteudo, sem interacao | Mantem o bundle | ninguem mexe |
| Interatividade complexa que ja funciona | Mantem, e **registra a divida** | clone-site-expert anota |

**Reconstruir preserva a estrutura, nao a descaracteriza.** Mesmo HTML semantico, mesmas classes, mesmo CSS - troca o motor por baixo. Foi assim que a pagina de briefing saiu de React pra HTML puro sem mudar um pixel.

**O que for mantido fica documentado como divida.** Nunca finja que foi otimizado.

---

## 3. A ordem do time (a ordem importa)

```
1. clone-site-expert   diagnostico tecnico + mapa de onde mora cada texto
2. copywriter-expert   dissecacao da copy (recebe o mapa do passo 1)
3. clone-site-expert   higienizacao, so depois do OK do fundador no inventario
4. frontend-expert     CSS  ─┐  handoffs sequenciais,
5. dev-expert          JS   ─┘  frontend SEMPRE primeiro
6. clone-site-expert   conferencia final
7. vercel-expert       publica e devolve o link
```

**Por que o diagnostico vem antes da copy:** e ele que descobre onde a copy mora. No precedente, metade dela estava dentro do JavaScript - a `copywriter-expert`, lendo so o HTML, teria perdido as seis respostas do FAQ e dado nota numa pagina incompleta.

**Passos 4 e 5 sao inegociaveis e separados.** CSS e sempre da `frontend-expert`, JS e sempre da `dev-expert`, em dois handoffs. Nunca combine, mesmo quando pareçam grudados - e regra dura do fundador.

**O `design.md` deixa de ser so entrega e vira insumo do passo 4:** e o contrato que diz a `frontend-expert` quais tokens e classes preservar, pra reconstrucao nao mudar o visual.

---

## 4. A armadilha do Tailwind purgado

Espelho traz o CSS **ja compilado e podado**: so existem as classes que o site original usava. Escrever uma classe utilitaria nova nao da erro - da **elemento sem estilo**, e nada avisa.

Antes de escrever HTML novo, extraia o vocabulario disponivel e escreva dentro dele. Rode `conferir_classes.py` depois. No precedente ele pegou `ml-1` e `pb-20` inexistentes: o logo estava com as duas palavras grudadas e ninguem tinha percebido.

Estilo genuinamente novo entra em **arquivo proprio** (padrao `tema.css`, `movimento.css`), nunca como utilitario Tailwind.

---

## 5. Conteudo duplicado: o aviso comercial

A copy e o layout sao do dono original. Modelar a estrutura e pratica normal, mas **publicar o texto igual coloca os dois sites competindo pelas mesmas palavras no Google, e o mais novo perde.**

Levante isso no diagnostico, uma vez, de forma pratica e sem moralizar. E argumento a favor de a promessa nova reescrever a copy, nao so trocar o nome.
