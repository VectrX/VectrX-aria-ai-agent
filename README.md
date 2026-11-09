# VectrX — Aria AI Agent

Aria is the local-first AI operations assistant for VectrX and Red Velvet. This is a **starter**, not an autonomous production agent.

## Requirements
- Python 3.11+
- OpenAI API key with API access and billing
- A long randomly generated local admin token

## Run locally (Windows PowerShell)

```powershell
git clone https://github.com/VectrX/VectrX-aria-ai-agent.git
cd VectrX-aria-ai-agent
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:ARIA_ADMIN_TOKEN="YOUR_LONG_RANDOM_SECRET"
python -m unittest discover -v
python aria.py
```

Use `http://127.0.0.1:4312/health` to check service health. Chat requests must be POSTed to `http://127.0.0.1:4312/api/chat` with an `Authorization: Bearer YOUR_LONG_RANDOM_SECRET` header and JSON `{"message":"Hello Aria"}`.

**Security:** Never put API keys or admin tokens in frontend JavaScript, GitHub, URLs, screenshots, or chat messages. The dashboard must access Aria through an authenticated backend proxy. The default server binds only to 127.0.0.1. This starter has no persistent storage, customer accounts, production rate limiting, payment processing, Red Velvet connection or autonomous task executor.

## Test

```powershell
python -m unittest discover -v
```

GitHub Actions also runs these tests on push. The automated tests mock the AI service and **do not prove real API billing or chat delivery**.

## Next integration
Connect the existing VectrX dashboard backend to Aria's local API without exposing secrets in the browser. Add persistent task state, approval-gated actions, structured logs, rate limiting, scheduled health checks and production deployment only after reviewing security. Do not place client conversations or personal data in the public repository.
