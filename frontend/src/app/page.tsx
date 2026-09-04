'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

export default function HomePage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      router.replace(user ? '/dashboard' : '/login');
    }
  }, [isLoading, router, user]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#070b13] text-slate-300 text-sm">
      Loading Market Pulse...
    </div>
  );
}
