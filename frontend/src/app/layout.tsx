import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Sidebar from "../components/sidebar";

import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EduAgent AI - College Management System",
  description: "AI-Powered College Multi-Agent Assistant System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex bg-slate-50 text-slate-800 font-sans">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 min-h-screen overflow-y-auto bg-slate-50">
          {children}
        </main>
      </body>
    </html>
  );
}
