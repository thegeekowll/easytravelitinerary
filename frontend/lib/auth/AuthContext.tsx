'use client';

/**
 * Authentication Context Provider
 *
 * Provides authentication state and methods throughout the application.
 * Handles login, logout, registration, and user state management.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api/client';
import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthContextType,
} from '@/lib/types/auth';

// ==================== Context Creation ====================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ==================== Auth Provider ====================

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // ==================== Initialize Auth State ====================

  useEffect(() => {
    const initializeAuth = async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Fetch current user
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
        
        // Sync cookie for middleware
        if (typeof window !== 'undefined') {
          // Set cookie to match token expiry (approx) or session
          document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Lax`; 
        }
      } catch (error) {
        // Token is invalid, clear it
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          document.cookie = 'auth_token=; path=/; max-age=0;';
        }
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // ==================== Login ====================

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setIsLoading(true);

        const response = await apiClient.login(credentials.email, credentials.password);

        // Store token
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user || {}));
          document.cookie = `auth_token=${response.access_token}; path=/; max-age=86400; SameSite=Lax`;
        }

        // Set user state
        setUser(response.user || null);

        // Show success message
        toast.success(`Welcome back!`);

        // Redirect to dashboard
        router.push('/dashboard');
      } catch (error: any) {
        // Error is already handled by API client
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  // ==================== Register ====================

  const register = useCallback(
    async (_data: RegisterData) => {
      try {
        setIsLoading(true);

        // Registration is admin-only, so this won't be called
        throw new Error('Registration is only available to administrators');
      } catch (error: any) {
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  // ==================== Logout ====================

  const logout = useCallback(async () => {
    try {
      // No logout endpoint, just clear local storage
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens and user state
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        document.cookie = 'auth_token=; path=/; max-age=0;';
      }
      setUser(null);

      // Show message
      toast.success('You have been logged out');

      // Redirect to login
      router.push('/auth/login');
    }
  }, [router]);

  // ==================== Refresh User ====================

  const refreshUser = useCallback(async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // If refresh fails, logout
      await logout();
    }
  }, [logout]);

  // ==================== Permission Helpers ====================

  const hasRole = useCallback(
    (role: string): boolean => {
      if (!user) return false;
      return user.role === role;
    },
    [user]
  );

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;
      // Admin has all permissions
      if (user.role === 'admin') return true;
      return user.permissions?.some((p) => p.name === permission) ?? false;
    },
    [user]
  );

  const hasAnyRole = useCallback(
    (roles: string[]): boolean => {
      if (!user) return false;
      return roles.includes(user.role);
    },
    [user]
  );

  const hasAllPermissions = useCallback(
    (permissions: string[]): boolean => {
      if (!user) return false;
      if (user.role === 'admin') return true;
      
      const userPermissions = user.permissions?.map((p) => p.name) ?? [];
      return permissions.every((p) => userPermissions.includes(p));
    },
    [user]
  );

  // ==================== Context Value ====================

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
    hasRole,
    hasPermission,
    hasAnyRole,
    hasAllPermissions,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// ==================== useAuth Hook ====================

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// ==================== Protected Route HOC ====================

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredRoles?: string[];
  requiredPermission?: string;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredRoles,
  requiredPermission,
  requiredPermissions,
  fallback,
}) => {
  const { isAuthenticated, isLoading, hasRole, hasAnyRole, hasPermission, hasAllPermissions } =
    useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  // Check role requirements
  if (requiredRole && !hasRole(requiredRole)) {
    return fallback || <div>Access Denied</div>;
  }

  if (requiredRoles && !hasAnyRole(requiredRoles)) {
    return fallback || <div>Access Denied</div>;
  }

  // Check permission requirements
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return fallback || <div>Access Denied</div>;
  }

  if (requiredPermissions && !hasAllPermissions(requiredPermissions)) {
    return fallback || <div>Access Denied</div>;
  }

  return <>{children}</>;
};

// ==================== Role-Based Route Components ====================

export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <ProtectedRoute requiredRole="admin">{children}</ProtectedRoute>;
};

export const CSAgentRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <ProtectedRoute requiredRoles={['admin', 'cs_agent']}>{children}</ProtectedRoute>;
};

export const AuthenticatedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <ProtectedRoute>{children}</ProtectedRoute>;
};
