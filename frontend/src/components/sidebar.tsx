"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { 
  LayoutDashboard, 
  MessageSquare, 
  CalendarDays, 
  BookOpen, 
  FileText, 
  Users, 
  School, 
  LogOut 
} from "lucide-react";
import { getSession, clearSession, UserSession } from "../lib/api";


export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);

  useEffect(() => {
    const activeSession = getSession();
    if (!activeSession && pathname !== "/login") {
      router.push("/login");
    } else {
      setSession(activeSession);
    }
  }, [pathname, router]);

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

  if (pathname === "/login") return null;

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Chat Assistant", href: "/chat", icon: MessageSquare },
    { name: "Attendance", href: "/attendance", icon: CalendarDays },
    { name: "Courses", href: "/courses", icon: BookOpen },
    { name: "Leave Requests", href: "/leaves", icon: FileText },
    { name: "Faculty Info", href: "/faculty", icon: Users },
    { name: "Classrooms", href: "/classrooms", icon: School },
  ];

  return (
    <aside className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col shrink-0">
      <div className="p-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-xl text-indigo-600">
          <School className="w-6 h-6" />
          <span>EduAgent AI</span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-100"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {session && (
        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 px-2 py-3 rounded-xl bg-white border border-slate-100 shadow-sm">
            <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-base shrink-0">
              {session.name.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-slate-800 truncate leading-none mb-1">
                {session.name}
              </p>
              <p className="text-xs text-slate-400 font-medium truncate uppercase tracking-wider mb-1">
                {session.role}
              </p>
              <p className="text-[10px] text-slate-400 truncate">
                ID: {session.userId}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 hover:border-red-100 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      )}
    </aside>
  );
}
