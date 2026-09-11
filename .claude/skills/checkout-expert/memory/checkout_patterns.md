# Checkout Patterns: Dodo Ecosystem
# Padrões aprovados de checkout usados nos projetos do ecossistema Dodo

---

## Padrão 1: Checkout estilo plataforma de assinatura (Modal com PIX)

**Usado em:** vitrines e projetos de link-in-bio com venda direta

### Fluxo completo:
```
[Botão CTA na página] 
  → [Modal de checkout abre]
    → [Serverless function cria PIX via PushinPay]
      → [QR Code + Copia e Cola exibidos]
        → [Countdown 30 minutos]
          → [Polling ou webhook confirma pagamento]
            → [Redirect para entregável]
```

### Componentes obrigatórios do modal:
1. **Header:** Nome do produto + preço formatado (R$ XX,XX)
2. **QR Code:** `<img>` com `qr_code_base64`
3. **Copia e Cola:** Input somente leitura + botão "Copiar Código"
4. **Timer:** Contador regressivo de 30 minutos (expira junto com o PIX)
5. **Botão "Já Paguei":** Trigger para polling manual
6. **Disclaimer PushinPay:** Texto obrigatório (Item 4.10)
7. **Loading state:** Spinner enquanto aguarda criação do PIX

### CSS Pattern (glassmorphism dark):
```css
.checkout-modal {
  background: rgba(15, 15, 20, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
}
```

---

## Padrão 2: Redirect Checkout (Página Dedicada)

**Usado em:** Fluxos de funil com upsell/downsell

### Fluxo:
```
[CTA] → [Nova página /checkout?offer=X] → [PIX gerado] → [Confirmação] → [Thank you page]
```

---

## Padrão 3: Checkout com Order Bump

Adicionar produto complementar antes do pagamento:
- Checkbox "Adicionar [Produto] por +R$XX"
- Se marcado: aumentar `value` na chamada da API
- Split rules ajustados proporcionalmente

---

## Padrão 4: Checkout Multilíngue (PT/EN)

**Usado em:** vitrines de perfil bilingue

- Textos do checkout em objeto JS separado
- Detectar idioma atual via `data-lang` no `<html>`
- Disclaimers em PT obrigatórios independente do idioma (PushinPay é BR)

---

## Padrão 5: Gatekeeper Post-Payment Verification

**Usado em:** Checkout de alto valor, grupos VIP, entregáveis digitais sensíveis.

### Problema:
Vazamento de link de acesso. Usuários mal-intencionados podem tentar acessar `/obrigado.html` diretamente via URL ou compartilhar o link sem pagar.

### Solução (O Gatekeeper):
Toda página de obrigado deve carregar inicialmente com um **Overlay de Segurança** e realizar uma verificação via API antes de mostrar o conteúdo.

1. **Overlay Inicial:** O CSS deve cobrir 100% da página com um loading (ex: "Verificando Acesso...").
2. **API Backend (`/api/verify-access`):**
   - Recebe o ID da transação via query param.
   - Consulta o Supabase: `status` deve ser `paid`.
   - Retorna `{ authorized: true/false }`.
3. **Lógica Frontend:**
   - Se `authorized == true`: Remove o overlay com fade-out.
   - Se `authorized == false`: Exibe erro ("Acesso Negado") e redireciona para a vitrine/checkout após 3 segundos.

---

## Regras de UX de Conversão

1. **Nunca redirect antes do pagamento** → mantém usuário no contexto
2. **Timer visível sempre** → urgência real (é o tempo real do PIX)
3. **Copia e cola > QR Code** → maioria paga via app mobile com copia e cola
4. **Loading state obrigatório** → 2-3 segundos para criar PIX, não deixar usuário no vácuo
5. **Mensagem de sucesso clara** → "Pagamento confirmado! Acesse agora:" + link
6. **Fallback de expiração** → ao expirar, oferecer gerar novo PIX sem sair do modal

---

## Entregáveis por produto (Dodo.exe)

| Produto | Entregável | Método de liberação |
|---|---|---|
| Acesso VIP Telegram | Link do grupo/canal privado | Bot Telegram via API |
| Produto digital | Link de download | URL direta pós-confirmação webhook |
| Mentoria/Consulta | Calendly ou WhatsApp | Redirect URL |

---

## Supabase: Schema de Transações

Tabela: `transactions`
```sql
CREATE TABLE transactions (
  id UUID PRIMARY KEY, -- ID da PushinPay
  status TEXT, -- created | paid | expired
  value INTEGER, -- em centavos
  payer_name TEXT,
  payer_doc TEXT, -- CPF/CNPJ
  product TEXT, -- identificador do produto
  offer TEXT, -- variante da oferta (main, bump, upsell)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  paid_at TIMESTAMPTZ,
  webhook_received_at TIMESTAMPTZ,
  end_to_end_id TEXT,
  metadata JSONB -- dados extras (UTMs, source, etc.)
);
```
