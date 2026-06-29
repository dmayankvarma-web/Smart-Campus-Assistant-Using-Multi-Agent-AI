"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BookOpen, Award, CheckCircle2 } from "lucide-react";
import { api, getSession, UserSession } from "../../lib/api";


export default function CoursesPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    api.getCourses()
      .then((data) => setCourses(data))
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
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Courses Catalog</h1>
          <p className="text-slate-500 mt-1">
            {session.role === "student" ? "Your registered, completed, and pending course history." : "Courses you are currently instructing."}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {courses.length === 0 ? (
          <div className="col-span-2 text-center py-12 text-slate-400 bg-white border border-slate-200/80 rounded-3xl">
            No course records found in database.
          </div>
        ) : (
          courses.map((c, idx) => (
            <div key={idx} className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md flex flex-col justify-between hover:shadow-lg transition-all duration-200">
              <div>
                <div className="flex justify-between items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  {session.role === "student" && (
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      c.status === "completed"
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                        : "bg-indigo-50 text-indigo-700 border border-indigo-100"
                    }`}>
                      {c.status === "completed" ? <CheckCircle2 className="w-3 h-3" /> : <Award className="w-3 h-3" />}
                      <span>{c.status}</span>
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-slate-800 leading-tight">{c.course_name}</h3>
                <p className="text-xs font-mono font-bold text-slate-400 mt-1 uppercase tracking-wider">{c.course_code}</p>
                <div className="mt-4 flex flex-col gap-1.5 text-xs text-slate-500 font-medium">
                  <p>Credits: <span className="text-slate-800 font-bold">{c.credits}</span></p>
                  {session.role === "student" && <p>Instructor: <span className="text-slate-800 font-bold">{c.instructor}</span></p>}
                  {session.role === "faculty" && <p>Department: <span className="text-slate-800 font-bold">{c.department}</span></p>}
                </div>
              </div>
              
              {session.role === "student" && c.grade && (
                <div className="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-bold uppercase tracking-wider">Final Grade</span>
                  <span className="text-base font-extrabold text-emerald-600 bg-emerald-50 border border-emerald-100 px-3 py-1 rounded-xl">
                    {c.grade}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
