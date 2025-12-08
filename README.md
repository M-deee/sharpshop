# SharpShop — Inventory Management Agent

A small CLI demo agent that helps sellers manage inventory (create, query, update, list) using a LangGraph-style conversational flow and an OpenRouter/OpenAI-compatible client.

## What this project is

This repository contains a lightweight conversational agent that:
- Accepts seller messages via a simple CLI (`main.py`).
- Uses an LLM (via OpenRouter/OpenAI-compatible client) to parse intent and extract structured actions.
- Executes mock inventory operations (create_product, query_inventory, update_product, list_products) implemented in `tools.py`.

It is a demo/prototype — the `tools.py` functions are simple mocks you can replace with real database calls.

## Example queries and expected responses

1) Create product

User:
"I want to add a product: \"Nike Shoes\", price: 20000, category: fashion, quantity: 5, condition: new."

Assistant (example):
```
{"action": "create_product", "data": {"title": "Nike Shoes", "price": 20000, "category": "fashion", "quantity": 5, "condition": "new", "description": "", "size": "", "brand": ""}}
```
After executing the action the assistant will confirm:

Assistant (final):
"✅ Product created: Nike Shoes (ID: PROD_0001) — price: 20000 — quantity: 5"

2) Query inventory

User:
"Search for \"Nike\""

Assistant (example):
```
{"action": "query_inventory", "data": {"query": "Nike"}}
```
Result (mock):
"Found 2 items matching 'Nike':\n- Nike Shoes — 5 in stock — NGN 20000 (ID: PROD_0001)\n- Nike T-Shirt — 10 in stock — NGN 8000 (ID: PROD_0002)"

3) Update product

User:
"Update product PROD_0001 price to 22000"

Assistant (example):
```
{"action": "update_product", "data": {"product_id": "PROD_0001", "updates": {"price": 22000}}}
```
Result (mock):
"✅ Product PROD_0001 updated: price set to 22000"

4) List products

User:
"Show me all products"

Assistant (example):
```
{"action":"list_products","data":{"limit":10}}
```
Result (mock):
"Listing 3 products:\n1) Nike Shoes — 5 — NGN 20000\n2) Adidas Cap — 4 — NGN 3000\n3) Samsung Charger — 12 — NGN 4500"

Note: The agent asks one clarifying question at a time if required fields are missing.

## Local setup (step-by-step)

Prerequisites
- Python 3.8+ installed
- Git (if cloning from a repository)

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

Minimal dependencies expected (add to `requirements.txt` if missing):
```
python-dotenv
openai
langgraph
```

4. Add your API key (do NOT commit this file)

Create a `.env` file in the project root with:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Important: keep `.env` local only. Do not commit it.

5. Ensure environment variables are loaded before `config.py` is imported

`agent.py` should call `from dotenv import load_dotenv` and `load_dotenv()` before importing `config` so `OPENROUTER_API_KEY` is available at import time.

6. Run the CLI

```bash
python3 main.py
```

Type messages at the prompt. Type `image` to simulate sending an image (if supported), and `quit` to exit.

## Quick connectivity test

A small `test_api.py` can be used to validate the API key and the OpenRouter/OpenAI client. Example:

```python
# test_api.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"

if not api_key:
    print("API key not found in .env")
    exit(1)

client = OpenAI(base_url=base_url, api_key=api_key)
try:
    r = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":"hello"}], temperature=0.7)
    print("OK", r)
except Exception as e:
    print("API error:", e)
```

Run:

```bash
python3 test_api.py
```

## Git hygiene & security

If you accidentally committed `.env`:

1. Stop, revoke/rotate the exposed API key immediately.
2. Remove the file from the index (keep local copy):

```bash
git rm --cached .env
git commit -m "Remove .env from repository"
git push origin main
```

3. Add `.env` to `.gitignore` (if not already present):

```
# environment
.env
.venv/
venv/
```

4. If a secret was committed and you need to remove it from history, use BFG or `git filter-branch` (this rewrites history — coordinate with collaborators).

## Development notes

- `tools.py` currently implements mock functions. Replace with real DB calls in production.
- The agent expects assistant responses to include a JSON block with an `action` and `data` when it should execute something. See `SYSTEM_PROMPT` in `agent.py` for the exact instruction.

## Troubleshooting

- 401 errors: usually due to missing/invalid API key. Ensure `.env` is present and `load_dotenv()` runs before `config.py` imports.
- If using OpenRouter, verify the `OPENROUTER_BASE_URL` and that your key is active.

## License & attribution

This is sample/demo code — adapt and extend for your needs.

---

If you want, I can now:
- Add this `README.md` to the repo for you, or
- Walk through removing `.env` from the git history (full purge) and update `.gitignore` accordingly.
