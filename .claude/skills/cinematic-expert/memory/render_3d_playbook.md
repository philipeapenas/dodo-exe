# Playbook de Render 3D em Codigo

**Versao:** 1.0 | **Data:** 29/08/2026 | **Owner:** cinematic-expert
**Origem:** estudo do fundador sobre sites 3D interativos com IA (conteudo de Gustavo Campelo), aprovado como treinamento.

Este playbook cobre a cena 3D construida em CODIGO, sem arquivo de modelo. E o irmao do `anatomia_prompt_cinematografico.md`: la a cena e video gerado no Higgsfield e reproduzido em canvas; aqui a cena e geometria Three.js escrita em TypeScript, que roda ao vivo e reage ao mouse e a rolagem.

Leia junto com `receitas_por_nicho.md`. O orcamento de efeito do nicho manda aqui tambem: 3D nao e permissao pra encher o site.

---

## 1. As duas ferramentas instaladas

Instaladas em `~/.claude/skills/` em 29/08/2026, nivel do usuario (valem em qualquer projeto, nao vivem no repositorio do workspace).

| Skill | Papel | Licenca |
| --- | --- | --- |
| `img2threejs` | Imagem de referencia vira modelo Three.js procedural em codigo. Devolve um spec JSON mais uma factory TypeScript que retorna um `THREE.Group`, mais folha de comparacao referencia contra render. | Apache-2.0 |
| `gsap-scrolltrigger`, `gsap-core`, `gsap-timeline`, `gsap-performance`, `gsap-plugins`, `gsap-utils`, `gsap-react`, `gsap-frameworks` | Skills oficiais da GreenSock. Ensinam o agente a usar GSAP do jeito certo. | MIT |

**Regra de delegacao:** ao escrever a coreografia de rolagem, ACIONE as skills `gsap-*` em vez de escrever GSAP de cabeca. Bug de animacao nasce de pratica errada, nao de falta de talento. `gsap-scrolltrigger` pro scroll e pinning, `gsap-performance` quando a cena pesar.

**Nao confunda com o `movimento_playbook.md` da frontend-expert.** Aquele e o sistema de movimento padrao dos sites da Dodo (pilha servida de `assets/js/vendor/`, dois modos, calmo e completo). Ele continua valendo. As skills `gsap-*` sao consultoria de como escrever, nao substituem a pilha.

---

## 2. Quando 3D em codigo entra

Entra quando o objeto E o argumento de venda, ou quando o nicho tem licenca pra imersao:

- Jogo, filme, produto tecnologico, produto fisico com forma marcante (drone, movel, embalagem).
- Marca que vende a propria estetica.

Nao entra quando o objeto nao vende nada:

- Servico profissional (advogado, contador, clinica). Construir a sala 3D dele nao acrescenta um lead.
- Site cujo objetivo declarado e captar lead rapido. O 3D atrasa o primeiro contato com a oferta.

Na duvida, o criterio e o mesmo do orcamento de efeito: **o efeito serve a conversao, nunca o contrario.**

---

## 3. O processo, na ordem obrigatoria

A ordem NAO e detalhe de gosto. O autor do estudo tentou os dois caminhos com o mesmo modelo (Opus 5): pedindo a cena inteira de uma vez o resultado saiu com bug e sem acabamento; construindo elemento por elemento saiu limpo. A diferenca foi o processo.

1. **Referencia real antes do primeiro prompt.** Prints do que se quer imitar, tipografia, paleta. Sem referencia, a IA devolve o generico dela.
2. **Um elemento por vez, via `img2threejs`.** Cada peca da cena e um pedido separado, revisado antes do proximo. O ganho nao e so qualidade: e saber onde atacar quando algo sair errado. Cena inteira num prompt so significa que "conserta a arvore" pode mexer no tronco, na folha ou nas duas.
3. **Imagem-alvo da cena montada.** Antes de juntar, gerar no GPT (ou equivalente) uma imagem do resultado final e usar como planta.
4. **Montagem.** So com todas as pecas prontas, mandar juntar conforme a imagem-alvo.
5. **So entao vira site.** HTML e CSS depois da cena existir.
6. **So entao a coreografia de rolagem.** GSAP ScrollTrigger, consultando as skills `gsap-*`.
7. **Shader e efeito de mouse por ultimo.** E acabamento, nao fundacao.

Custo real desse metodo, medido pelo autor: um dia de trabalho pra uma cena completa. Mas com a maquina trabalhando sozinha entre os pedidos.

---

## 4. Constantes de camera: a IA nao acerta enquadramento

Este e o achado mais util do estudo. Posicao de camera, elevacao e centro de foco sao a parte que a IA erra e que prompt nao conserta.

Peca explicitamente, no momento de montar a cena:

> crie constantes nomeadas no codigo para posicao, elevacao e alvo da camera, para que eu ajuste na mao

Depois disso o ajuste fino e edicao de numero no arquivo, com resultado imediato na tela. Sem isso, cada correcao de enquadramento vira uma rodada de prompt com resultado imprevisivel.

---

## 5. Peso: o numero que justifica o metodo

Geometria escrita em codigo modela so o que o usuario ve (superficie oca, sem interior). O exemplo do estudo fechou a cena completa em **7.000 triangulos e 200 KB**, menos que uma foto de hero mal exportada.

Se a cena passar disso por larga margem, o problema e escopo, nao ferramenta: tem elemento na cena que ninguem olha.

---

## 6. Guardas que continuam valendo

Nada aqui revoga as regras da skill. Em cena 3D elas apertam:

- **Fallback obrigatorio.** Mobile e `prefers-reduced-motion` recebem imagem estatica da cena, nunca a pagina morta nem o canvas travando o aparelho.
- **Texto nunca dentro da cena.** Titulo, servico e CTA sao HTML real sobreposto.
- **Licenca de fonte.** Tipografia copiada da referencia pode ser de uso pessoal. Conferir a licenca ANTES de entrar em site de cliente: uso comercial indevido gera processo pro cliente, nao pra gente.
- **Portao de saida.** Vale o checklist da Parte 7 do `anatomia_prompt_cinematografico.md`: rodar em localhost e conferir em navegador real antes de dizer que esta pronto.

---

## 7. Limites declarados da `img2threejs`

A propria skill avisa, e o playbook registra pra ninguem prometer o que ela nao faz:

- Uma imagem nao revela geometria escondida. O que esta atras do objeto e reconstrucao plausivel, nao copia.
- Personagem sai estilizado, nao fotorrealista.
- Ela reporta quando a fidelidade pedida nao e alcancavel com a imagem dada. Reporte isso ao fundador em vez de insistir em rodada nova.
