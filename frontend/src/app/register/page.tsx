'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Activity, ArrowRight, Eye, EyeOff, Lock, Mail, User } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!form.name.trim() || !form.email.includes('@')) return setError('Enter your name and a valid email address.');
    if (form.password.length < 8 || !/[A-Za-z]/.test(form.password) || !/[0-9]/.test(form.password)) return setError('Password must be at least 8 characters and include a letter and a number.');
    if (form.password !== form.confirm) return setError('Passwords do not match.');
    setIsLoading(true);
    try {
      await register(form.email, form.password, form.name);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'We could not create your account.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#070b13] px-4 py-8 text-white">
      <section className="w-full max-w-md rounded-2xl border border-slate-800 bg-[#0c121e] p-8 shadow-2xl">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-lg shadow-blue-500/30"><Activity className="h-6 w-6" /></div>
          <h1 className="mt-4 text-2xl font-bold">Create your Market Pulse</h1>
          <p className="mt-1 text-xs text-slate-400">A calmer way to understand what changed.</p>
        </div>
        {error && <div role="alert" className="mt-5 rounded-xl border border-rose-900/50 bg-rose-950/30 p-3 text-xs text-rose-300">{error}</div>}
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block text-xs font-semibold text-slate-300">Full name<div className="relative mt-1"><User className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input value={form.name} onChange={(e) => update('name', e.target.value)} className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none" /></div></label>
          <label className="block text-xs font-semibold text-slate-300">Email<div className="relative mt-1"><Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input type="email" value={form.email} onChange={(e) => update('email', e.target.value)} className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none" /></div></label>
          <label className="block text-xs font-semibold text-slate-300">Password<div className="relative mt-1"><Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input type={showPassword ? 'text' : 'password'} value={form.password} onChange={(e) => update('password', e.target.value)} className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-10 text-sm focus:border-blue-500 focus:outline-none" /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Hide password' : 'Show password'} className="absolute right-3 top-2.5 text-slate-400">{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></label>
          <label className="block text-xs font-semibold text-slate-300">Confirm password<div className="relative mt-1"><Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input type={showPassword ? 'text' : 'password'} value={form.confirm} onChange={(e) => update('confirm', e.target.value)} className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none" /></div></label>
          <button disabled={isLoading} className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 text-sm font-bold hover:bg-blue-500 disabled:opacity-50">{isLoading ? 'Creating account...' : 'Create account'} <ArrowRight className="h-4 w-4" /></button>
        </form>
        <p className="mt-6 text-center text-xs text-slate-400">Already have an account? <Link href="/login" className="font-semibold text-blue-400 hover:text-blue-300">Sign in</Link></p>
      </section>
    </main>
  );
}
