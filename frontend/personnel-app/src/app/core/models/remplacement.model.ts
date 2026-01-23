export interface Remplacement {
  id: number;
  collaborateur_remplacant_id: number;
  collaborateur_remplace_id: number;
  entreprise_id: number;
  motif: string;
  date_debut: string;
  date_fin: string;
  statut: 'planifie' | 'en_cours' | 'termine' | 'annule';
  notes?: string;
  created_at: string;
  updated_at: string;
}