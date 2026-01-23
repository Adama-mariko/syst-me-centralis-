export interface Placement {
  id: number;
  collaborateur_id: number;
  entreprise_id: number;
  poste: string;
  date_debut: string;
  date_fin?: string;
  salaire: number;
  statut: 'en_attente' | 'en_cours' | 'termine' | 'annule';
  description?: string;
  conditions?: string;
  created_at: string;
  updated_at: string;
}