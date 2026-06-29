"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  CalendarDays, 
  BookOpen, 
  FileText, 
  GraduationCap, 
  CheckCircle,
  Clock,
  MapPin,
  ArrowRight,
  Sparkles,
  School
} from "lucide-react";
import { motion } from "framer-motion";
import { api, getSession, UserSession } from "../../lib/api";



export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    
    api.getStats()
      .then((data) => setStats(data))
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

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="p-8 max-w-6xl w-full mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight bg-gradient-to-r from-slate-800 to-indigo-900 bg-clip-text text-transparent">Welcome back, {session.name}!</h1>
          <p className="text-slate-500 mt-1 font-medium">Here is what's happening in your portal today.</p>
        </div>
        <span className="px-4 py-1.5 rounded-full text-xs font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-100 transition-colors uppercase tracking-wider">
          {session.role}
        </span>
      </div>

      {session.role === "student" && stats && (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {/* Card 1: Attendance */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100/80 text-indigo-600 flex items-center justify-center shrink-0">
              <CalendarDays className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Overall Attendance</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.attendance}%</h3>
              <p className="text-[10px] text-emerald-500 font-bold mt-1">✓ Required: &ge; 75%</p>
            </div>
          </motion.div>

          {/* Card 2: Enrolled Courses */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-100/80 text-emerald-600 flex items-center justify-center shrink-0">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Enrolled Courses</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.enrolled_courses}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Active this semester</p>
            </div>
          </motion.div>

          {/* Card 3: Completed Courses */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100/80 text-blue-600 flex items-center justify-center shrink-0">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Completed Courses</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.completed_courses}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Passed semesters</p>
            </div>
          </motion.div>

          {/* Card 4: Pending Leaves */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-100/80 text-amber-600 flex items-center justify-center shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Pending Leaves</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.pending_leaves}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Awaiting HOD review</p>
            </div>
          </motion.div>
        </motion.div>
      )}

      {session.role === "faculty" && stats && (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {/* Card 1: Courses Taught */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100/80 text-indigo-600 flex items-center justify-center shrink-0">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Courses Taught</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.courses_taught}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Active lectures</p>
            </div>
          </motion.div>

          {/* Card 2: Classroom Bookings */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-100/80 text-emerald-600 flex items-center justify-center shrink-0">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">My Room Bookings</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.classroom_bookings}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Reserved schedules</p>
            </div>
          </motion.div>

          {/* Card 3: Pending Leaves */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-100/80 text-amber-600 flex items-center justify-center shrink-0">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Student Leaves</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.pending_leaves}</h3>
              <p className="text-[10px] text-amber-600 font-bold mt-1">⚠️ Awaiting approval</p>
            </div>
          </motion.div>

          {/* Card 4: Total Classrooms */}
          <motion.div 
            variants={itemVariants} 
            className="bg-white p-6 rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-5"
          >
            <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100/80 text-blue-600 flex items-center justify-center shrink-0">
              <School className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Classrooms</p>
              <h3 className="text-2xl font-bold text-slate-800 mt-1">{stats.total_classrooms}</h3>
              <p className="text-[10px] text-slate-400 mt-1">Managed classrooms</p>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Quick Access Chat Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-8 p-8 rounded-3xl bg-gradient-to-r from-indigo-600 to-violet-700 text-white shadow-xl shadow-indigo-150 flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
      >
        <div className="max-w-md">
          <div className="flex items-center gap-2 mb-3 bg-white/10 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider w-fit">
            <Sparkles className="w-3.5 h-3.5 fill-white/10" />
            <span>AI powered Agent</span>
          </div>
          <h2 className="text-2xl font-bold">Ask the College Assistant</h2>
          <p className="text-indigo-100 text-sm mt-1.5 leading-relaxed">
            Need information about exam structures, attendance requirements, bus schedules, or database reports? Converse directly with our multi-agent assistant system.
          </p>
        </div>
        <button
          onClick={() => router.push("/chat")}
          className="shrink-0 flex items-center gap-2 bg-white text-indigo-700 px-6 py-3.5 rounded-2xl font-bold text-sm shadow-md hover:bg-indigo-50 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
        >
          <span>Open Chat Assistant</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </motion.div>
    </div>
  );
}
