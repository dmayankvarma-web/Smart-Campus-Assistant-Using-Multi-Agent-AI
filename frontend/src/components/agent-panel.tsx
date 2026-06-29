"use client";

import { CheckCircle2, AlertTriangle, Play, HelpCircle, FileText } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface AgentLog {
  agent: string;
  status: string;
  message: string;
}

interface AgentPanelProps {
  logs: AgentLog[];
  route?: string;
  sqlQuery?: string | null;
  retrievedDocs?: any[];
}

export default function AgentPanel({ logs, route, sqlQuery, retrievedDocs }: AgentPanelProps) {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case "blocked":
      case "failed":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case "in progress":
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          >
            <Play className="w-5 h-5 text-indigo-500 fill-indigo-50" />
          </motion.div>
        );
      default:
        return <HelpCircle className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="w-80 bg-white border-l border-slate-200 p-6 flex flex-col shrink-0 overflow-y-auto">
      <div className="flex items-center gap-2 mb-6">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
        <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">Agent Activity (Live)</h3>
      </div>

      {logs.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-center p-4">
          <Play className="w-8 h-8 mb-2 stroke-[1.5]" />
          <p className="text-sm font-medium">Waiting for query...</p>
        </div>
      ) : (
        <div className="space-y-6 flex-1">
          <AnimatePresence initial={false}>
            {logs.map((log, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="flex gap-4"
              >
                <div className="shrink-0 mt-0.5">{getStatusIcon(log.status)}</div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-slate-800 leading-tight">
                    {log.agent}
                  </h4>
                  <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold uppercase mt-1 ${
                    log.status.toLowerCase() === "completed"
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                      : log.status.toLowerCase() === "blocked" || log.status.toLowerCase() === "failed"
                      ? "bg-red-50 text-red-700 border border-red-100"
                      : "bg-indigo-50 text-indigo-700 border border-indigo-100"
                  }`}>
                    {log.status}
                  </span>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed break-words">
                    {log.message}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Conditional detailed views */}
          {route === "sql" && sqlQuery && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200"
            >
              <h5 className="text-xs font-bold text-slate-700 mb-2 uppercase tracking-wide">Generated SQL</h5>
              <pre className="text-[10px] font-mono text-indigo-700 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {sqlQuery}
              </pre>
            </motion.div>
          )}

          {route === "rag" && retrievedDocs && retrievedDocs.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-6 space-y-3"
            >
              <h5 className="text-xs font-bold text-slate-700 uppercase tracking-wide">Retrieved Citations</h5>
              {retrievedDocs.map((doc, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-600 mb-1">
                    <FileText className="w-3.5 h-3.5" />
                    <span>{doc.source}</span>
                  </div>
                  <p className="text-slate-500 leading-relaxed italic">
                    "{doc.content.length > 120 ? `${doc.content.substring(0, 120)}...` : doc.content}"
                  </p>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
