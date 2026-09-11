# PushinPay API: Reference Guide
# Source: https://app.theneo.io/pushinpay/pix
# Last updated: 2026-04-12
# Environment: Production (Brasília UTC-3)

---

## Overview

PushinPay é um processador de pagamentos PIX brasileiro. A API permite:
- Criar cobranças PIX (QR Code dinâmico)
- Consultar status de transações
- Receber notificações via webhook
- Realizar saques PIX
- Criar PIX recorrentes
- Emitir boletos
- Realizar reembolsos
- Configurar split de receita entre contas

**Base URL (Production):** `https://api.pushinpay.com.br/api/pix/cashIn`
**Base URL (Sandbox):** Solicitar via suporte após cadastro em produção

---

## Authentication

Todas as requisições devem conter o header:
```
Authorization: Bearer {PUSHINPAY_TOKEN}
Content-Type: application/json
```

**⚠️ NUNCA expor o token no frontend.** Sempre usar via variável de ambiente server-side (ex: Vercel Serverless Function).

---

## 1. Criar PIX (POST /api/pix/cashIn)

**Endpoint:** `POST https://api.pushinpay.com.br/api/pix/cashIn`

### Pontos de atenção críticos:
- Conta deve estar CRIADA e APROVADA em https://app.pushinpay.com.br/register
- Valores SEMPRE em CENTAVOS (integer)
- Valor mínimo: 50 centavos (R$0,50)
- Percentual máximo de split: 50% por conta
- Verificar limite máximo configurado na conta antes de criar transações altas
- Se não tiver servidor para webhooks, NÃO preencher `webhook_url`

### Request Body:
```json
{
  "value": 3500,
  "webhook_url": "https://seu-dominio.com/api/webhook-pix",
  "split_rules": [
    { "value": 1000, "account_id": "9C3XXXXX3A043" }
  ]
}
```

### Campos do Body:
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `value` | integer | ✅ | Valor em centavos. Mínimo: 50 |
| `webhook_url` | string | ❌ | URL HTTPS para receber notificações |
| `split_rules` | array | ❌ | Regras de split: `[{ "value": 50, "account_id": "ID" }]` |

### Response (200 OK):
```json
{
  "id": "9c29870c-9f69-4bb6-90d3-2dce9453bb45",
  "qr_code": "00020101021226770014BR.GOV.BCB.PIX2555api...",
  "status": "created",
  "value": 3500,
  "webhook_url": "https://seu-dominio.com/api/webhook-pix",
  "qr_code_base64": "data:image/png;base64,iVBORw0KGgoAA.....",
  "webhook": null,
  "split_rules": [],
  "end_to_end_id": null,
  "payer_name": null,
  "payer_national_registration": null
}
```

### Campos da Response:
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | string | UUID da transação. **SALVAR para consultas futuras** |
| `qr_code` | string | Código PIX EMV para cópia manual ("Copia e Cola") |
| `status` | string | `created` \| `paid` \| `expired` |
| `value` | integer | Valor em centavos |
| `webhook_url` | string | URL configurada para notificações |
| `qr_code_base64` | string | Imagem QR Code em base64. Usar em `<img src="...">` |
| `webhook` | string/null | Retorno do processamento interno da notificação |
| `split_rules` | array | Regras de split configuradas |
| `end_to_end_id` | string/null | ID Banco Central (preenchido APÓS pagamento) |
| `payer_name` | string/null | Nome do pagador (preenchido APÓS pagamento) |
| `payer_national_registration` | string/null | CPF/CNPJ do pagador (preenchido APÓS pagamento) |

---

## 2. Consultar PIX (GET /api/pix/cashIn/{id})

**Endpoint:** `GET https://api.pushinpay.com.br/api/pix/cashIn/{id}`

### Pontos de atenção críticos:
- ⚠️ **Limite de polling: 1 consulta por minuto.** Consultas acima disso podem bloquear a conta.
- Usar APENAS quando o cliente identificar que pagou (clicou em "Já paguei")
- **Preferir webhooks** para detecção automática de pagamento

### Response: Igual ao de Criar PIX (ver acima)

### Status possíveis:
- `created` → PIX gerado, aguardando pagamento
- `paid` → Pago com sucesso
- `expired` → Expirado (padrão Banco Central: 30 minutos)

---

## 3. Webhook de Retorno (Recebimento)

Quando `webhook_url` é configurado na criação, a PushinPay envia POST para esta URL quando o status muda.

