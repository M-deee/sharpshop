# SharpShop — Inventory Management Agent 🛍️🤖

Welcome to SharpShop — a playful CLI chatbot that helps sellers manage their inventory by talking like a human. It uses a conversational flow (LangGraph-style) and an OpenRouter/OpenAI-compatible client to turn natural messages into actions (create, query, update, list).

Why this is fun
- Quick prototyping of conversational inventory flows
- Mock tools in `tools.py` so you can swap in a real DB later
- Friendly assistant that asks one clarifying question at a time ✨

Features
- Conversational agent that extracts structured actions from messages
- Mocked inventory actions: create, query, update, list
- Simple CLI interface (`main.py`) for quick testing

Getting started — quick and safe (3 minutes)
1. Clone the repo (or use your local copy)

```bash
git clone https://github.com/<your-username>/sharpshop.git
cd sharpshop
```

2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

If `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

Suggested minimal dependencies (add to `requirements.txt` if missing):

```
python-dotenv
openai
langgraph
```

4. Add your API key (do NOT commit this file) 🔒

Create a `.env` file in the project root with:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Important: keep `.env` local only. Do not commit it — rotate the key if it ever gets pushed.

5. Make sure `agent.py` loads env variables early

`agent.py` should call `from dotenv import load_dotenv` and `load_dotenv()` before importing `config` so the API key is available at import time.

6. Run the CLI

```bash
python3 main.py
```

Type a message, for example:
`I want to add a product: "Nike Shoes", price: 20000, category: fashion, quantity: 5, condition: new.`

Example interactions (chat-style)

---

User: I want to add a product: "Nike Shoes", price: 20000, category: fashion, quantity: 5, condition: new.

Agent (parsed action):

```json
{"action": "create_product", "data": {"title": "Nike Shoes", "price": 20000, "category": "fashion", "quantity": 5, "condition": "new"}}
```

Agent (confirmation):

Agent: ✅ Product created: Nike Shoes (ID: PROD_0001) — NGN 20000 — quantity: 5

---

User: Search for "Nike"

Agent (parsed action):

```json
{"action": "query_inventory", "data": {"query": "Nike"}}
```

Agent (result):

Agent: 🔎 Found 2 items matching 'Nike':
- Nike Shoes — 5 in stock — NGN 20000 (ID: PROD_0001)
- Nike T-Shirt — 10 in stock — NGN 8000 (ID: PROD_0002)

---

User: Update product PROD_0001 price to 22000

Agent (parsed action):

```json
{"action": "update_product", "data": {"product_id": "PROD_0001", "updates": {"price": 22000}}}
```

Agent (confirmation):

Agent: ✅ Product PROD_0001 updated: price set to 22000

---

User: Show me all products

Agent (parsed action):

```json
{"action":"list_products","data":{"limit":10}}
```

Agent (result):

Agent: 📋 Listing 3 products:
1) Nike Shoes — 5 — NGN 20000
2) Adidas Cap — 4 — NGN 3000
3) Samsung Charger — 12 — NGN 4500

Notes
- The bot asks one clarifying question at a time if required fields are missing (keeps UX simple).
- `tools.py` uses mock implementations — replace these with real DB calls when ready.

Security & git hygiene 🧰

- Do NOT commit `.env`. If you accidentally pushed it, revoke the key immediately and remove the file from the repo index with:

```bash
git rm --cached .env
git commit -m "Remove .env from repository"
git push origin main
```

- Add `.env` to `.gitignore` so it won't be added again.

Troubleshooting

- 401 errors: usually due to missing/invalid API key. Make sure `.env` exists and `load_dotenv()` runs before `config.py` imports.
- If using OpenRouter, verify `OPENROUTER_BASE_URL` and key status in your OpenRouter dashboard.

Want help next? 🚀

- I can add `.env` to `.gitignore` and remove it from the index for you (safe, non-destructive).
- If you need secrets purged from commit history I can provide the commands (note: this rewrites history and requires coordinating with collaborators).

Enjoy building — and let me know if you'd like the agent to speak in a different tone (formal, playful, or extra friendly)! 🎉