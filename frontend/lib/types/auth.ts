/**
 * Authentication type definitions
 */

export interface User {
  id: string; // UUID from backend
  email: string;
  full_name: string;
  role: string; // Enum value as string
  is_active: boolean;
  profile_photo_url?: string;
  phone_number?: string;
  address?: string;
  date_of_birth?: string;
  position?: string;
  agent_type?: string;
  created_at: string;
  updated_at: string;
  permissions: Permission[]; // Top level
}

export interface Role {
  id: number;
  name: string;
  description: string;
  permissions: Permission[];
}

export interface Permission {
  id: string; // UUID
  name: string;
  description: string;
  category: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
}
