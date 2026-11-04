# Masal LeadIQ

**AI-powered real-estate lead intelligence and sales prioritization platform.**

Masal LeadIQ helps real-estate sales teams turn customer enquiries into actionable sales opportunities. It captures incoming leads, uses AI to evaluate buying readiness, categorizes leads as Hot, Warm or Cold, and generates personalized recommendations to help salespeople decide what to do next.

## What It Does

### Core Features

- **Lead Intake:** Captures customer name, preferred location, property requirement, budget, buying timeline and customer message.
- **AI-Powered Lead Analysis:** Generates a concise lead summary, customer intent, key requirements, objections, recommended next action and suggested customer response.
- **Intelligent Lead Prioritization:** Assigns a score out of 100 and categorizes leads as Hot, Warm or Cold based on buying readiness.
- **Lead-Specific AI Conversation:** Allows salespeople to ask follow-up questions using the selected lead's details and AI assessment as context.
- **Multiple Lead Management:** Saves and organizes multiple enquiries in a priority-based dashboard.
- **Scan-Friendly Dashboard:** Displays lead scores, priority levels, summaries and recommended actions for quick decision-making.

### Additional Feature: Smart Call Companion

Masal LeadIQ includes a Smart Call Companion that helps salespeople prepare before contacting a customer.

It generates:
- A personalized opening angle for the conversation.
- Three customer-specific talking points.
- Suggested responses to potential objections.
- A realistic desired call outcome.
- A recommended follow-up action.

The feature supports salespeople in preparing for customer conversations without making commitments on behalf of the business.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend and UI | Streamlit |
| Programming Language | Python |
| AI Provider | Groq API |
| AI Model | openai/gpt-oss-20b |
| API Communication | Python Requests |
| Data Storage | JSON |
| Development Environment | Visual Studio Code |
| Version Control | Git and GitHub |
| Deployment | Streamlit Community Cloud |

## Architecture Overview

```text
                 Masal LeadIQ
                      |
                Streamlit UI
                   app.py
                      |
          +-----------+-----------+
          |                       |
      Lead Manager             AI Engine
    lead_manager.py           ai_engine.py
          |                       |
     JSON Storage              Groq API
    data/leads.json                |
                            GPT-OSS-20B
                                  |
                    +-------------+-------------+
                    |             |             |
               Lead Analysis   AI Chat     Call Companion
                    |             |             |
                    +-------------+-------------+
                                  |
                          AI Recommendations
```

### AI Integration

- **Provider:** Groq API.
- **Model:** `openai/gpt-oss-20b`.
- **API Endpoint:** Groq's OpenAI-compatible Chat Completions endpoint.
- **HTTP Client:** Python Requests.
- **Authentication:** API key stored securely using Streamlit secrets.

The application sends customer enquiry details to the Groq API and receives AI-generated assessments.

The lead analysis uses JSON response mode to maintain a consistent structure for displaying scores, priorities, recommendations and call preparation details.

The conversational assistant receives the selected lead's information, previous AI assessment and recent conversation history to generate relevant follow-up responses.

The application does not generate fabricated AI analysis when the API is unavailable. It displays an error while retaining the saved lead for another attempt.

## Project Structure

```text
Masal-LeadIQ/
│
├── app.py
├── ai_engine.py
├── lead_manager.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── data/
│   └── .gitkeep
│
└── tests/
    └── test_lead_manager.py
```

## Run Locally

### Prerequisites

- Python 3.10 or later.
- Git.
- A Groq API key.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Masal-LeadIQ.git
cd Masal-LeadIQ
```

### 2. Create a Virtual Environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API Key

Create a file named `.streamlit/secrets.toml` and add:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
```

Generate an API key through the [Groq Console](https://console.groq.com/keys).

Never commit your actual API key to GitHub or share it publicly.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

## How to Use Masal LeadIQ

1. Open the dashboard and add a new customer enquiry.
2. Enter the customer's details and requirements.
3. Submit the enquiry to save the lead and trigger live AI analysis.
4. Review the lead summary, buying intent, score and priority.
5. Open Smart Call Companion to prepare for the customer conversation.
6. Use Ask About This Lead to ask contextual follow-up questions.
7. Add more leads and compare their priorities in the dashboard.

The application also provides sample enquiries for testing the workflow.

## Deployment

Masal LeadIQ can be deployed using Streamlit Community Cloud.

1. Push the project to a public GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in using GitHub.
4. Select **Create app**.
5. Choose the Masal-LeadIQ repository.
6. Select the `main` branch.
7. Set the main file path to `app.py`.
8. Open Advanced Settings and add the following secret:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
```

9. Click Deploy.

Once deployment is complete, Streamlit provides a public application URL that can be shared.

## Key Technical Decisions

- **Streamlit:** Used to build an interactive dashboard quickly without requiring a separate frontend framework.
- **Groq API:** Provides access to an AI model for real-time lead analysis and conversational assistance.
- **GPT-OSS-20B:** Used to generate structured lead assessments and contextual sales recommendations.
- **JSON Response Mode:** Helps maintain consistent AI output for the application's analysis workflow.
- **Modular Architecture:** Separates user interface, AI processing, prompts and lead management.
- **JSON Storage:** Keeps the prototype simple without requiring a separate database setup.
- **Lead Scoring:** Helps sales teams prioritize enquiries based on buying readiness rather than relying only on enquiry order.

## Limitations and Future Improvements

- **Storage:** JSON-based storage is suitable for a prototype. A managed database such as PostgreSQL or Supabase would be more suitable for production.
- **Authentication:** User authentication, role-based access and multi-user permissions can be added in future versions.
- **AI Reliability:** AI-generated scores and recommendations may require human verification.
- **Data Persistence:** The application's local JSON storage should not be treated as durable storage on cloud hosting. A persistent database is recommended for production.
- **Chat History:** Conversations are maintained within the Streamlit session and are not permanently stored.
- **Scalability:** Further improvements could include automated lead assignment, CRM integration, analytics and sales performance tracking.

## AI Usage Disclosure

- **ChatGPT:** Assisted with project planning, architecture, initial code scaffolding, debugging and implementation guidance.
- **Groq API:** Used at runtime for AI-powered lead analysis, lead scoring, Smart Call Companion and contextual follow-up conversations.
- **GPT-OSS-20B:** The model used for generating AI responses through the Groq API.
- **Visual Studio Code:** Used for development, code editing and testing.
- **GitHub:** Used for source-code management and version control.
- **Streamlit Community Cloud:** Used for application deployment.

The AI-generated results are intended to assist sales teams and should be reviewed by a human before taking business decisions.

---

**Masal LeadIQ — From customer enquiry to the next best action.**
