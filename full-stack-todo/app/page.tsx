"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "./../context/AuthContext";
import { ShieldCheck } from "lucide-react";
import Image from "next/image";

export default function Home() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [user, loading, router]);

  if (loading) return null;

  return (
    <div className="min-h-screen flex flex-col bg-[#020617] text-slate-200">
      <main className="grow flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900/40 backdrop-blur-md p-10 rounded-3xl border border-slate-800 shadow-2xl text-center">
          <div className="w-20 bg-indigo-600 rounded-xl p-3 flex items-center justify-center mx-auto mb-6">
            <Image src="/favicon.ico" width={48} height={48} alt="" />
          </div>

          <h1 className="text-4xl font-black text-white tracking-tight mb-2">
            Micro Task AI
          </h1>
          <p className="text-slate-400 font-medium mb-10">
            AI-powered task management for modern teams.
          </p>

          <div className="flex flex-col gap-3">
            <button
              onClick={() => router.push("/auth/signin")}
              className="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-500 transition-all active:scale-95 shadow-lg shadow-indigo-600/20"
            >
              Sign In
            </button>
            <button
              onClick={() => router.push("/auth/signup")}
              className="w-full py-4 bg-slate-800 text-slate-300 font-bold rounded-xl hover:bg-slate-700 transition-all active:scale-95"
            >
              Get Started
            </button>
          </div>
          <div className="mt-8 flex items-center justify-center gap-2 text-slate-600 text-xs font-bold uppercase tracking-widest">
            <ShieldCheck size={14} /> Secure by Better Auth
          </div>
        </div>
      </main>
    </div>
  );
}