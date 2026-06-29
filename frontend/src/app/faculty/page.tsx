"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Users, Mail, MapPin, Tag } from "lucide-react";
import { api, getSession, UserSession } from "../../lib/api";


export default function FacultyPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [faculty, setFaculty] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    api.getFaculty()
      .then((data) => setFaculty(data))
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
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Faculty Directory</h1>
          <p className="text-slate-500 mt-1">Official listing of university academic professors, instructors, and HODs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {faculty.length === 0 ? (
          <div className="col-span-3 text-center py-12 text-slate-400 bg-white border border-slate-200/80 rounded-3xl">
            No faculty records found in database.
          </div>
        ) : (
          faculty.map((f, idx) => (
            <div key={idx} className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md flex flex-col justify-between hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg">
                    {f.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-800 leading-tight">{f.name}</h3>
                    <p className="text-xs text-indigo-600 font-semibold mt-0.5">{f.designation}</p>
                  </div>
                </div>

                <div className="space-y-2.5 text-xs text-slate-500 font-medium border-t border-slate-100 pt-4 mt-4">
                  <div className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>Department: <span className="text-slate-700 font-bold">{f.department}</span></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-slate-400 shrink-0" />
                    <span className="truncate">{f.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>Office: <span className="text-slate-750 font-bold">{f.office_room}</span></span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
