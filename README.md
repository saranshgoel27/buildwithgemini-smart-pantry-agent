# Smart Pantry Assistant 🥦 Apple 🥑

An intelligent AI assistant for smart pantry inventory management, expiration tracking, allergy-aware recipe planning, local supermarket discovery, and multimodal dish presentation generation powered by Google's Agent Development Kit (ADK) and Vertex AI.

![Smart Pantry Assistant Demo](smart_pantry_demo.gif?v=2)

---

## 🚀 Key Features & Capabilities

Based on the actual codebase implementation (`app/`), Smart Pantry Assistant provides the following capabilities:

- **📦 Firestore Pantry Inventory Management**: List, add, update, track expiration dates, and remove ingredients stored in Google Cloud Firestore (`app/pantry_tools.py`).
- **🧠 Durable Memory Bank**: Remembers user dietary restrictions, allergies, and health preferences across conversation sessions using `VertexAiMemoryBankService` on Vertex AI (`app/agent.py`).
- **📍 Real-Time Local Supermarket Search**: Converts addresses or city names into coordinates via Geocoding and searches for nearby supermarkets/grocery stores using Google Places API (New) (`app/maps_tools.py`).
- **📸 Food Image Generation**: Generates dish presentation previews using `imagen-3.0-generate-002`, saves them as session artifacts, and uploads them to Google Cloud Storage to return public HTTPS URLs (`app/image_tools.py`).
- **📹 Food Video Clip Generation**: Generates 3–5 second food and kitchen clips using Google's Omni model (`gemini-omni-flash-preview`) in the `global` region, saves artifacts, and uploads them directly to Google Cloud Storage (`app/video_tools.py`).
- **🎨 Adaptive UI (A2UI v0.8)**: Generates structured, responsive UI surfaces (cards, columns, rows, images) using `A2uiSchemaManager` (v0.8) and `a2ui_callback` (`app/a2ui_utils.py`).
- **🌐 Custom FastAPI Frontend & A2A Proxy**: A branded, responsive web chat interface built with FastAPI forwarding messages to the Agent Runtime via the `a2a-sdk` (`frontend/`), featuring an instant **🔄 New Chat** session reset button and `/reset` endpoint.

---

## 🛠️ Architecture & Google Cloud Services

- **Framework**: Google Agent Development Kit (ADK) with `Gemini` models.
- **Database**: Google Cloud Firestore (Native Mode) for pantry item persistence.
- **Memory**: Vertex AI Memory Bank (`VertexAiMemoryBankService`).
- **Media Storage**: Google Cloud Storage public media bucket (`gs://qwiklabs-gcp-02-fa5a2915d776-smart-pantry-media`).
- **Location Services**: Google Maps Geocoding API & Google Places API (New).
- **Generative Models**:
  - `gemini-flash-latest` (Core Agent Reasoning & Tool Execution)
  - `imagen-3.0-generate-002` (Image Generation)
  - `gemini-omni-flash-preview` (Video Generation)
- **Deployment Targets**: Deployed to Vertex AI Reasoning Engine (Agent Runtime) and Cloud Run.

---

## 💻 Local Setup & Execution Instructions

### Prerequisites

Ensure you have the following installed:
- Python 3.11+
- `uv` package manager (`pip install uv`)
- Node.js & npm (for Playwright / demo recorder)
- Google Cloud SDK (`gcloud`) authenticated to your GCP project

### 1. Set Up Environment Variables

Create or update `.env` in the project root:

```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-east1
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 2. Run the Agent Locally via ADK Playground

To run the agent locally using the ADK development web UI:

```bash
uv run adk web . --port 8080 --reload_agents
```

### 3. Run the Custom FastAPI Frontend Locally

To run the custom chat UI proxy against your deployed Reasoning Engine:

```bash
cd frontend
pip install -r requirements.txt

export AGENT_ENGINE_RESOURCE_NAME="projects/YOUR_PROJECT_NUMBER/locations/us-east1/reasoningEngines/YOUR_ENGINE_ID"
export AGENT_DIRECTORY="app"

uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 📂 Project Structure

```
smart-pantry-agent/
├── app/
│   ├── agent.py            # Root agent configuration, Memory Bank & system instructions
│   ├── pantry_tools.py     # Firestore CRUD tools for pantry inventory
│   ├── maps_tools.py       # Geocoding & Places API (New) search tools
│   ├── image_tools.py      # Imagen 3 image generation & Cloud Storage upload
│   ├── video_tools.py      # Gemini Omni video generation & Cloud Storage upload
│   └── a2ui_utils.py       # A2UI callback and structured schema manager
├── frontend/
│   ├── main.py             # FastAPI proxy backend using a2a-sdk
│   ├── static/index.html   # Rebranded responsive chat UI
│   └── Dockerfile          # Cloud Run container build spec
├── agents-cli-manifest.yaml # Agent deployment manifest
├── smart_pantry_demo.gif   # Looping demo recording
└── README.md               # Project documentation
```
