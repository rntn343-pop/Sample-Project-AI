# PocketSmart AI

PocketSmart AI is a complete FastAPI + Jinja2 web application for budget-aware recommendations across:

- Home interior planning
- Party planning
- Jewelry planning with optional outfit-image analysis

The implementation follows the uploaded project documentation's architecture and route inventory, while resolving its Flask/FastAPI inconsistency in favor of FastAPI because the later milestones and conclusion explicitly specify FastAPI, Jinja2, and Uvicorn.

## What is included

- FastAPI backend with modular routes/services/models
- JWT authentication plus browser session cookies
- SQLite persistence for users and recommendation history
- Gemini multimodal integration via Google's current `google-genai` SDK
- Safe deterministic fallback recommendations when no API key is configured or Gemini fails
- Search links for Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO and generic platforms
- Responsive HTML/CSS/JavaScript frontend
- Planner pages, recommendation details, history, dashboard, registration and login
- Automated tests
- Docker support

## Important model compatibility note

The source documentation names **Gemini 1.5 Flash Pro**. That model family is no longer available in the Gemini API; Google's release notes state that Gemini 1.5 models were shut down in September 2025. This project therefore defaults to `gemini-3.8-flash` and keeps the model configurable through `GEMINI_MODEL`.

Set `GEMINI_MODEL` to another model available to your account when needed. The `.env.example` file lists several current model IDs as examples. The launcher also exposes them with `python launch.py --list-models` and allows a one-time override with `python launch.py --model <MODEL_ID>`. Model availability can vary by account/project, so verify access against Google\'s current model catalog.

## Gemini troubleshooting

Run `python scripts/diagnose_gemini.py` from the activated virtual environment to verify that `.env` is being loaded, the SDK is installed, the configured model is reachable, and an actual Gemini request succeeds. When a key is configured, Gemini errors are no longer silently converted to a fallback response; the frontend reports the API error instead.

Use `GEMINI_MODEL=gemini-3.8-flash`. The Gemini 1.5 models named in the original project documentation were shut down in September 2025.

## One-click-style installer and launcher

The project includes cross-platform Python scripts so Windows, macOS, and Linux users can install and launch PocketSmart without manually activating the virtual environment.

### Install

From the project folder:

```bash
python install.py
```

The installer creates `.venv`, installs `requirements.txt`, creates/updates `.env`, and prompts for the Gemini API key. It also generates a secure `SECRET_KEY` automatically. Leave the API-key prompt blank to keep an existing key or run with the local fallback.

### Launch

```bash
python launch.py
```

The launcher uses the project virtual environment, starts Uvicorn on `http://127.0.0.1:8000`, waits for `/health`, opens the default web browser automatically, and keeps the terminal open while the server is running. Press `Ctrl+C` to stop the server.

You may change the launch host/port for a local run with:

```text
POCKETSMART_HOST=127.0.0.1
POCKETSMART_PORT=8000
```

On Windows PowerShell, for example:

```powershell
$env:POCKETSMART_PORT=8080
python launch.py
```

On macOS/Linux:

```bash
POCKETSMART_PORT=8080 python3 launch.py
```

## Quick start in VS Code

### 1. Open the folder

Open `pocketsmart_ai` in VS Code.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env`.

Set a strong `SECRET_KEY`.

For Gemini-powered responses set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The application still runs without a Gemini key by using its local fallback recommendation engine.

### 5. Run the app

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000

### 6. Test

```bash
pytest -q
```

## Main routes

Browser pages:

- `/` — landing page
- `/register` — registration
- `/login` — login
- `/logout` — logout
- `/dashboard` — logged-in dashboard
- `/home-planner` — home planner
- `/party-planner` — party planner
- `/jewelry-planner` — jewelry planner
- `/history` — recommendation history
- `/recommendations-details/{id}` — recommendation detail
- `/testimonials` — demo testimonials page

API/form routes:

- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `POST /home-budget` (alias)
- `POST /party-budget` (alias)
- `POST /jewelry-budget` (alias)
- `POST /token` — JWT token using OAuth2 password form
- `GET /session-info`
- `POST /session-data`
- `GET /recommendations-details/{id}` or `GET /recommendations-details?recommendation_id={id}`
- `GET /history`
- `GET /startup`
- `GET /health`

## Product and service links

The uploaded documentation asks for third-party platform sourcing and also explicitly allows mock/simulated sourcing. This implementation does not scrape marketplaces. Gemini returns search terms and the backend creates links on known platform domains. Prices returned by Gemini are treated as estimates, not verified live marketplace prices.

## Production notes

- Replace SQLite with PostgreSQL for multi-instance deployment.
- Set `COOKIE_SECURE=true` behind HTTPS.
- Restrict `CORS_ORIGINS` to trusted origins.
- Add a real product-search provider before presenting any price as live/verified.
- Replace the demo testimonial content before production use.


### Gemini response normalization
Gemini can occasionally return valid JSON with a compact or slightly inconsistent shape, such as a string `outfit_analysis` or JSON with a trailing comma. PocketSmart normalizes those responses locally before Pydantic validation, so useful model output is preserved instead of being rejected.

The parser also repairs common JSON formatting mistakes using only the Python standard library; there is no extra JSON-repair service or API dependency.

### Budget enforcement
Gemini output is never allowed to exceed the budget submitted by the user. PocketSmart treats the submitted budget as authoritative, recalculates all line-item totals locally, reduces quantities when necessary, and removes unaffordable items rather than fabricating cheaper prices.


### Gemini model selection during installation

The installer shows these examples at the model prompt:

```text
Latest     - gemini-3.8-flash
Additional - gemini-3.7-flash
             gemini-3.6-flash
             gemini-3.5-flash
             gemini-3.5-flash-lite
             gemini-3.1-flash-lite
             gemini-2.5-flash
             gemini-2.5-flash-lite
```

Enter any model ID supported by your Gemini API key. Leaving the prompt blank keeps the existing configured model.
