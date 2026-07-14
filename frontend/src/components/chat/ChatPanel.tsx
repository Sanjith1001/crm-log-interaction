import React, { useState, useRef, useEffect } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { MessageBubble } from "./MessageBubble";
import { useAgentStream } from "../../hooks/useAgentStream";
import "../../pages/pages.css";

export function ChatPanel() {
  const messages = useSelector((state: RootState) => state.chat.messages);
  const isStreaming = useSelector((state: RootState) => state.chat.isStreaming);
  const currentStatus = useSelector((state: RootState) => state.chat.currentStatus);
  const pendingConfirmation = useSelector((state: RootState) => state.chat.pendingConfirmation);
  
  const { sendMessage } = useAgentStream();
  const [input, setInput] = useState("");
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  // Web Speech API Configuration
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognitionRef = useRef<any>(null);
  const [isListening, setIsListening] = useState(false);
  const [recognitionSupport, setRecognitionSupport] = useState(false);

  useEffect(() => {
    if (SpeechRecognition) {
      setRecognitionSupport(true);
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = "en-US";
      
      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => (prev ? prev + " " + transcript : transcript));
        setIsListening(false);
      };
      
      rec.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
        if (event.error === "not-allowed") {
          setInput("⚠️ Mic access denied. Verify browser mic permissions.");
        } else if (event.error === "no-speech") {
          setInput("⚠️ No speech detected. Please speak closer to mic.");
        } else {
          setInput(`⚠️ Voice type error: ${event.error}`);
        }
        setTimeout(() => {
          setInput("");
        }, 4000);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, [SpeechRecognition]);

  const handleSpeechToggle = () => {
    if (!recognitionRef.current) return;
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim(), "chat");
    setInput("");
  };

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [messages, currentStatus]);

  return (
    <div className="panel-card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div className="panel-header">
        <h3 className="panel-title">🤖 Aegis AI Assistant</h3>
        {currentStatus && (
          <span style={{ fontSize: 12, color: "var(--accent-ai)" }}>
            ● {currentStatus}
          </span>
        )}
      </div>

      <div ref={chatMessagesRef} className="chat-messages" style={{ flexGrow: 1, overflowY: "auto" }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "var(--text-secondary)", margin: "auto" }}>
            <p style={{ fontSize: 24, marginBottom: 8 }}>👋 Hello Representative!</p>
            <p style={{ fontSize: 14 }}>
              How can I help you today? You can say things like:
            </p>
            <ul style={{ listStyle: "none", marginTop: 12, display: "flex", flexDirection: "column", gap: 8, fontSize: 13, color: "var(--primary)" }}>
              <li>• "Met with Dr. Rao to discuss Lipitor and key insights."</li>
              <li>• "Show all my visits from the past week."</li>
              <li>• "What should I focus on for my next visit with Dr. Sharma?"</li>
            </ul>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} message={m} />)
        )}
        
        {pendingConfirmation && (
          <MessageBubble
            message={{
              id: "pending-conf-message",
              sender: "agent",
              text: "Please review and confirm the updates above:",
              pendingConfirmation
            }}
          />
        )}
      </div>

      <form className="chat-input-container" onSubmit={handleSubmit}>
        {recognitionSupport && (
          <button
            type="button"
            onClick={handleSpeechToggle}
            className="mic-btn"
            style={{
              background: "none",
              border: "none",
              color: isListening ? "var(--error)" : "var(--primary)",
              cursor: "pointer",
              fontSize: 18,
              padding: "0 12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              animation: isListening ? "pulse 1.5s infinite" : "none"
            }}
            title={isListening ? "Listening... Click to stop" : "Speak to agent"}
          >
            {isListening ? "🎙️🔴" : "🎙️"}
          </button>
        )}
        <input
          type="text"
          className="chat-textarea"
          placeholder={pendingConfirmation ? "Waiting for confirmation..." : "Describe the interaction, ask questions..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming || !!pendingConfirmation}
        />
        <button type="submit" className="chat-send-btn" disabled={isStreaming || !input.trim() || !!pendingConfirmation}>
          ➔
        </button>
        {isListening && (
          <style>{`
            @keyframes pulse {
              0% { transform: scale(1); opacity: 1; }
              50% { transform: scale(1.15); opacity: 0.7; }
              100% { transform: scale(1); opacity: 1; }
            }
          `}</style>
        )}
      </form>
    </div>
  );
}
export default ChatPanel;
