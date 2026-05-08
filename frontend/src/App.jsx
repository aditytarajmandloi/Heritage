import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import ChatPanel from "./components/ChatPanel";
import MediaPanel from "./components/MediaPanel";
import Sidebar from "./components/Sidebar";
import { askQuestion, searchByImage } from "./services/api";

export default function App() {
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem("heritage_sessions");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.length > 0) return parsed;
      } catch (e) {}
    }
    return [{ id: Date.now().toString(), title: "New Session", messages: [], currentMedia: null }];
  });
  
  const [activeSessionId, setActiveSessionId] = useState(sessions[0]?.id);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    localStorage.setItem("heritage_sessions", JSON.stringify(sessions));
  }, [sessions]);

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];
  const messages = activeSession.messages;
  const currentMedia = activeSession.currentMedia;

  const handleNewSession = () => {
    const newSession = { id: Date.now().toString(), title: "New Session", messages: [], currentMedia: null };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newSession.id);
  };

  const handleDeleteSession = (id) => {
    const updated = sessions.filter(s => s.id !== id);
    if (updated.length === 0) {
      const fresh = { id: Date.now().toString(), title: "New Session", messages: [], currentMedia: null };
      setSessions([fresh]);
      setActiveSessionId(fresh.id);
    } else {
      setSessions(updated);
      if (id === activeSessionId) setActiveSessionId(updated[0].id);
    }
  };

  const updateActiveSession = (updates) => {
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return { ...s, ...updates };
      }
      return s;
    }));
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const userMsg = { id: Date.now(), type: "user", text };
    const newMessages = [...messages, userMsg];
    
    const titleUpdate = messages.length === 0 ? { title: text.substring(0, 30) + (text.length > 30 ? '...' : '') } : {};
    
    updateActiveSession({ messages: newMessages, ...titleUpdate });
    setIsLoading(true);
    setError(null);

    try {
      const historyPayload = messages.map((m) => ({
        role: m.type === "user" ? "user" : "assistant",
        content: m.text,
      }));

      const currentLandmark = currentMedia?.graph_data?.landmark || null;
      const data = await askQuestion(text, historyPayload, currentLandmark);

      const aiMsg = { id: Date.now() + 1, type: "ai", text: data.answer };
      
      updateActiveSession({
        messages: [...newMessages, aiMsg],
        currentMedia: { media: data.media, graph_data: data.graph_data }
      });

    } catch (err) {
      console.error(err);
      setError("Failed to connect to the Heritage Knowledge Base.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (imageFile) => {
    const userMsg = { id: Date.now(), type: "user", text: `[Uploaded Image: ${imageFile.name}]` };
    const newMessages = [...messages, userMsg];
    
    updateActiveSession({ messages: newMessages });
    setIsLoading(true);
    setError(null);

    try {
      const data = await searchByImage(imageFile);
      
      if (data.error) {
        setError(data.error);
        return;
      }

      const aiMsg = { id: Date.now() + 1, type: "ai", text: data.answer };
      
      updateActiveSession({
        messages: [...newMessages, aiMsg],
        currentMedia: { media: data.media, graph_data: data.graph_data }
      });

    } catch (err) {
      console.error(err);
      setError("Failed to search by image.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
      <main className="main-layout">
        <Sidebar 
          isOpen={isSidebarOpen}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={setActiveSessionId}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
        />
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSendMessage={handleSendMessage}
          onImageUpload={handleImageUpload}
        />
        <MediaPanel
          currentMedia={currentMedia}
          onRelatedClick={handleSendMessage}
        />
      </main>
    </>
  );
}
