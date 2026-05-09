import { useRef, useEffect, useState } from "react";
import { transcribeAudio } from "../services/api";

const SUGGESTIONS = [
  { icon: "🏛️", text: "Tell me about Vidhana Soudha" },
  { icon: "🐂", text: "What is the history of Bull Temple?" },
  { icon: "🌿", text: "Describe Lalbagh Botanical Garden" },
  { icon: "🏰", text: "Tell me about Bangalore Palace" },
  { icon: "🕌", text: "Explore Tipu Sultan's Palace" },
  { icon: "⛪", text: "What style is St. Mark's Cathedral?" },
];

export default function ChatPanel({ messages, isLoading, error, onSendMessage, onImageUpload }) {
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, isTranscribing]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (isRecording) { stopRecording(); return; }
    const text = inputText.trim();
    if (!text) return;
    onSendMessage(text);
    setInputText("");
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };
      mediaRecorder.onstop = async () => {
        setIsRecording(false);
        setIsTranscribing(true);
        setInputText("Transcribing audio...");
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const result = await transcribeAudio(audioBlob);
          if (result.text && result.text.trim()) {
            setInputText("");
            onSendMessage(result.text.trim());
          } else {
            setInputText("");
            alert("No speech detected.");
          }
        } catch (err) {
          console.error("Transcription error:", err);
          alert("Failed to transcribe audio.");
          setInputText("");
        } finally {
          setIsTranscribing(false);
          stream.getTracks().forEach(track => track.stop());
        }
      };
      mediaRecorder.start();
      setIsRecording(true);
      setInputText("Recording... (Click mic to send)");
    } catch (err) {
      alert("Microphone access denied.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) mediaRecorderRef.current.stop();
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && !isLoading && !isTranscribing && (
          <div className="chat-empty">
            <div className="chat-empty__icon">🏛️</div>
            <h2 className="chat-empty__title">Explore Bengaluru's Heritage</h2>
            <p className="chat-empty__sub">Ask about any of the 13 iconic landmarks spanning 1000+ years of history. Try text, voice, or image upload.</p>
            <div className="chat-empty__suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="chat-empty__chip" onClick={() => onSendMessage(s.text)}>
                  <span className="chat-empty__chip-icon">{s.icon}</span>
                  {s.text}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message message--${msg.type}`}>
            <span className="message__label">
              {msg.type === "user" ? "You" : "Heritage AI"}
            </span>
            <div className="message__bubble">{msg.text}</div>
          </div>
        ))}

        {(isLoading || isTranscribing) && (
          <div className="message message--ai message--loading">
            <span className="message__label">Heritage AI</span>
            <div className="message__bubble">
              {isTranscribing ? "Transcribing audio" : "Searching knowledge base"}
              <span className="loading-dots"></span>
            </div>
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input type="file" accept="image/*" ref={fileInputRef} style={{ display: 'none' }} onChange={(e) => { const file = e.target.files[0]; if (file && onImageUpload) onImageUpload(file); e.target.value = ""; }} />
        <button type="button" className="chat-input__voice-btn" onClick={() => fileInputRef.current?.click()} title="Upload Image" disabled={isLoading || isTranscribing}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </button>
        <button type="button" className={`chat-input__voice-btn ${isRecording ? 'listening' : ''}`} onClick={() => isRecording ? stopRecording() : startRecording()} title={isRecording ? "Stop" : "Record"} disabled={isLoading || isTranscribing}>
          {isRecording ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"></rect></svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          )}
        </button>
        <input type="text" value={inputText} onChange={(e) => setInputText(e.target.value)} className="chat-input__field" placeholder={isRecording ? "Recording..." : "Ask about a heritage site..."} disabled={isLoading || isRecording || isTranscribing} />
        <button type="submit" className="chat-input__button" disabled={isLoading || isTranscribing || (!inputText.trim() && !isRecording)}>
          {isLoading || isTranscribing ? "..." : "Ask"}
        </button>
      </form>
    </div>
  );
}
