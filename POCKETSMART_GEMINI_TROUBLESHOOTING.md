# PocketSmart AI — Gemini troubleshooting fix

The original implementation intentionally converted every Gemini exception into a local fallback result. That made configuration/API/model errors look like a missing API key.

This version changes that behavior:

- No `GEMINI_API_KEY` -> local fallback is allowed.
- `GEMINI_API_KEY` is present -> actual Gemini errors are raised and returned to the frontend as HTTP 502 with the real error message.
- Set `GEMINI_FALLBACK_ON_ERROR=true` only when you deliberately want silent local fallback after a Gemini failure.
- `python scripts/diagnose_gemini.py` verifies `.env`, model, SDK and performs a real text request.

## Windows commands

From `D:\scratch\PocketSmartAI`:

```powershell
.venv\Scripts\activate
python -m pip install -U google-genai python-dotenv
python -c "from app.config import settings; print('GEMINI_API_KEY loaded:', bool(settings.gemini_api_key)); print('GEMINI_MODEL:', settings.gemini_model)"
python scripts\diagnose_gemini.py
```

Expected configuration output is similar to:

```text
.env exists  : True
API key      : abcde...1234
Model        : gemini-3.8-flash
```

Then:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/health
```

You want:

```json
{
  "gemini_configured": true,
  "model": "gemini-3.8-flash"
}
```

## Important model setting

Do not put the old documentation value `gemini-1.5-flash-pro` in `.env`. Gemini 1.5 models were shut down by Google in September 2025. Use a currently available model such as:

```env
GEMINI_MODEL=gemini-3.8-flash
```

## If the diagnostic script fails

The script prints the exact class and API error instead of hiding it. Typical categories are:

- `.env exists: False` or `API key: NOT SET` -> `.env` location/name problem.
- `google-genai is not installed` -> wrong virtual environment or package not installed.
- `401/403` -> API key/project/access problem.
- `404` or model-not-found -> wrong/retired model name.
- `429` -> quota/rate-limit issue.
- network/timeout error -> local network, proxy or firewall problem.

Never paste the full API key into chat or screenshots.
