"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Sparkles, MessageSquare, Bot, User } from "lucide-react";
import { motion } from "framer-motion";
import { api, getSession, UserSession } from "../../lib/api";
import AgentPanel, { AgentLog } from "../../components/agent-panel";


interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Agent logging tracking states
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([]);
  const [activeRoute, setActiveRoute] = useState("");
  const [activeSql, setActiveSql] = useState<string | null>(null);
  const [activeDocs, setActiveDocs] = useState<any[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionIdRef = useRef<string>(`session_${Date.now()}`);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    
    // Start with a clean, fresh session every time the user logs in / page mounts
    sessionIdRef.current = `session_${s.userId}_${Date.now()}`;
    setMessages([
      { role: "assistant", content: `Hello ${s.name}! I am your college multi-agent assistant. Ask me anything about attendance percentages, grades, classroom bookings, or college handbook policies.` }
    ]);
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent, promptValue?: string) => {
    if (e) e.preventDefault();
    const messageToSend = promptValue || input;
    if (!messageToSend.trim() || loading) return;

    setInput("");
    setMessages(prev => [...prev, { role: "user", content: messageToSend }]);
    setLoading(true);
    setAgentLogs([]);
    setActiveRoute("");
    setActiveSql(null);
    setActiveDocs([]);

    try {
      const res = await api.sendMessage(messageToSend, sessionIdRef.current);
      setMessages(prev => [...prev, { role: "assistant", content: res.response }]);
      setAgentLogs(res.agent_log || []);
      setActiveRoute(res.route || "");
      setActiveSql(res.sql_query || null);
      setActiveDocs(res.retrieved_docs || []);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSubmit(undefined, suggestion);
  };

  const suggestions = [
    "What is my attendance percentage?",
    "Show my enrolled courses.",
    "What are the rules for medical leaves?",
    "Show all room bookings.",
  ];

  if (!session) return null;

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Chat area */}
      <div className="flex-1 flex flex-col bg-slate-50 relative min-w-0">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-4 flex items-center gap-3 shrink-0">
          <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
            <Sparkles className="w-5 h-5 fill-indigo-50" />
          </div>
          <div>
            <h2 className="font-bold text-slate-800 text-base">Multi-Agent Assistant</h2>
            <p className="text-xs text-slate-400 font-medium">Orchestrated by LangGraph &amp; Ollama</p>
          </div>
        </div>

        {/* Conversations viewport */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {messages.map((msg, index) => (
            <div key={index} className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div className={`p-4 rounded-3xl max-w-lg leading-relaxed text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-100"
                  : "bg-white text-slate-700 rounded-tl-none border border-slate-200/60 shadow-sm"
              }`}>
                {msg.content}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-xs shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-4 items-center">
              <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-white p-4 rounded-3xl rounded-tl-none border border-slate-200/60 shadow-sm flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce delay-75" />
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce delay-150" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts */}
        {messages.length <= 1 && (
          <div className="px-8 pb-4 shrink-0">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Suggested prompts</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSuggestionClick(s)}
                  className="px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold rounded-2xl text-slate-600 hover:text-slate-800 transition-all duration-200 cursor-pointer shadow-sm"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input box */}
        <div className="p-6 bg-white border-t border-slate-200 shrink-0">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 px-5 py-4 border border-slate-200 rounded-3xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all duration-200 shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="w-14 h-14 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-100 disabled:text-slate-450 disabled:cursor-not-allowed text-white rounded-3xl flex items-center justify-center transition-all duration-200 shadow-md shadow-indigo-150"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

      {/* Agent Panel right sidebar */}
      <AgentPanel
        logs={agentLogs}
        route={activeRoute}
        sqlQuery={activeSql}
        retrievedDocs={activeDocs}
      />
    </div>
  );
}
