export interface Collaborateur {
  id: number;
  numero_employe: string;
  nom: string;
  prenom: string;
  email: string;
  telephone?: string;
  adresse?: string;
  ville?: string;
  code_postal?: string;
  date_naissance?: string;
  date_embauche: string;
  poste: string;
  competences?: string;
  salaire?: number;
  statut: 'actif' | 'inactif' | 'en_conge' | 'arret_maladie';
  entreprise_actuelle_id?: number;
  is_validated_by_rh: boolean;
  validation_date?: string;
  created_at: string;
  updated_at: string;
}