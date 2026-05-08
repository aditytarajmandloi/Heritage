"""
LLM Service — Phase 3.3

Integrates Groq API for natural language generation.
Takes merged context (vector + graph) and generates tour guide responses.
"""

from groq import Groq


SYSTEM_PROMPT = """You are a highly intelligent and conversational Bengaluru Heritage Tour Guide.
Your job is to answer the user's question directly, accurately, and engagingly.

Use the following retrieved context to inform your answer:
**Retrieved Text:**
{vector_context}

**Retrieved Relationships (from Knowledge Graph):**
{graph_context}

CRITICAL RULES:
1. DIRECTLY ANSWER THE QUESTION FIRST. Do not just dump a generic description unless they ask for a general overview.
2. If they ask a specific question (e.g., "what year?", "who built it?", "what style?"), give them that exact answer immediately, then add 1-2 sentences of interesting context.
3. Use the graph relationships! If they ask what else is nearby or similar, look at the "Retrieved Relationships" to give them related landmarks.
4. Keep it conversational, smart, and concise (2-4 sentences max). Avoid sounding like a textbook.
5. If the retrieved text/graph doesn't have the exact answer, you may use your own general knowledge to help, but mention that you are adding extra info.
"""


class LLMService:
    """Handles natural language generation via Groq API."""

    def __init__(self, api_key: str):
        """Initialize the Groq client."""
        if not api_key:
            print("   [LLM] WARNING: No Groq API key provided. LLM will use fallback mode.")
            self.client = None
            return

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        print(f"   [LLM] Groq client initialized ({self.model})")

    def generate(self, vector_context: str, graph_context: str, question: str, history: list = None) -> str:
        """
        Generate a natural language answer using the augmented context.
        Falls back to raw vector text if Groq API is unavailable.
        """
        if not self.client:
            return self._fallback_response(vector_context, question)

        try:
            prompt = SYSTEM_PROMPT.format(
                vector_context=vector_context,
                graph_context=graph_context,
            )

            messages = []
            if history:
                for msg in history:
                    # Groq roles: 'user', 'assistant', 'system'
                    role = "assistant" if msg.get("role") == "ai" else "user"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            # System prompt can be added as the first message or combined. We'll combine it with the latest user query.
            messages.append({
                "role": "user",
                "content": f"System Context:\n{prompt}\n\nUser Question: {question}"
            })

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content.strip()
            else:
                return self._fallback_response(vector_context, question)

        except Exception as e:
            print(f"   [LLM] Groq API error: {e}")
            return self._fallback_response(vector_context, question)

    def transcribe_audio(self, audio_file) -> str:
        """Transcribe an audio file using Groq Whisper API."""
        if not self.client:
            raise ValueError("Groq API client is not initialized.")
            
        try:
            transcription = self.client.audio.transcriptions.create(
              file=audio_file,
              model="whisper-large-v3-turbo",
              response_format="json",
              language="en",
            )
            return transcription.text
        except Exception as e:
            print(f"   [LLM] Groq Whisper API error: {e}")
            raise e

    def _fallback_response(self, vector_context: str, question: str) -> str:
        """Return raw vector text when LLM is unavailable."""
        if vector_context:
            return f"[Note: AI generation is unavailable (API error). Showing raw database results.]\n\n{vector_context}"
        return "I'm sorry, I couldn't find relevant information about that topic in our heritage database."
