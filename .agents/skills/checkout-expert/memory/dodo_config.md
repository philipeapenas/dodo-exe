# Dodo.exe: Checkout Config Reference
# Configurações específicas do ecossistema para o checkout-expert

---

## Variáveis de Ambiente (Vercel)

```env
# PushinPay
PUSHINPAY_TOKEN=seu_token_aqui

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=sua_service_key_aqui

# Telegram Bot (para liberar acesso VIP)
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_GROUP_ID=-100xxxxxxxxxx
TELEGRAM_INVITE_LINK=https://t.me/+xxxxxxxxxxxx

# URLs de entregável por produto
REDIRECT_VIP_URL=https://t.me/+xxxxxxxxxxxx
REDIRECT_DIGITAL_URL=https://seu-dominio.com/obrigado
```

---

## Estrutura de Arquivos Vercel (padrão Dodo)

```
projeto/
├── api/
│   ├── create-pix.js        ← Criar cobrança PIX
│   ├── check-pix.js         ← Consultar status PIX
│   └── webhook-pix.js       ← Receber confirmação PushinPay
├── js/
│   ├── config.js            ← Config pública do projeto
│   └── checkout.js          ← Lógica do modal de checkout
├── index.html               ← Página principal (vitrine/bio)
└── vercel.json              ← Configuração de deploy
```

---

## Template: api/create-pix.js

```javascript
export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', process.env.ALLOWED_ORIGIN || '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { value, product, offer } = req.body;

  // Validação
  if (!value || value < 50) {
    return res.status(400).json({ error: 'Valor mínimo é R$0,50 (50 centavos)' });
  }

  try {
    const response = await fetch('https://api.pushinpay.com.br/api/pix/cashIn', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.PUSHINPAY_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        value,
        webhook_url: `${process.env.VERCEL_URL}/api/webhook-pix`
      })
    });

    if (!response.ok) {
      const error = await response.json();
      return res.status(response.status).json({ error: error.message || 'Erro na PushinPay' });
    }

    const data = await response.json();

    // Logar criação no Supabase (sem await para não atrasar response)
    logToSupabase({ ...data, product, offer }).catch(console.error);

    return res.status(200).json({
      id: data.id,
      qr_code: data.qr_code,
      qr_code_base64: data.qr_code_base64,
      value: data.value,
      status: data.status
    });

  } catch (err) {
    console.error('create-pix error:', err);
    return res.status(500).json({ error: 'Erro interno ao criar PIX' });
  }
}

async function logToSupabase(data) {
  const { createClient } = await import('@supabase/supabase-js');
  const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
  await supabase.from('transactions').insert({
    id: data.id,
    status: data.status,
    value: data.value,
    product: data.product,
    offer: data.offer
  });
}
```

---

## Template: api/webhook-pix.js

```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  // RESPONDER 200 IMEDIATAMENTE (PushinPay tem timeout curto)
  res.status(200).json({ received: true });

  const { id, status, value, payer_name, payer_national_registration, end_to_end_id } = req.body;

  try {
    const { createClient } = await import('@supabase/supabase-js');
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

    // Atualizar status no Supabase
    await supabase.from('transactions').update({
      status,
      payer_name,
      payer_doc: payer_national_registration,
      end_to_end_id,
      webhook_received_at: new Date().toISOString(),
      ...(status === 'paid' && { paid_at: new Date().toISOString() })
    }).eq('id', id);

    // Liberar acesso se pago
    if (status === 'paid') {
      // Notificar via Telegram, enviar link, etc.
      console.log(`✅ Pagamento confirmado: ${id} | ${payer_name} | R$${value / 100}`);
    }

  } catch (err) {
    console.error('webhook-pix error:', err);
  }
}
```

---

## Template: api/check-pix.js

```javascript
export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).end();

  const { id } = req.query;
  if (!id) return res.status(400).json({ error: 'ID obrigatório' });

  try {
    const response = await fetch(`https://api.pushinpay.com.br/api/pix/cashIn/${id}`, {
      headers: {
        'Authorization': `Bearer ${process.env.PUSHINPAY_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    return res.status(200).json({ status: data.status, value: data.value });

  } catch (err) {
    return res.status(500).json({ error: 'Erro ao consultar PIX' });
  }
}
```

---

## Contatos e Recursos

- PushinPay Dashboard: https://app.pushinpay.com.br
- PushinPay Register: https://app.pushinpay.com.br/register
- API Docs: https://app.theneo.io/pushinpay/pix
- Termos de Uso: https://pushinpay.com.br/termos-de-uso
- Suporte PushinPay: via painel (para liberar sandbox)
