export interface Placement {
  id: number;
  collaborateur_id: number;
  entreprise_id: number;
  poste_demande: string;
  description?: string;
  date_debut: string;
  date_fin?: string;
  salaire_propose?: number;
  statut: 'en_attente' | 'confirme' | 'en_cours' | 'termine' | 'annule';
  commentaires?: string;
  validation_rh_date?: string;
  created_at: string;
  updated_at: string;
}