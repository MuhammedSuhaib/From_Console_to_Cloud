// frontend/full-stack-todo/components/AuthGuard.tsx
import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface AuthGuardProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
  onUnauthenticated?: () => void;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  isAuthenticated, 
  onUnauthenticated 
}) => {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated && pathname !== '/auth/signin' && pathname !== '/auth/signup') {
      // Redirect to sign-in page if not authenticated
      router.push('/auth/signin');
      if (onUnauthenticated) {
        onUnauthenticated();
      }
    }
  }, [isAuthenticated, pathname, router, onUnauthenticated]);

  // If not authenticated and trying to access protected route, return null
  // (the redirect effect would handle navigation)
  if (!isAuthenticated && pathname !== '/auth/signin' && pathname !== '/auth/signup') {
    return null; // or a loading component
  }

  return <>{children}</>;
};

export default AuthGuard;