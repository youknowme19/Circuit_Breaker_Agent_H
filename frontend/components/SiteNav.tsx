'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, Shield, X } from 'lucide-react';

const links = [
  { href: '/', label: 'Overview' },
  { href: '/agent', label: 'Agent' },
  { href: '/transfer', label: 'Live Transfer' },
  { href: '/attacks', label: 'Attack Lab' },
  { href: '/agent/tools', label: 'Tools' },
  { href: '/wallet', label: 'Wallet' },
  { href: '/audit', label: 'Audit' },
  { href: '/demo', label: 'Demo' },
];




export default function SiteNav({ compact = false }: { compact?: boolean }) {
  const path = usePathname();
  const [open, setOpen] = useState(false);

  const itemClass = (href: string) =>
    `focus-ring block rounded-md px-3 py-1.5 text-xs font-semibold ${
      path === href ? 'bg-orange-500/20 text-orange-200' : 'text-slate-400 hover:text-white'
    }`;

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#07080c]/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="focus-ring flex items-center gap-2 rounded-md">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-orange-500/40 bg-orange-500/10 text-orange-400">
            <Shield className="h-5 w-5" aria-hidden />
          </span>
          <span>
            <span className="block text-sm font-bold tracking-wide text-white">CIRCUIT BREAKER</span>
            {!compact && (
              <span className="block font-mono text-[10px] text-orange-300/80">authorization control plane</span>
            )}
          </span>
        </Link>
        <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className={itemClass(l.href)}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Link
            href="/console"
            className="focus-ring rounded-md bg-orange-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-orange-500"
          >
            Launch Console
          </Link>
          <button
            type="button"
            className="focus-ring rounded-md border border-white/15 p-2 text-slate-200 md:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? 'Close menu' : 'Open menu'}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>
      {open && (
        <nav id="mobile-nav" aria-label="Mobile" className="border-t border-white/10 px-4 py-3 md:hidden">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className={`${itemClass(l.href)} py-2`} onClick={() => setOpen(false)}>
              {l.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
