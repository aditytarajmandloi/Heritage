import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.services.graph_service import KnowledgeGraphService
from app.services.vector_service import VectorStoreService
from app.services.llm_service import LLMService
from app.services.audio_service import AudioService
from app.services.rag_service import HybridRAGService
from app.routers import graph_router, query_router

# Ensure static directories exist before mounting (runs at import time)
os.makedirs(os.path.join(settings.static_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.static_dir, "audio"), exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    print(f"[Heritage Explorer] {settings.app_name} -- Backend starting...")
    print(f"   Static dir : {settings.static_dir}")
    print(f"   Data dir   : {settings.data_dir}")
    print(f"   Chroma dir : {settings.chroma_persist_dir}")

    # Initialize Knowledge Graph (singleton for all requests)
    graph_service = KnowledgeGraphService(data_path=settings.data_dir)
    app.state.graph_service = graph_service
    summary = graph_service.get_graph_summary()
    print(f"   Graph loaded: {summary['total_nodes']} nodes, {summary['total_edges']} edges")

    # Initialize Vector Store
    vector_service = VectorStoreService(persist_dir=settings.chroma_persist_dir)
    app.state.vector_service = vector_service

    # Auto-ingest descriptions, pdfs, and images if collection is empty
    if vector_service.collection.count() == 0:
        import json
        data_file = os.path.join(settings.data_dir, "master_data.json")
        with open(data_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        descriptions_dir = os.path.join(settings.data_dir, "descriptions")
        vector_service.ingest_descriptions(descriptions_dir, raw_data.get("landmarks", []))
        
        # Ingest PDFs
        docs_dir = os.path.join(settings.data_dir, "docs")
        vector_service.ingest_pdfs(docs_dir)

    if vector_service.image_collection.count() == 0:
        # Ingest Images
        images_dir = os.path.join(settings.static_dir, "images")
        vector_service.ingest_images(images_dir)

    # Initialize LLM Service
    llm_service = LLMService(api_key=settings.groq_api_key)
    app.state.llm_service = llm_service

    # Initialize Audio Service
    audio_dir = os.path.join(settings.static_dir, "audio")
    audio_service = AudioService(output_dir=audio_dir)
    app.state.audio_service = audio_service

    # Initialize Hybrid RAG Service (the brain)
    rag_service = HybridRAGService(
        vector_service=vector_service,
        graph_service=graph_service,
        llm_service=llm_service,
        audio_service=audio_service,
        static_base_url="http://localhost:8000",
    )
    app.state.rag_service = rag_service
    print("   [RAG] Hybrid RAG pipeline ready!")

    yield

    # Shutdown
    print(f"[Heritage Explorer] {settings.app_name} -- Backend shutting down...")


# --- App Instance ---
app = FastAPI(
    title=settings.app_name,
    description="A Multi-Modal Graph RAG system for exploring Bengaluru's architectural heritage",
    version="1.0.0",
    lifespan=lifespan,
)


# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Mount Static Files ---
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


# --- Routers ---
app.include_router(graph_router.router)
app.include_router(query_router.router)


# --- Health Check ---
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the backend is running."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
    }
