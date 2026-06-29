"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarDays, AlertTriangle, CheckCircle } from "lucide-react";
import { api, getSession, UserSession } from "../../lib/api";


export default function AttendancePage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    api.getAttendance()
      .then((data) => setRecords(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading || !session) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="w-6 h-6 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl w-full mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Attendance Logs</h1>
          <p className="text-slate-500 mt-1">Detailed database record of class registrations and attendance logs.</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-md overflow-hidden">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-400 uppercase tracking-wider">
              {session.role === "faculty" && <th className="px-6 py-4">Student ID</th>}
              <th className="px-6 py-4">Course Code</th>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm font-medium text-slate-700">
            {records.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                  No attendance records found in database.
                </td>
              </tr>
            ) : (
              records.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                  {session.role === "faculty" && <td className="px-6 py-4 font-mono text-xs">{r.student_id}</td>}
                  <td className="px-6 py-4">{r.course_code}</td>
                  <td className="px-6 py-4">{r.date}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                      r.status === "present"
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                        : "bg-red-50 text-red-700 border border-red-100"
                    }`}>
                      {r.status === "present" ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                      <span className="capitalize">{r.status}</span>
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
