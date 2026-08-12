# Welles web (Vercel) + Colab or Modal GPU

```
Browser → Vercel (web/) → WELLES_API_URL → Colab (or Modal) → n0social/welles
```

HF Gradio **Spaces with GPU need a paid plan**. Use **Colab** (free T4, tab must stay open) or **Modal**.

## Personal demo flow (recommended)

1. Start Colab (`notebooks/welles_serve.ipynb`, T4) → copy ngrok URL  
2. Open the Vercel site → paste URL into **Colab API URL** (saved in your browser)  
3. Write / Rewrite / Continue  

No need to change Vercel env vars each session. Keep the Colab tab open.


## Option B — Modal (stays up without a browser tab)

```bash
pip install modal
modal setup
modal deploy space/modal_app.py
```

Set `WELLES_API_URL` to the Modal HTTPS endpoint.

## Vercel

1. Push repo to GitHub  
2. Import in Vercel → Root Directory: `web`  
3. Env: `WELLES_API_URL=<Colab ngrok or Modal URL>`  
4. Deploy  

## Local web (needs Node)

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```
