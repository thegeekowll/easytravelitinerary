/**
 * Authentication Hooks
 *
 * Custom hooks for authentication-related functionality.
 */

import { useAuth as useAuthContext } from '@/lib/auth/AuthContext';

// Re-export the main useAuth hook
export { useAuthContext as useAuth };

// Export individual auth hooks for convenience
export { useUser, usePermissions, useRoles } from './auth-hooks';
