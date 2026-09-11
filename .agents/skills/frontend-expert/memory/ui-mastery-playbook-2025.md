# 🎨 2025 UI/UX Mastery Playbook

Este documento atua como a bíblia de estilização *Premium* da skill `stitch-frontend-system`. Toda interface gerada deve respeitar estes princípios rigorosos de design baseados nas tendências de 2025.

## 1. Neumorphism 2.0 & Premium Glassmorphism
- **Profundidade sem sujeira:** Evite sombras muito duras ou escuras. O Neumorphism 2.0 foca em relevos sutis.
- **Vidro Fosco (Glassmorphism):** Utilize proporções exatas para visuais sofisticados:
  ```css
  background: rgba(255, 255, 255, 0.05); /* Ou dark rgba(0,0,0,0.3) */
  backdrop-filter: blur(12px) saturate(1.2);
  -webkit-backdrop-filter: blur(12px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  ```
- **Hierarquia Visual:** Use o glassmorphism apenas em cards, modais e containers de destaque, nunca no background base.

## 2. Spatial Design & Minimalismo Dinâmico
- O minimalismo em 2025 não é mais "tudo chapado" (flat). Trata-se de **claridade espacial**.
- Use o eixo Z. Camadas com níveis diferentes de `blur` devem se sobrepor para criar uma paralaxe de UI.
- Deixe os elementos "respirarem" (muito `padding`, `gap`, e margens generosas).

## 3. Dark Mode Nativo e Complexo
- **Fundo Sofisticado:** Nunca use preto absoluto (`#000000`). Utilize tons como `#0d0d0d`, `#11181c` ou nuances azuladas muito escuras.
- **Gradientes Acentuados:** Fundos podem ter `radial-gradient` sutis invisíveis que revelam cantos da tela em roxo ou rosa muito suave para dar vida.

## 4. Microinterações Tangíveis
- Adicione `transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);` em absolutamente todos os botões e links.
- Em estados de `:hover` ou `:active`, o elemento deve se transformar (por exemplo, `transform: translateY(-2px) scale(1.02);`) ou aumentar o "brilho" da borda translúcida.
  
## 5. UI Focada em Biografia (Link-in-Bio)
- O nome e foto do perfil precisam saltar na tela. Se o fundo da página for agitado ou tiver muitas imagens brutas, adicione um **Backdrop Container** forte atrás dos textos do perfil de forma que os textos (`h1`, `p`) fiquem perfeitamente legíveis. Use sombras nos textos (`text-shadow`) para ancorá-los caso não haja containter, mas prefira um box-shadow + glassmorphism.

## 6. Arquitetura Below-The-Fold & Scroll Responsivo (Lição Aprendida)
- **Evite o Trava-Tela:** Quando projetar layouts híbridos (fundo fixo com conteúdo longo que desliza por cima), JAMAIS use `overflow: hidden;` na tag `body`. Isso destrói o touch-scroll nativo no iOS e Instagram. Use estritamente `overflow-x: hidden;` acompanhado de contêineres com `min-height: 100dvh`.
- **Cache-Busting Agressivo:** Navegadores in-app de redes sociais ignoram `no-cache` comum. Ao atualizar UX de Vitrines, você DEVE alterar a string de *query parameter* (`?v=...`) na importação do `.css` e `.js` de todos os `.html` importando as bibliotecas, garantindo atualização em tempo real na tela do usuário final.

## 7. Engenharia de Referências (21st.dev)
- **Fonte Primária de Inspiração:** Acesse sempre `https://21st.dev/community/components` para analisar estruturalmente os componentes mais modernos feitos pela comunidade.
- **Implementação Premium:** Utilize os códigos (sejam eles React, Tailwind, Framer Motion ou animações CSS modernas) para construir a melhor interface possível. Você não está mais restrito a converter tudo para Vanilla CSS ou Glassmorphism; sua missão primária é garantir que o resultado final do projeto do usuário seja o mais deslumbrante e sofisticado possível, utilizando as melhores ferramentas e tecnologias disponíveis no momento.
