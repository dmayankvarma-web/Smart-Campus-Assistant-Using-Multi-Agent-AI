"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getSession } from "../lib/api";


export default function IndexPage() {
  const router = useRouter();

  useEffect(() => {
    const session = getSession();
    if (session) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="flex-1 flex items-center justify-center bg-slate-50">
      <div className="w-6 h-6 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
    </div>
  );
}
