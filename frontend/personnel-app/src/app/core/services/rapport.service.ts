import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Rapport {
  id?: number;
  type_rapport: string;
  titre: string;
  description?: string;
  periode_debut: string;
  periode_fin: string;
  entreprise_id?: number;
  entreprise?: {
    id: number;
    nom: string;
  };
  ville?: string;
  statut: string;
  fichier_path?: string;
  donnees_json?: string;
  genere_par_user_id: number;
  generateur?: {
    id: number;
    nom: string;
    prenom: string;
  };
  created_at?: string;
  updated_at?: string;
}

export interface RapportResponse {
  rapports: Rapport[];
  total: number;
  pages: number;
  current_page: number;
}

export interface Statistiques {
  total_collaborateurs: number;
  total_entreprises: number;
  total_placements: number;
  total_absences: number;
  placements_actifs: number;
  absences_en_attente: number;
  evolution_mensuelle: {
    mois: string;
    placements: number;
    absences: number;
  }[];
}

@Injectable({
  providedIn: 'root'
})
export class RapportService {
  private readonly API_URL = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    });
  }

  getRapports(page: number = 1, perPage: number = 10, filters?: any): Observable<RapportResponse> {
    let params: any = { page, per_page: perPage };
    if (filters) {
      params = { ...params, ...filters };
    }
    
    const queryString = new URLSearchParams(params).toString();
    return this.http.get<RapportResponse>(`${this.API_URL}/rapports?${queryString}`, {
      headers: this.getHeaders()
    });
  }

  getRapport(id: number): Observable<{ rapport: Rapport }> {
    return this.http.get<{ rapport: Rapport }>(`${this.API_URL}/rapports/${id}`, {
      headers: this.getHeaders()
    });
  }

  genererRapportPlacements(data: {
    periode_debut: string;
    periode_fin: string;
    entreprise_id?: number;
    ville?: string;
  }): Observable<{ message: string; rapport: Rapport }> {
    return this.http.post<{ message: string; rapport: Rapport }>(`${this.API_URL}/rapports/placements`, data, {
      headers: this.getHeaders()
    });
  }

  genererRapportAbsences(data: {
    periode_debut: string;
    periode_fin: string;
    entreprise_id?: number;
  }): Observable<{ message: string; rapport: Rapport }> {
    return this.http.post<{ message: string; rapport: Rapport }>(`${this.API_URL}/rapports/absences`, data, {
      headers: this.getHeaders()
    });
  }

  exporterRapportCSV(id: number): Observable<Blob> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      ...(token && { Authorization: `Bearer ${token}` })
    });
    
    return this.http.get(`${this.API_URL}/rapports/${id}/export/csv`, {
      headers: headers,
      responseType: 'blob'
    });
  }

  getMesRapports(): Observable<{ rapports: Rapport[] }> {
    return this.http.get<{ rapports: Rapport[] }>(`${this.API_URL}/rapports/mes-rapports`, {
      headers: this.getHeaders()
    });
  }

  getStatistiquesGlobales(): Observable<{ statistiques: Statistiques }> {
    return this.http.get<{ statistiques: Statistiques }>(`${this.API_URL}/rapports/statistiques`, {
      headers: this.getHeaders()
    });
  }

  getTypesRapport(): string[] {
    return [
      'mensuel_placements',
      'mensuel_absences',
      'mensuel_remplacements',
      'annuel_global',
      'personnalise'
    ];
  }

  getTypeRapportLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'mensuel_placements': 'Rapport mensuel des placements',
      'mensuel_absences': 'Rapport mensuel des absences',
      'mensuel_remplacements': 'Rapport mensuel des remplacements',
      'annuel_global': 'Rapport annuel global',
      'personnalise': 'Rapport personnalisé'
    };
    return labels[type] || type;
  }

  getStatutRapportLabel(statut: string): string {
    const labels: { [key: string]: string } = {
      'en_cours': 'En cours',
      'genere': 'Généré',
      'erreur': 'Erreur'
    };
    return labels[statut] || statut;
  }

  getStatutColor(statut: string): string {
    const colors: { [key: string]: string } = {
      'en_cours': 'warn',
      'genere': 'primary',
      'erreur': 'accent'
    };
    return colors[statut] || 'basic';
  }

  downloadCSV(rapport: Rapport): void {
    this.exporterRapportCSV(rapport.id!).subscribe(blob => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `rapport_${rapport.id}_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    });
  }
}