# 🏛️ Bengaluru Heritage Explorer

> A Multi-Modal Graph RAG system for exploring Bengaluru's architectural heritage.

## Overview
This project is an advanced AI-powered Tour Guide built to explore the rich architectural heritage of Bengaluru. It goes beyond standard RAG (Retrieval-Augmented Generation) by implementing a **Hybrid Graph RAG** system that combines semantic vector search (ChromaDB) with structured relationship traversal (NetworkX Knowledge Graph) to provide the LLM with a rich "super-context".

The AI can not only describe landmarks but seamlessly recommend nearby sites, compare architectural styles, and contextualize historical eras. The application provides a **multi-modal experience** across **4 modalities**: text, images, voice input, and AI-generated audio guides.

## Heritage Sites Covered
The system covers **13 iconic Bengaluru landmarks** spanning over 1000 years of history:

| # | Landmark | Year | Style | Era |
|:--|:---------|:-----|:------|:----|
| 1 | Someshwara Temple | 1085 CE | Chola-Dravidian | Chola Period |
| 2 | Bull Temple (Nandi Temple) | 1537 | Dravidian | Vijayanagara Empire |
| 3 | Gavi Gangadhareshwara Temple | 1537 | Dravidian | Vijayanagara Empire |
| 4 | Bangalore Fort | 1537/1761 | Indo-Islamic | Pre-Colonial |
| 5 | Lalbagh Botanical Garden | 1760 | Colonial Landscape | Pre-Colonial |
| 6 | Tipu Sultan's Summer Palace | 1791 | Indo-Islamic | Pre-Colonial |
| 7 | St. Mark's Cathedral | 1808 | Gothic Revival | British Raj |
| 8 | Bangalore Palace | 1878 | Tudor Revival | British Raj |
| 9 | Mayo Hall | 1883 | Neo-Classical | British Raj |
| 10 | Government Museum | 1886 | Neo-Classical | British Raj |
| 11 | IISc Main Building | 1911 | Indo-Saracenic | British Raj |
| 12 | State Central Library | 1915 | Neo-Classical | British Raj |
| 13 | Vidhana Soudha | 1956 | Neo-Dravidian | Post-Independence |

## Architecture & Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Frontend** | React 19 + Vite 8 | Dark-themed, glassmorphic UI with chat, media & graph panels |
| **Backend** | FastAPI (Python 3.12) | High-performance async API server |
| **Vector DB** | ChromaDB + SentenceTransformers | Semantic search over text descriptions & PDF chunks |
| **Image Search** | CLIP (clip-ViT-B-32) | Multi-modal image-to-landmark matching via upload |
| **Knowledge Graph** | NetworkX (DiGraph) | Structured relationship mapping (Style, Era, Location, Nearby) |
| **LLM Engine** | Groq API (Llama 3.3 70B) | Natural language answer generation with chat history |
| **Voice Input** | Groq Whisper (large-v3-turbo) | Speech-to-text transcription for voice queries |
| **Audio Output** | gTTS | Text-to-Speech synthesis for audio guide generation |

## Multi-Modal Capabilities

### Input Modalities
1. **Text** — Type queries in the chat panel
2. **Voice** — Record audio queries via microphone (transcribed by Groq Whisper)
3. **Image Upload** — Upload a photo of a landmark for CLIP-based identification

### Output Modalities
1. **Text** — AI-generated conversational answers
2. **Image** — Landmark photographs displayed in the media panel
3. **Audio** — gTTS-generated `.mp3` audio guide for each response
4. **Graph** — Visual relationship tree showing style, era, location & related sites

## Ingestion Pipeline

The system ingests data from **3 source types** on startup:

```
data/descriptions/*.txt  →  SentenceTransformer (MiniLM)  →  ChromaDB (heritage_vectors)
data/docs/*.pdf          →  PyPDF2 → SentenceTransformer   →  ChromaDB (heritage_vectors)
static/images/*          →  CLIP (ViT-B-32)                →  ChromaDB (heritage_images)
```

