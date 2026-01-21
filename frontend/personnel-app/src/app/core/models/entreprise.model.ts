export interface Entreprise {
  id: number;
  nom: string;
  siret: string;
  adresse: string;
  ville: string;
  code_postal: string;
  telephone?: string;
  email?: string;
  contact_rh_nom?: string;
  contact_rh_email?: string;
  contact_rh_telephone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}