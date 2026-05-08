import { useRef, useEffect, useState } from "react";
import { transcribeAudio } from "../services/api";

export default function ChatPanel({
  messages,
  isLoading,
  error,
  onSendMessage,
  onImageUpload,
}) {
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
    if (isRecording) {
      stopRecording();
      return;
    }
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
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
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
            alert("No speech detected in the recording.");
          }
        } catch (err) {
          console.error("Transcription error:", err);
          alert("Failed to transcribe audio. Ensure backend is running and Groq API key is set.");
          setInputText("");
        } finally {
          setIsTranscribing(false);
          // Stop all audio tracks to release microphone
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setInputText("Recording... (Click mic to send)");
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Microphone access was denied. Please allow microphone permissions in your browser settings.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleImageClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && onImageUpload) {
      onImageUpload(file);
    }
    e.target.value = "";
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && !isLoading && !isTranscribing && (
          <div className="chat-messages__empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{opacity: 0.3}}>
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p className="chat-messages__empty-text">
              Explore Bengaluru's Heritage
            </p>
            <p className="chat-messages__empty-hint">
              Query the architectural database
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message message--${msg.type}`}>
            <span className="message__label">
              {msg.type === "user" ? "Query" : "System"}
            </span>
            <div className="message__bubble">{msg.text}</div>
          </div>
        ))}

        {(isLoading || isTranscribing) && (
          <div className="message message--ai message--loading">
            <span className="message__label">System</span>
            <div className="message__bubble">
              {isTranscribing ? "Transcribing audio" : "Processing request"}
              <span className="loading-dots"></span>
            </div>
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input 
          type="file" 
          accept="image/*" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileChange} 
        />
        <button 
          type="button" 
          className="chat-input__voice-btn"
          onClick={handleImageClick}
          title="Upload Image to Search"
          disabled={isLoading || isTranscribing}
          style={{ marginRight: '8px' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </button>
        <button 
          type="button" 
          className={`chat-input__voice-btn ${isRecording ? 'listening' : ''}`}
          onClick={handleMicClick}
          title={isRecording ? "Stop & Send" : "Record Audio"}
          disabled={isLoading || isTranscribing}
        >
          {isRecording ? (
             <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
               <rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>
             </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          )}
        </button>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="chat-input__field"
          placeholder={isRecording ? "Recording... Click stop to send." : "Enter query parameters..."}
          disabled={isLoading || isRecording || isTranscribing}
        />
        <button
          type="submit"
          className="chat-input__button"
          disabled={isLoading || isTranscribing || (!inputText.trim() && !isRecording)}
        >
          {isLoading || isTranscribing ? "Wait" : "Submit"}
        </button>
      </form>
    </div>
  );
}