### Payload recebido (POST):
```json
{
  "id": "9c29870c-9f69-4bb6-90d3-2dce9453bb45",
  "status": "paid",
  "value": 3500,
  "end_to_end_id": "E00038166202504120000...",
  "payer_name": "João Silva",
  "payer_national_registration": "123.456.789-00",
  "qr_code": "00020101...",
  "split_rules": [],
  "webhook_url": "https://seu-dominio.com/api/webhook-pix"
}
```

### Comportamento da PushinPay:
- Tentativas: 3x em caso de falha no webhook
- Após 3 falhas: reenvio manual disponível no painel administrativo
- Header customizado opcional: configurável no painel (enviado em todos os webhooks)

### Handler mínimo obrigatório (Vercel):
```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  
  const { id, status, value, payer_name, payer_national_registration } = req.body;
  
  // Responder 200 IMEDIATAMENTE (antes de qualquer processamento lento)
  res.status(200).json({ received: true });
  
  // Processar assincronamente
  if (status === 'paid') {
    // 1. Logar no Supabase
    // 2. Liberar acesso ao entregável (bot Telegram, download, etc.)
  }
}
```

---

## 4. Saque PIX (POST /api/pix/cashOut)

**Endpoint:** `POST https://api.pushinpay.com.br/api/pix/cashOut`

Para sacar fundos da conta PushinPay para uma chave PIX externa.

---

## 5. PIX Recorrente

### Criar PIX Recorrente
**Endpoint:** `POST https://api.pushinpay.com.br/api/pix/recorrente`

Permite cobranças periódicas automatizadas (assinatura).

### Cancelar PIX Recorrente
**Endpoint:** `DELETE https://api.pushinpay.com.br/api/pix/recorrente/{id}`

### Buscar PIX Recorrente
**Endpoint:** `GET https://api.pushinpay.com.br/api/pix/recorrente/{id}`

---

## 6. Split Rules: Guia Completo

Split divide o valor da transação entre múltiplas contas PushinPay.

### Formato:
```json
"split_rules": [
  { "value": 5000, "account_id": "CONTA_PRODUTOR" },
  { "value": 2000, "account_id": "CONTA_AFILIADO" }
]
```

### Regras e Validações:
| Regra | Detalhe |
|---|---|
| Máximo por conta | 50% do valor total |
| Soma máxima | splits + taxa ≤ valor total da transação |
| `account_id` inválido | Erro: conta não encontrada |
| Valores em centavos | Sempre integer |

### Erros comuns de split:
- `"Valor da transação não pode ser menor que o valor do split"` → split > total
- `"A soma dos splits não pode exceder o valor da transação"` → soma splits + taxa > total
- `"Conta de split não encontrada"` → account_id inválido
- `"Splits do token inválidos"` → inconsistência no token de split

---

## 7. Reembolso

**Endpoint:** `POST https://api.pushinpay.com.br/api/reembolso`

Para reverter uma transação paga.

---

## 8. Dados da Conta

**Endpoint:** `GET https://api.pushinpay.com.br/api/conta`

Retorna dados da conta, incluindo limites configurados.

---

## 9. Erros Comuns e Tratamento

| Erro | Causa | Solução |
|---|---|---|
| Valor acima do limite | Transação > limite da conta | Verificar limite no dashboard ou pedir aumento |
| Split + taxa > total | Configuração inválida | Ajustar valores dos splits |
| Conta split não encontrada | `account_id` errado | Verificar IDs no painel PushinPay |
| 401 Unauthorized | Token inválido ou expirado | Verificar `PUSHINPAY_TOKEN` na env |
| Conta não aprovada | Cadastro pendente | Completar verificação em app.pushinpay.com.br |

---

## 10. Obrigatoriedade Legal (Item 4.10 - Termos de Uso)

**⚠️ MANDATORY em todos os checkouts:**

O seguinte aviso DEVE aparecer de forma clara, destacada e acessível no checkout, antes da finalização do pagamento:

> *"A PUSHIN PAY atua exclusivamente como processadora de pagamentos e não possui qualquer responsabilidade pela entrega, suporte, conteúdo, qualidade ou cumprimento das obrigações relacionadas aos produtos ou serviços oferecidos pelo vendedor."*

**Não cumprir pode gerar penalizações e bloqueio da conta.**

Referência: https://pushinpay.com.br/termos-de-uso

---

## 11. Ambiente Sandbox

- Cadastro: Primeiro em produção (app.pushinpay.com.br/register), depois solicitar sandbox via suporte
- Finalidade: testes sem transações reais
- Base URL Sandbox: solicitada via suporte (não público)
