Here is the comprehensive `README.md` for your backend repository.

***

```markdown
# Constitution Analyzer - Backend API

The intelligent engine behind the Constitution Analyzer. This is a high-performance, asynchronous API that orchestrates web scraping, prompt engineering, and interaction with Google's Gemini AI models to provide detailed legal analysis and conversational Q&A.

## 🚀 Features

*   **Dual-Model AI Strategy:**
    *   **Gemini 1.5 Pro:** Used for deep, initial document analysis.
    *   **Gemini 2.0 Flash:** Used for fast, cost-effective follow-up questions.
*   **Context Engineering:** Real-time scraping and cleaning of legal text from `gov.za` URLs using `httpx` and `BeautifulSoup4`.
*   **Robust Prompt Engineering:** Uses advanced XML-structured prompts with strict guardrails, style guides, and JSON mode enforcement.
*   **Stateless "Dual Context" Memory:** Handles follow-up questions by re-grounding the AI in both the original source text and the initial analysis for every request.
*   **Secure Infrastructure:** Fully containerized, runs on Google Cloud Run with strict IAM permissions and Secret Manager integration.

## 🛠️ Tech Stack

*   **Framework:** FastAPI
*   **Server:** Uvicorn
*   **Package Management:** `uv` (pyproject.toml)
*   **AI SDK:** `google-generativeai` (Vertex AI)
*   **Infrastructure:** Docker, Google Cloud Run, Artifact Registry

## 📂 Project Structure

```

```

## ⚡️ Getting Started

### Prerequisites

*   Python 3.11+
*   `uv` (recommended) or `pip`
*   A Google Cloud Project with Vertex AI enabled
*   A Gemini API Key

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/constitution-analyzer-backend.git
    cd constitution-analyzer-backend
    ```

2.  Create a virtual environment and install dependencies:
    ```bash
    # Using uv (Recommended)
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

3.  **Configure Secrets:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY="your_actual_gemini_api_key_here"
    ```

### Running Locally

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Interactive docs (Swagger UI) are available at `http://127.0.0.1:8000/docs`.

## 🧪 Testing

This project includes a robust test suite and an "AI Grading AI" evaluation pipeline.

**Run Unit Tests:**
```bash
pytest
```

**Run Prompt Quality Evals:**
```bash
python run_evals.py
```
*This script uses `eval_dataset.json` to test the AI's output against a fact-based rubric.*

## 🐳 Docker & Deployment

### Local Docker Build

```bash
docker build -t constitution-analyzer-api .
docker run -p 8000:8080 --env-file .env constitution-analyzer-api
```

### CI/CD Pipeline (Google Cloud)

The project is configured for automated deployment via **Google Cloud Build**.

1.  **Trigger:** Push to `main` branch.
2.  **Build:** Cloud Build compiles the Docker image.
3.  **Push:** Image is uploaded to Artifact Registry (`europe-west1`).
4.  **Deploy:** New revision deployed to Cloud Run.

**Configuration (`cloudbuild.yaml`):**
*   Ensure the `_SERVICE_NAME`, `_REGION`, and `_REPO_NAME` substitutions match your GCP project.
*   The Cloud Run service runs as a dedicated Service Account (`constitution-analyzer-sa`) with minimal permissions (`aiplatform.user`, `secretmanager.secretAccessor`).

## 🤝 Related Repositories

*   **Frontend UI:** [Link to your frontend repo] - The Vue.js application that consumes this API.
  ![Front End](https://github.com/MokSent-Studio/constitutional-analyzer-fe)
```
