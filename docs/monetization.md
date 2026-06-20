# Monetization — turning Mastr into a paid product

The web app already has the **shape** of a sellable product: a clean
upload→result flow and a **freemium gate** (3 free renders, then a paywall).
What's there now is a *client-side demo* gate — easy to bypass. To actually take
money and enforce limits, you add three things, in this order.

## 1. Accounts (so usage is tied to a person, not a browser)
- **Supabase Auth** (free tier) — email/password or Google sign-in.
- On sign-in, the server knows who the user is and can store their plan + usage.
- Without accounts, any limit can be bypassed by clearing the browser.

## 2. Payments (Stripe)
- **Stripe Checkout + Billing** for the subscription (e.g. £6/mo Pro).
- Flow: user clicks **Go Pro** → server creates a Checkout Session → Stripe hosts
  the payment page → on success, a **webhook** marks the user `pro` in the DB.
- The client never handles card data; Stripe does. You need: a Stripe account,
  a product/price, and the secret key **on the server only** (never in the browser).

## 3. Server-side enforcement (the real gate)
Move the limit from the browser to the API:
- Each `/api/master|mix|match` call checks the signed-in user's plan + monthly
  count **before** processing.
- Free users: N renders/month or a watermark / lower-quality export.
- Pro users: unlimited + full-quality WAV.
- Store counts in the DB; reset monthly.

```
Browser ──(signed-in)──> API ──> check plan & usage ──> process ──> increment
                                   │ over limit → 402 Payment Required → paywall
Stripe webhook ──> DB: user.plan = 'pro'
```

## Pricing (starting guess — validate later)
- **Free:** 3 masters, MP3/preview export, light watermark.
- **Pro ~£6/mo** (or ~£1/track pay-as-you-go): unlimited, WAV export, reference
  match, batch. A **pay-per-track** option converts one-off users who won't subscribe.

## Distribution (half the job)
- A real domain + landing page with **before/after audio demos**.
- SEO/content: "free online mastering", "make my song louder", tutorials.
- Post in producer communities; a free tier that's genuinely useful is the hook.

## Build order
1. Keep improving quality (this is the product).
2. Add Supabase Auth → know who the user is.
3. Add Stripe Checkout + webhook → take money.
4. Move the gate server-side → enforce free vs pro.
5. Landing page + demos → get traffic.

> Reference businesses: **LANDR**, **eMastered**, **CloudBounce** — all
> upload→master subscription services. Proof the model works.
