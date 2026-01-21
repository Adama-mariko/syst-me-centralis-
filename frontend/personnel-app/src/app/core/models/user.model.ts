export interface User {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  role: 'admin' | 'rh_entreprise';
  entreprise_id?: number;
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}