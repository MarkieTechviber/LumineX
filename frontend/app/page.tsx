"use client";

import React, { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { Send, Terminal, Search, Code, Brain, Layout, Activity } from 'lucide-react';

export default function LuminexApp() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("agent");
  const [status, setStatus] = useState("Ready");
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:3001');

    socketRef.current.on('token', (data) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
        }
        return [...prev, { role: 'assistant', content: data.content }];
      });
    });

    socketRef.current.on('status', (data) => {
      setStatus(data.content);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', content: input }]);
    socketRef.current?.emit('message', { prompt: input, mode });
    setInput("");
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <div className="w-16 border-r border-slate-800 flex flex-col items-center py-4 gap-6 bg-slate-900/50">
        <div className="text-blue-500 font-bold text-xl mb-4">L</div>
        <ModeIcon icon={<Search size={20} />} active={mode === 'search'} onClick={() => setMode('search')} />
        <ModeIcon icon={<Code size={20} />} active={mode === 'agent'} onClick={() => setMode('agent')} />
        <ModeIcon icon={<Layout size={20} />} active={mode === 'builder'} onClick={() => setMode('builder')} />
        <ModeIcon icon={<Brain size={20} />} active={mode === 'reasoning'} onClick={() => setMode('reasoning')} />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        <header className="h-14 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-950/80 backdrop-blur">
          <div className="flex items-center gap-2">
            <span className="font-semibold capitalize">{mode} Mode</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">{status}</span>
          </div>
          <Activity size={18} className="text-slate-500" />
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
                <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 bg-slate-950">
          <div className="max-w-4xl mx-auto relative">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Ask Luminex anything...`}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 pr-12 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              onClick={handleSend}
              className="absolute right-3 top-3 p-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Artifact Panel (Mock) */}
      <div className="w-96 border-l border-slate-800 bg-slate-900/30 hidden lg:flex flex-col">
        <div className="h-14 border-b border-slate-800 flex items-center px-4 font-medium">Artifacts & Canvas</div>
        <div className="flex-1 p-4 flex items-center justify-center text-slate-500 flex-col gap-2">
          <Layout size={48} className="opacity-20" />
          <p className="text-sm">No artifacts generated yet</p>
        </div>
      </div>
    </div>
  );
}

function ModeIcon({ icon, active, onClick }: { icon: any, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`p-3 rounded-xl transition-all ${active ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
    >
      {icon}
    </button>
  );
}
