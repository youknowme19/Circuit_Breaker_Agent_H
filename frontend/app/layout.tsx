import './globals.css';
import type { Metadata } from 'next';
import { IBM_Plex_Sans, IBM_Plex_Mono } from 'next/font/google';

const sans = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-sans',
});

const mono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'Circuit Breaker — The agent can be fooled. The money doesn’t have to be.',
  description:
    'Deterministic authorization layer between AI agents and financial execution. AI proposes. Circuit Breaker authorizes. Only the execution gate can move money.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${sans.variable} ${mono.variable}`}>
      <body className={`${sans.className} min-h-screen bg-[#07080c] text-slate-100 antialiased`}>{children}</body>
    </html>
  );
}
