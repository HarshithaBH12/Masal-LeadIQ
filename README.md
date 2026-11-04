# Masal LeadIQ

**AI-powered real-estate lead intelligence for sales teams.**

Masal LeadIQ helps a salesperson move from a raw enquiry to a practical next step. It captures inbound leads, asks Gemini to assess buying readiness, ranks leads as Hot/Warm/Cold, and prepares a customer-specific call plan.

## What it does

### Required assignment features
- **Lead intake:** customer name, location, property requirement, budget, buying timeline and free-text customer message.
- **AI analysis:** concise lead summary, customer intent, key requirements, objections/concerns, recommended next action and suggested customer response.
- **Lead-specific conversation:** ask follow-up questions about one saved lead. The assistant receives that lead's saved details and analysis as context.
- **Multiple leads and prioritization:** save multiple leads, view them in a priority queue, and sort by AI priority and score.
- **Scan-friendly UI:** score, priority, summary and next action are surfaced in the workspace.

### Added feature: Smart Call Companion
Each AI assessment includes a call preparation brief:
- A suggested opening angle.
- Three customer-specific talking points.
- Responses to likely objections.
- A realistic desired call outcome.
- A suggested follow-up timeframe.

This feature is intended to help the salesperson prepare for the conversation, not replace their judgement or make commitments on behalf of the business.

## Architecture overview

```text
Streamlit UI (app.py)
   |
   +-- Lead intake / lead workspace / chat
   |
   +-- lead_manager.py ---- JSON file storage (data/leads.json)
   |
   +-- ai_engine.py ------- Google Gen AI SDK
                              |
                              +-- Gemini analysis (structured JSON)
                              +-- Lead-contextual follow-up chat
```

### AI model and how it is called

- **Provider:** Google Gemini API
- **HTTP client:** `requests` sends HTTPS requests directly to the Gemini REST API.
- **Model configured:** `gemini-2.5-flash`
- **Analysis call:** an HTTPS `POST` to Gemini's `generateContent` endpoint with JSON response mode and a response schema. The schema makes the lead assessment predictable for the UI.
- **Conversation call:** another `generateContent` request with the selected lead's original details, AI assessment and recent chat history in the prompt.

The AI is a real runtime dependency. The app does not fabricate analysis if the API is unavailable; it shows an actionable error and keeps the lead saved so the salesperson can retry.

## Run locally

### 1. Requirements
- Python 3.10 or later (Python 3.11/3.12 recommended)
- A Google Gemini API key

### 2. Open the folder in VS Code

Open a terminal in the project folder.

### 3. Create and activate a virtual environment

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Add your API key

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the placeholder:

```toml
GEMINI_API_KEY = "your-real-key"
```

You can create a Gemini API key in Google AI Studio: https://aistudio.google.com/apikey

Never commit `secrets.toml` or expose your API key in screenshots, source code or a public repository. The file is ignored by Git.

Alternatively, set the `GEMINI_API_KEY` environment variable.

### 6. Start the app
```bash
streamlit run app.py
```

The app will open in your browser, usually at `http://localhost:8501`.

## Try the workflow

1. Open **Add a lead** and enter all required fields.
2. Submit the form. The app saves the lead and calls Gemini for analysis.
3. Open **Lead workspace** to review the score, priority, summary and recommended next action.
4. Open **Smart Call Companion** to prepare for the call.
5. Use **Ask about this lead** to ask a contextual follow-up question.
6. Add more leads. The overview sorts analyzed Hot leads before Warm and Cold leads.
7. On the dashboard, **Load sample enquiries** adds synthetic leads that you can analyze individually. Sample analysis is not prewritten; Gemini generates it live.

## Deploy on Streamlit Community Cloud

1. Create a **public** GitHub repository and push this project.
2. Visit https://share.streamlit.io/ and choose **Create app**.
3. Select your repository, branch (`main`) and entrypoint file (`app.py`).
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```
5. Deploy. Share the resulting `https://....streamlit.app` URL.

The repository includes `requirements.txt` and `.streamlit/config.toml`, which Community Cloud uses for dependencies and app configuration.

## Key technical decisions

- **Streamlit:** fast to build, simple to demo and suitable for a compact internal sales tool.
- **Gemini structured output:** reduces fragile free-form parsing for the core analysis.
- **Separate AI and storage modules:** keeps model calls, data persistence and UI concerns easier to explain and maintain.
- **JSON storage:** avoids database setup and meets the assignment's in-memory-or-database allowance. It is suitable for a small prototype, not concurrent production use.
- **Lead score + label:** provides a quick queue signal while the rationale and confidence remain visible for human review.
- **Contextual chat:** includes the selected lead's facts and AI analysis in each follow-up request rather than using a generic assistant prompt.

## Known limitations

- The JSON file is local prototype storage. Streamlit Community Cloud's local filesystem should not be treated as durable production storage; data can be lost when the app restarts or is redeployed. For production, replace this with a managed database such as Supabase/Postgres or Firestore.
- This prototype has no authentication, role-based permissions, audit log or multi-user isolation. Do not enter real customer personal data until appropriate access controls and privacy safeguards are added.
- The app uses one configured Gemini model. Model availability, quotas, pricing and free-tier limits depend on Google's current terms and region.
- AI-generated scores and call suggestions can be wrong. Salespeople must verify customer details, property availability, pricing, legal information and all commitments.
- The score is a prioritization aid, not a prediction of sale or a judgement about a person.
- Chat history is held in the Streamlit session and is not persisted across sessions.

## AI usage disclosure

Update this section before submission so it accurately reflects your work. Example:

- **ChatGPT:** helped interpret the assignment, plan the feature set and architecture, scaffold the initial application, and explain/debug implementation decisions.
- **Grok:** performs live lead analysis, structured scoring, call preparation and lead-contextual follow-up responses at runtime.
- **VS Code:** used to run, inspect and test the project.
- **GitHub / Streamlit Community Cloud:** used for source hosting and deployment.

Only list tools you actually used. Be prepared to explain the prompts, data flow, JSON schema, storage trade-offs, API-key handling and limitations.


