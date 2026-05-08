# 🏛️ Bengaluru Heritage Explorer

> A Multi-Modal Graph RAG system for exploring Bengaluru's architectural heritage.

## Overview
This project is an advanced AI Tour Guide built to explore the rich architectural heritage of Bengaluru. It goes beyond standard RAG (Retrieval-Augmented Generation) by implementing a **Hybrid Graph RAG** system. It combines semantic vector search (ChromaDB) with structured relationship traversal (NetworkX) to provide the LLM with a rich "super-context". 

This ensures the AI can not only describe landmarks but seamlessly recommend nearby sites, compare architectural styles, and contextualize historical eras. The application provides a multi-modal experience: text, images, and AI-generated audio guides.

## Heritage Sites Covered
The system covers **13 iconic Bengaluru landmarks** spanning over 1000 years of history:
- **Someshwara Temple** (1085 CE) — Bengaluru's oldest surviving temple
- **Bull Temple & Gavi Gangadhareshwara Temple** (1537) — Vijayanagara-era treasures
- **Bangalore Fort** (1537/1761) — The birthplace of the city
- **Lalbagh Botanical Garden** (1760) — Hyder Ali's botanical legacy
- **Tipu Sultan's Summer Palace** (1791) — Indo-Islamic wooden palace
- **St. Mark's Cathedral** (1808) — One of Asia's oldest Anglican churches
- **Bangalore Palace** (1878) — Tudor Revival elegance
- **Mayo Hall & Government Museum** (1880s) — British Raj Neo-Classical gems
- **IISc Main Building** (1911) — Indo-Saracenic academic landmark
- **State Central Library** (1915) — Neo-Classical Cubbon Park icon
- **Vidhana Soudha** (1956) — Post-Independence Neo-Dravidian masterpiece

## Architecture & Tech Stack

| Layer      | Technology                    | Purpose |
|:-----------|:------------------------------|:--------|
| **Frontend**   | React + Vite                  | Dark-themed, glassmorphic UI |
| **Backend**    | FastAPI (Python 3.12)         | High-performance API server |
| **Vector DB**  | ChromaDB + SentenceTransformers | Semantic search over text descriptions |
| **Image Search** | CLIP (clip-ViT-B-32) | Multi-modal image-to-landmark matching |
| **Graph DB**   | NetworkX                      | Structured relationship mapping (Style, Era, Location) |
| **LLM Engine** | Groq API (Llama 3.3 70B) | Natural language answer generation |
| **Audio**      | gTTS                          | Text-to-Speech synthesis for accessibility |

## Project Structure
```
project_root/
├── backend/
│   ├── app/
│   │   ├── routers/       # API Endpoints (query, graph)
│   │   └── services/      # RAG Pipeline, LLM, Audio, Vector, Graph
│   ├── data/              # master_data.json and text descriptions
│   ├── static/            # Images and generated Audio
│   └── chroma_data/       # Persistent vector storage
├── frontend/
│   ├── src/
│   │   ├── components/    # ChatPanel, MediaPanel, Header
│   │   └── services/      # API communication
│   └── index.html
└── docker-compose.yml     # Full-stack orchestration
```

## How to Run

### Local Development
1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Add your Groq API key to backend/.env
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Access the Frontend: `http://localhost:5173`
4. Access Backend API Docs: `http://localhost:8000/docs`

### Docker (when configured)
```bash
docker compose up --build
```

## How it Works (The Pipeline)
When a user asks a question (e.g., *"What is the style of Vidhana Soudha?"*):
1. **Vector Search:** Queries ChromaDB to find the most semantically relevant text chunks.
2. **Graph Traversal:** Extracts the identified `landmark_id` and traverses the NetworkX graph to find connected nodes (e.g., Neo-Dravidian style, nearby buildings).
3. **Context Merge:** Combines the text and graph relationships into a single, comprehensive prompt.
4. **LLM Synthesis:** The LLM generates a concise, accurate, and conversational answer.
5. **Multi-Modal Generation:** The answer is sent to gTTS to generate an audio `.mp3` file.
6. **Response:** The frontend receives the text, audio URL, image URL, and graph metadata and renders the UI.
