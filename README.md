# DyadLink 伴知

DyadLink is a Streamlit research-demonstration app based on Cheng (2026), “Separating ECog scale-score information from dyad availability: observation-process contributions to dyadic prediction of cognitive impairment in ADNI.”

The app presents fixed cohort-level research results and an optional, consent-gated reflection conversation. It is not a diagnostic tool, a personal risk predictor, or a native Android/iOS/Windows application; it runs in a web browser.

## Features

- Conversation-first interface with voice transcription and editable transcript review.
- A full-screen data-processing consent gate before entering the app. Declining stops the session; consent can be withdrawn from the sidebar.
- A separate research dashboard with the paper's fixed C-index results.
- A local scripted demonstration mode when DeepSeek is not configured.
- Responsive layouts and larger controls for mobile and older-adult accessibility.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Voice recording requires browser microphone permission and HTTPS outside localhost.

## Configure DeepSeek

Set `DEEPSEEK_API_KEY` as a server-side environment variable or deployment secret. For local testing, a `.streamlit/secrets.toml` file may contain:

```toml
DEEPSEEK_API_KEY = "your-key-here"
```

Never commit a real API key. The local secrets file is ignored by Git and is plaintext, not encrypted. Public deployments should use the hosting platform's Secrets manager.

## Research reference

Cheng, W. W. (2026). *Separating ECog scale-score information from dyad availability: observation-process contributions to dyadic prediction of cognitive impairment in ADNI*. Research Square, Version 3. https://doi.org/10.21203/rs.3.rs-10884877/v3

The displayed research metrics are fixed published results, not estimates computed from a visitor's inputs.
