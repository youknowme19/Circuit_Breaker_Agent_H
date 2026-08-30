'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SecurityRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/console');
  }, [router]);
  return <p className="p-8 text-slate-400">Redirecting to security console…</p>;
}
