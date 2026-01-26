import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Absence {
  id?: number;
  collaborateur_id: number;
  collaborateur?: {
    id: number;
    nom: string;
    prenom: string;
    email: string;
  };
  type_absence: string;
  motif?: string;
  date_debut: string;
  date_fin: string;
  nombre_jours: number;
  statut: string;
  commentaires?: string;
  document_justificatif?: string;
  demande_par_collaborateur_id: number;
  demandeur?: {
    id: number;
    nom: string;
    prenom: string;
  };
  approuve_par_user_id?: number;
  approbateur?: {
    id: number;
    nom: string;
    prenom: string;
  };
  date_approbation?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AbsenceResponse {
  absences: Absence[];
  total: number;
  pages: number;
  current_page: number;
}

@Injectable({
  providedIn: 'root'
})
export class AbsenceService {
  private readonly API_URL = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    });
  }

  getAbsences(page: number = 1, perPage: number = 10, filters?: any): Observable<AbsenceResponse> {
    let params: any = { page, per_page: perPage };
    if (filters) {
      params = { ...params, ...filters };
    }
    
    const queryString = new URLSearchParams(params).toString();
    return this.http.get<AbsenceResponse>(`${this.API_URL}/absences?${queryString}`, {
      headers: this.getHeaders()
    });
  }

  getAbsence(id: number): Observable<{ absence: Absence }> {
    return this.http.get<{ absence: Absence }>(`${this.API_URL}/absences/${id}`, {
      headers: this.getHeaders()
    });
  }

  createAbsence(absence: Partial<Absence>): Observable<{ message: string; absence: Absence }> {
    return this.http.post<{ message: string; absence: Absence }>(`${this.API_URL}/absences`, absence, {
      headers: this.getHeaders()
    });
  }

  updateAbsence(id: number, absence: Partial<Absence>): Observable<{ message: string; absence: Absence }> {
    return this.http.put<{ message: string; absence: Absence }>(`${this.API_URL}/absences/${id}`, absence, {
      headers: this.getHeaders()
    });
  }

  approuverAbsence(id: number, commentaires?: string): Observable<{ message: string; absence: Absence }> {
    return this.http.post<{ message: string; absence: Absence }>(`${this.API_URL}/absences/${id}/approuver`, { commentaires }, {
      headers: this.getHeaders()
    });
  }

  refuserAbsence(id: number, commentaires?: string): Observable<{ message: string; absence: Absence }> {
    return this.http.post<{ message: string; absence: Absence }>(`${this.API_URL}/absences/${id}/refuser`, { commentaires }, {
      headers: this.getHeaders()
    });
  }

  deleteAbsence(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.API_URL}/absences/${id}`, {
      headers: this.getHeaders()
    });
  }

  getAbsencesEnAttente(): Observable<{ absences: Absence[] }> {
    return this.http.get<{ absences: Absence[] }>(`${this.API_URL}/absences/en-attente`, {
      headers: this.getHeaders()
    });
  }

  getAbsencesCollaborateur(collaborateurId: number): Observable<{ absences: Absence[] }> {
    return this.http.get<{ absences: Absence[] }>(`${this.API_URL}/collaborateurs/${collaborateurId}/absences`, {
      headers: this.getHeaders()
    });
  }

  getTypesAbsence(): string[] {
    return [
      'conge_paye',
      'conge_sans_solde', 
      'maladie',
      'formation',
      'maternite',
      'paternite',
      'autre'
    ];
  }

  getStatutsAbsence(): string[] {
    return [
      'en_attente',
      'approuve',
      'refuse',
      'annule'
    ];
  }

  getTypeAbsenceLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'conge_paye': 'Congé payé',
      'conge_sans_solde': 'Congé sans solde',
      'maladie': 'Maladie',
      'formation': 'Formation',
      'maternite': 'Maternité',
      'paternite': 'Paternité',
      'autre': 'Autre'
    };
    return labels[type] || type;
  }

  getStatutAbsenceLabel(statut: string): string {
    const labels: { [key: string]: string } = {
      'en_attente': 'En attente',
      'approuve': 'Approuvé',
      'refuse': 'Refusé',
      'annule': 'Annulé'
    };
    return labels[statut] || statut;
  }

  getStatutColor(statut: string): string {
    const colors: { [key: string]: string } = {
      'en_attente': 'warn',
      'approuve': 'primary',
      'refuse': 'accent',
      'annule': 'basic'
    };
    return colors[statut] || 'basic';
  }
}