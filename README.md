Since we've evolved the project from a simple translator into a **Stateful Multi-Agent System** with **Infrastructure-as-Code**, the README needs to reflect that "Enterprise" level of polish.

Here is the updated `README.md`. It now highlights the **A2A (Agent-to-Agent)** communication, the **Firestore Slang Vault**, and the **Terraform** integration.

---

# 🧢 No Cap Corporate Translator

### *A Stateful Multi-Agent Multimodal System*

Built for the **2026 Google Agent Hackathon**, this system acts as a sophisticated bridge between corporate leadership and the Gen Z workforce. It orchestrates a "squad" of specialized AI agents to generate a full multimodal experience while maintaining a persistent global knowledge base.

## 🤖 The Multi-Agent Orchestration

The system utilizes a chained agentic workflow:

1. **The Linguist (Gemini 2.5 Flash):** Performs the initial "tone-shift" from corporate jargon to Gen Z slang.
2. **The Vocab Researcher (Gemini 2.5 Flash):** **(A2A)** Receives the output from the Linguist, performs a comparative analysis against the original text, and generates a structured glossary.
3. **The Archivist (Firestore Tool):** **(Agentic Action)** Automatically syncs the discovered slang into a persistent Cloud Firestore database ("The Slang Vault").
4. **The Vocalist (Cloud TTS):** Generates high-fidelity audio using the **Neural2-H** engine with customized pitch and speed.
5. **The Visualist (Imagen 3):** Generates a contextually relevant meme to accompany the translation.
6. **The Gatekeeper (Safety Agent)**: Acts as the first line of defense, using zero-shot classification to ensure all inputs adhere to Responsible AI safety guidelines (filtering violence, weapons, and illegal content).

---

## 🛠️ Technical Stack

* **LLM Orchestration:** Vertex AI (Gemini 2.5 Flash)
* **Database:** Google Cloud Firestore (Native Mode)
* **Infrastructure:** Terraform (IaC)
* **Image Gen:** Imagen 3.0
* **Audio Gen:** Google Cloud Text-to-Speech (Neural2)
* **UI:** Streamlit

The codebase is organized into a `src` directory, with each agent in its own module for better maintainability and scalability.

---

## 🚀 Deployment Instructions

### 1. Infrastructure Setup (Terraform)

Automate the creation of the Firestore database and API enablement. Run the following commands from the `infra` directory:

```bash
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

### 2. Local Environment Setup

```bash
# Install dependencies
rm -rf .venv
uv venv
uv run pip install -r requirements.txt

# Authenticate Application Default Credentials (ADC) for Firestore access
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# Launch the app
uv run streamlit run src/app.py
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy no-cap-translator \
  --source . \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

## 📊 The "Slang Vault" (Persistence)

The application includes a live sidebar feed that pulls the latest 10 slang terms directly from the **Firestore** database, creating a shared organizational dictionary that evolves with every translation.

---