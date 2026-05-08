"""
Hybrid RAG Service — Phase 3.2

The core "brain" of the project. Combines:
  1. Vector similarity search (ChromaDB)
  2. Knowledge Graph traversal (NetworkX)
  3. LLM generation (Gemini)
  4. Audio synthesis (gTTS)

Into a single multi-modal query pipeline.
"""

from app.services.vector_service import VectorStoreService
from app.services.graph_service import KnowledgeGraphService
from app.services.llm_service import LLMService
from app.services.audio_service import AudioService


class HybridRAGService:
    """Orchestrates the full hybrid retrieval-augmented generation pipeline."""

    def __init__(
        self,
        vector_service: VectorStoreService,
        graph_service: KnowledgeGraphService,
        llm_service: LLMService,
        audio_service: AudioService,
        static_base_url: str = "http://localhost:8000",
    ):
        self.vector = vector_service
        self.graph = graph_service
        self.llm = llm_service
        self.audio = audio_service
        self.static_base_url = static_base_url

    def query(self, user_question: str, history: list = None, current_landmark: str = None) -> dict:
        """
        Execute the full 6-step hybrid RAG pipeline.

        Args:
            user_question: The query from the user.
            history: Optional list of previous chat messages.
            current_landmark: Optional name of the currently active landmark to contextualize follow-ups.
        """
        # ───── Step 1: VECTOR RETRIEVAL (Semantic Search) ─────
        search_query = user_question
        # If it's a short follow-up question and we have a context landmark, combine them
        if current_landmark and len(user_question.split()) < 10:
            search_query = f"{current_landmark} {user_question}"

        vector_results = self.vector.search(search_query, n_results=2)

        # ───── Step 2: GRAPH TRAVERSAL (Graph Layer) ─────
        graph_data = {}
        connections = {}
        related_sites = []
        primary_landmark = None

        # Determine the visual landmark
        landmark_id = None
        
        # 1. Did the user explicitly ask for a specific landmark?
        for lm in self.graph.get_all_landmarks():
            if lm["name"].lower() in user_question.lower():
                landmark_id = lm["id"]
                break
                
        # 2. If not, and we have a current_landmark, keep the visual locked to it!
        if not landmark_id and current_landmark:
            lm = self.graph.find_landmark_by_name(current_landmark)
            if lm:
                landmark_id = lm["id"]
                
        # 3. Fallback to vector search match
        if not landmark_id and vector_results:
            landmark_id = vector_results[0]["landmark_id"]

        if landmark_id:
            primary_landmark = self.graph.get_landmark(landmark_id)
            connections = self.graph.get_connections(landmark_id)
            nearby = self.graph.find_nearby(landmark_id)
            related = self.graph.get_related_landmarks(landmark_id)

            top_match = vector_results[0] if vector_results else {}

            # Build graph_data for the response
            graph_data = {
                "landmark": primary_landmark.get("name", "") if primary_landmark else top_match.get("landmark_name", ""),
                "style": primary_landmark.get("style", "") if primary_landmark else top_match.get("style", ""),
                "era": primary_landmark.get("era", "") if primary_landmark else top_match.get("era", ""),
                "location": f"{primary_landmark.get('location', '')}, {primary_landmark.get('neighborhood', '')}".strip(", ") if primary_landmark else "",
                "related_sites": [n.get("name", "") for n in nearby if n.get("name")]
                               + [r.get("name", "") for r in related if r.get("name")],
            }

            # Deduplicate related sites
            graph_data["related_sites"] = list(dict.fromkeys(graph_data["related_sites"]))

        # ───── Step 3: CONTEXT MERGE (Super-Context) ─────
        vector_context = self._format_vector_context(vector_results)
        graph_context = self._format_graph_context(connections, graph_data)
        merged_context = f"{vector_context}\n\n{graph_context}"

        # ───── Step 4: LLM GENERATION ─────
        answer = self.llm.generate(vector_context, graph_context, user_question, history)

        # ───── Step 5: AUDIO GENERATION (3rd Modality) ─────
        audio_text = answer
        if "[Note:" in answer:
            import re
            audio_text = re.sub(r'\[Note:.*?\]', '', answer, flags=re.DOTALL).strip()
            
        audio_url_path = self.audio.generate_speech(audio_text)
        audio_url = f"{self.static_base_url}{audio_url_path}" if audio_url_path else ""

        # ───── Step 6: RESPONSE PACKAGE ─────
        image_url = ""
        images = []
        if primary_landmark:
            if primary_landmark.get("image_file"):
                image_url = f"{self.static_base_url}/static/images/{primary_landmark['image_file']}"
            if primary_landmark.get("images"):
                images = primary_landmark["images"]

        return {
            "answer": answer,
            "media": {
                "image_url": image_url,
                "images": images,
                "audio_url": audio_url,
            },
            "graph_data": graph_data,
        }

    def _format_vector_context(self, vector_results: list[dict]) -> str:
        """Format vector search results into a readable context string."""
        if not vector_results:
            return "No relevant text found in the heritage database."

        parts = []
        for i, match in enumerate(vector_results, 1):
            parts.append(
                f"[Match {i}] {match['landmark_name']} "
                f"(Style: {match.get('style', 'N/A')}, Era: {match.get('era', 'N/A')}):\n"
                f"{match['text'][:600]}"
            )
        return "\n\n".join(parts)

    def _format_graph_context(self, connections: dict, graph_data: dict) -> str:
        """Format graph traversal results into a readable context string."""
        if not connections and not graph_data:
            return "No graph relationships found."

        parts = []

        if graph_data.get("landmark"):
            parts.append(f"Primary Landmark: {graph_data['landmark']}")

        if graph_data.get("style"):
            parts.append(f"Architectural Style: {graph_data['style']}")

        if graph_data.get("era"):
            parts.append(f"Historical Era: {graph_data['era']}")

        if graph_data.get("location"):
            parts.append(f"Location: {graph_data['location']}")

        # Add style description from connections
        for style in connections.get("styles", []):
            if style.get("description"):
                parts.append(f"Style Description: {style['description']}")

        # Add era description from connections
        for era in connections.get("eras", []):
            if era.get("description"):
                parts.append(f"Era Context: {era['description']}")
            if era.get("period"):
                parts.append(f"Period: {era['period']}")

        # Add nearby landmarks
        nearby_names = [n.get("name", "") for n in connections.get("nearby", []) if n.get("name")]
        if nearby_names:
            parts.append(f"Nearby Landmarks: {', '.join(nearby_names)}")

        # Add related sites
        if graph_data.get("related_sites"):
            parts.append(f"Related Sites: {', '.join(graph_data['related_sites'])}")

        return "\n".join(parts)
