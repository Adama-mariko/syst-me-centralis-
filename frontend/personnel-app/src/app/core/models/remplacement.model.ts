export interface Remplacement {
  id: number;
  remplacant_id: number;
  remplace_id: number;
  type_remplacement: 'temporaire' | 'permanent' | 'urgence';
  motif?: string;
  date_debut: string;
  date_fin: string;
  statut: 'planifie' | 'en_cours' | 'termine' | 'annule';
  commentaires?: string;
  created_at: string;
  updated_at: string;
  // Relations
  remplacant?: any;
  remplace?: any;
  created_by?: any;
}