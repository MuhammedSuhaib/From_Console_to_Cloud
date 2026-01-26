#!/bin/bash

# Next.js Clutter Cleanup Script
# Run from project root

echo "🧹 Starting Clutter Cleanup..."

# 1. Remove SVG Logos
if [ -f "public/next.svg" ]; then rm public/next.svg && echo "🗑️ Deleted next.svg"; fi
if [ -f "public/vercel.svg" ]; then rm public/vercel.svg && echo "🗑️ Deleted vercel.svg"; fi

# 2. Remove default favicon
if [ -f "app/favicon.ico" ]; then rm app/favicon.ico && echo "🗑️ Deleted app/favicon.ico"; fi
if [ -f "public/favicon.ico" ]; then rm public/favicon.ico && echo "🗑️ Deleted public/favicon.ico"; fi

# 3. Create a clean entry page
cat <<EOF > app/page.tsx
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold text-center">
        Clean Slate: Ready for Development
      </h1>
    </main>
  );
}
EOF

echo "✅ UI Boilerplate cleaned. Styles preserved."