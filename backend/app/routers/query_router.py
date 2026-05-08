"""
Query API Router — Phase 3.5

The single most important endpoint in the entire project.
POST /api/query proves: RAG pipeline, Knowledge Graph, and 3 modalities — all in one response.
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel


from typing import List, Optional

router = APIRouter(prefix="/api", tags=["Query"])

class ChatMessage(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    """Request body for the query endpoint."""
    question: str
    history: Optional[List[ChatMessage]] = []
    current_landmark: Optional[str] = None


@router.post("/query")
async def query_heritage(request: Request, body: QueryRequest):
    """
    The main query endpoint — executes the full hybrid RAG pipeline.

    Steps:
    1. Semantic search (ChromaDB) for relevant text
    2. Graph traversal (NetworkX) for relationships
    3. Context merge (vector + graph)
    4. LLM generation (Gemini) for natural language answer
    5. Audio generation (gTTS) for 3rd modality
    6. Package response with text + image + audio + graph data

    Returns a multi-modal JSON response.
    """
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        response_data = request.app.state.rag_service.query(
            user_question=body.question,
            history=[msg.model_dump() for msg in body.history] if body.history else None,
            current_landmark=body.current_landmark
        )
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """
    Transcribes audio bytes to text using Groq Whisper.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        # Groq needs a tuple of (filename, bytes)
        file_tuple = (file.filename, audio_bytes)
        
        text = request.app.state.rag_service.llm.transcribe_audio(file_tuple)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_image")
async def search_image(request: Request, file: UploadFile = File(...)):
    """
    Search by uploaded image using CLIP embeddings.
    Finds the most similar landmark, then triggers a RAG response.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")
            
        vector_service = request.app.state.vector_service
        match = vector_service.search_by_image(image_bytes)
        
        if not match or not match.get("landmark_id"):
            return {"error": "No matching landmark found for this image."}
            
        landmark_id = match["landmark_id"]
        
        # Now, we use the matched landmark to trigger a standard RAG query
        # We simulate a user asking "Tell me about this image"
        question = f"Tell me about {landmark_id.replace('_', ' ').title()}"
        
        response_data = request.app.state.rag_service.query(
            user_question=question,
            history=[],
            current_landmark=landmark_id
        )
        return response_data
    except Exception as e:
        print(f"Error in image search: {e}")
        raise HTTPException(status_code=500, detail=str(e))
