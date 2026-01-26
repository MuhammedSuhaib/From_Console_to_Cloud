'use client';
import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { createAuthClient } from 'better-auth/client';
import { User, Mail, Lock, Loader2 } from 'lucide-react';

const auth = createAuthClient({ baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000' });

export default function SignUpPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await auth.signUp.email({ email, password, name });
      if (res.error) { setError(res.error.message ?? 'Signup failed'); setLoading(false); return; }
      if (res.data?.token) {
        localStorage.setItem('auth_token', res.data.token);
        window.location.replace('/dashboard');
      }
    } catch (err) { setLoading(false); setError("System error. Try again."); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] px-6">
      <div className="max-w-sm w-full space-y-8 bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-10">
       <h2 className="text-3xl font-black text-indigo-400 text-center">Micro Task AI</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {error && <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-xl text-xs font-bold text-center">{error}</div>}
          <div className="relative">
            <User className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="text" required placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <div className="relative">
            <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <button type="submit" disabled={loading} className="w-full py-4 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-500 transition-all disabled:opacity-50 flex justify-center items-center gap-2">
            {loading ? <Loader2 className="animate-spin" size={20} /> : "Create Account"}
          </button>
        </form>
        <p className="text-center text-sm text-slate-500 font-medium">Already in? <Link href="/auth/signin" className="text-indigo-400 font-bold">Sign in</Link></p>
      </div>
    </div>
  );
}