- **13 text descriptions** embedded as semantic vectors
- **19 PDF pages** from the heritage guide extracted and embedded
- **13 landmark images** embedded as CLIP vectors for visual search

## RAG Pipeline (6 Steps)

When a user asks a question (e.g., *"What is the style of Vidhana Soudha?"*):

1. **Vector Search** — Queries ChromaDB to find the most semantically relevant text chunks
2. **Graph Traversal** — Extracts the `landmark_id` and traverses the NetworkX graph to find connected nodes (style, era, nearby landmarks, related sites via 2-hop traversal)
3. **Context Merge** — Combines text context + graph relationships into a single "super-context"
4. **LLM Synthesis** — Groq LLM generates a concise, conversational answer using the merged context
5. **Audio Generation** — gTTS converts the answer to an `.mp3` audio file
6. **Response Package** — Frontend receives text + image URL + audio URL + graph metadata

## Knowledge Graph Structure

```
39 nodes  |  61 edges

Node Types: landmark (14), style (9), era (5), location (11)
Edge Types: HAS_STYLE (13), BUILT_IN_ERA (13), LOCATED_IN (13), NEARBY (22)
```

Supports:
- **1-hop queries**: "What style is X?" → `landmark → HAS_STYLE → style`
- **2-hop queries**: "What other buildings share this style?" → `landmark → style → other landmarks`
- **Nearby discovery**: `landmark → NEARBY → landmark`

## Project Structure
```
project_root/
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings & env variables
│   │   ├── main.py            # FastAPI app with lifespan events
│   │   ├── routers/
│   │   │   ├── query_router.py    # /api/query, /api/transcribe, /api/search_image
│   │   │   └── graph_router.py    # /api/graph/landmarks, /connections, /summary
│   │   └── services/
│   │       ├── rag_service.py     # Hybrid RAG orchestrator (the brain)
│   │       ├── vector_service.py  # ChromaDB + CLIP embeddings
│   │       ├── graph_service.py   # NetworkX knowledge graph
│   │       ├── llm_service.py     # Groq LLM integration
│   │       └── audio_service.py   # gTTS audio synthesis
│   ├── data/
│   │   ├── master_data.json       # 13 landmarks, 9 styles, 5 eras
│   │   ├── descriptions/          # 13 text description files
│   │   └── docs/                  # heritage_guide.pdf (19 pages)
│   ├── static/images/             # 13 landmark photographs
│   ├── generate_pdf.py            # PDF generator script
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main app with session management
│   │   ├── main.jsx               # React entry point
│   │   ├── index.css              # Glassmorphic dark theme design system
│   │   ├── components/
│   │   │   ├── Header.jsx         # App header with branding
│   │   │   ├── ChatPanel.jsx      # Chat UI with text/voice/image input
│   │   │   ├── MediaPanel.jsx     # Image, audio player & graph tree
│   │   │   └── Sidebar.jsx        # Session management sidebar
│   │   └── services/
│   │       └── api.js             # Backend API communication
│   ├── index.html
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml             # Full-stack orchestration
```

## How to Run

### Local Development
```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
python generate_pdf.py           # Generate heritage PDF
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Docker
```bash
# Ensure Docker Desktop is running
docker compose up --build

# Or in background
docker compose up --build -d
```

### Access Points
| Service | URL |
|:--------|:----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

## Environment Variables

Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/api/query` | Main RAG query (text question + chat history) |
| POST | `/api/transcribe` | Audio-to-text transcription (Groq Whisper) |
| POST | `/api/search_image` | Image-based landmark search (CLIP) |
| GET | `/api/graph/landmarks` | List all landmarks in the knowledge graph |
| GET | `/api/graph/landmarks/{id}/connections` | Get graph connections for a landmark |
| GET | `/api/graph/summary` | Knowledge graph statistics |
| GET | `/api/health` | Backend health check |
