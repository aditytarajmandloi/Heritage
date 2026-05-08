const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Send a question to the backend and get a multi-modal response.
 * @param {string} question - The user's question
 * @returns {Promise<Object>} - { answer, media: { image_url, audio_url }, graph_data }
 */
export async function askQuestion(question, history = [], current_landmark = null) {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history, current_landmark }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Query failed (${response.status}): ${errorText}`);
  }

  return response.json();
}

/**
 * Check if the backend is reachable.
 * @returns {Promise<Object>} - { status, app, version }
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) throw new Error("Backend unreachable");
  return response.json();
}

/**
 * Get the list of all landmarks from the graph.
 * @returns {Promise<Array>}
 */
export async function getLandmarks() {
  const response = await fetch(`${API_BASE}/api/graph/landmarks`);
  if (!response.ok) throw new Error("Failed to fetch landmarks");
  return response.json();
}

/**
 * Transcribe audio using the backend Groq Whisper API
 * @param {Blob} audioBlob - The audio recording
 * @returns {Promise<Object>} - { text }
 */
export async function transcribeAudio(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.webm");

  const response = await fetch(`${API_BASE}/api/transcribe`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Transcription failed (${response.status}): ${errorText}`);
  }

  return response.json();
}

/**
 * Upload an image to search via CLIP embeddings
 * @param {File} imageFile - The image to upload
 * @returns {Promise<Object>} - RAG response
 */
export async function searchByImage(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);

  const response = await fetch(`${API_BASE}/api/search_image`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Image search failed (${response.status}): ${errorText}`);
  }

  return response.json();
}
