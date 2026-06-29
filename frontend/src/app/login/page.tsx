"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { School, ArrowRight, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../../lib/api";



export default function LoginPage() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.login(userId, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to log in.");
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (demoId: string) => {
    setUserId(demoId);
    setPassword("password123");
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 px-4 min-h-screen">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-white p-8 rounded-3xl border border-slate-200/80 shadow-xl shadow-slate-100 flex flex-col"
      >
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-4 shadow-sm border border-indigo-100">
            <School className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">EduAgent AI</h2>
          <p className="text-sm text-slate-500 mt-1">College Management Multi-Agent Assistant</p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-100 flex gap-3 text-sm text-red-700"
          >
            <ShieldAlert className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">User ID</label>
            <input
              type="text"
              required
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="e.g. 192125022 or F101"
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all duration-200"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all duration-200"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 flex items-center justify-center gap-2 py-3.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-semibold text-sm shadow-lg shadow-indigo-150 transition-all duration-200 disabled:opacity-75 disabled:cursor-not-allowed"
          >
            {loading ? "Authenticating..." : "Sign In"}
            {!loading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div className="mt-8 border-t border-slate-100 pt-6">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 text-center">Demo Credentials</p>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => handleFillDemo("192125022")}
              className="p-3 text-left rounded-2xl border border-slate-150 hover:bg-slate-50 transition-all duration-200"
            >
              <p className="text-xs font-bold text-slate-700">Student Account</p>
              <p className="text-[10px] text-slate-400 mt-0.5">ID: 192125022 / Pass: password123</p>
            </button>
            <button
              onClick={() => handleFillDemo("F101")}
              className="p-3 text-left rounded-2xl border border-slate-150 hover:bg-slate-50 transition-all duration-200"
            >
              <p className="text-xs font-bold text-slate-700">Faculty Account</p>
              <p className="text-[10px] text-slate-400 mt-0.5">ID: F101 / Pass: password123</p>
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
