/**
 * Additional Authentication Hooks
 */

import { useMemo } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';

/**
 * Hook to get current user
 */
export const useUser = () => {
  const { user, isLoading } = useAuth();

  return useMemo(
    () => ({
      user,
      isLoading,
      isAdmin: user?.role === 'admin',
      isCSAgent: user?.role === 'cs_agent',
      isPublic: user?.role === 'public',
    }),
    [user, isLoading]
  );
};

/**
 * Hook to check permissions
 */
export const usePermissions = () => {
  const { hasPermission, hasAllPermissions, user } = useAuth();

  return useMemo(
    () => ({
      hasPermission,
      hasAllPermissions,
      permissions: user?.permissions?.map((p) => p.name) || [],
      can: (permission: string) => hasPermission(permission),
      canAll: (permissions: string[]) => hasAllPermissions(permissions),
    }),
    [hasPermission, hasAllPermissions, user]
  );
};

/**
 * Hook to check roles
 */
export const useRoles = () => {
  const { hasRole, hasAnyRole, user } = useAuth();

  return useMemo(
    () => ({
      hasRole,
      hasAnyRole,
      role: user?.role || null,
      is: (role: string) => hasRole(role),
      isAny: (roles: string[]) => hasAnyRole(roles),
    }),
    [hasRole, hasAnyRole, user]
  );
};
