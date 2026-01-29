'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
    </div>
  );
}

export function SmallSpinner() {
  return (
    <div className="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-indigo-500 align-middle"></div>
  );
}
