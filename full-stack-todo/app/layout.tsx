import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from './../context/AuthContext';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    template: '%s | Micro Task AI',
    default: 'Micro Task AI - AI-Powered Task Management',
  },
  description: 'AI-powered task management application with intelligent automation and seamless collaboration for modern teams.',
  keywords: ['task management', 'AI productivity', 'todo app', 'team collaboration', 'artificial intelligence'],
  authors: [{ name: 'Micro Task AI Team' }],
  creator: 'Micro Task AI',
  publisher: 'Micro Task AI',
  openGraph: {
    title: 'Micro Task AI - AI-Powered Task Management',
    description: 'AI-powered task management application with intelligent automation and seamless collaboration for modern teams.',
    url: 'https://microtask-ai.example.com',
    siteName: 'Micro Task AI',
    images: [
      {
        url: 'https://microtask-ai.example.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Micro Task AI - AI-Powered Task Management Dashboard',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Micro Task AI - AI-Powered Task Management',
    description: 'AI-powered task management application with intelligent automation and seamless collaboration for modern teams.',
  },
  alternates: {
    canonical: 'https://microtask-ai.example.com',
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning={true}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased `}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
