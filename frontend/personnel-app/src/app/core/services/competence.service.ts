import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Competence {
  id?: number;
  nom: string;
  description?: string;
  categorie?: string;
  niveau_requis: string;
  is_active: boolean;
  created_at?: string;
}

export interface CollaborateurCompetence {
  id?: number;
  collaborateur_id: number;
  competence_id: number;
  competence?: Competence;
  niveau: string;
  certifie: boolean;
  date_acquisition?: string;
  created_at?: string;
}

export interface CompetenceResponse {
  competences: Competence[];
  total: number;
  pages: number;
  current_page: number;
}

@Injectable({
  providedIn: 'root'
})
export class CompetenceService {
  private readonly API_URL = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    });
  }

  getCompetences(page: number = 1, perPage: number = 50, filters?: any): Observable<CompetenceResponse> {
    let params: any = { page, per_page: perPage };
    if (filters) {
      params = { ...params, ...filters };
    }
    
    const queryString = new URLSearchParams(params).toString();
    return this.http.get<CompetenceResponse>(`${this.API_URL}/competences?${queryString}`, {
      headers: this.getHeaders()
    });
  }

  createCompetence(competence: Partial<Competence>): Observable<{ message: string; competence: Competence }> {
    return this.http.post<{ message: string; competence: Competence }>(`${this.API_URL}/competences`, competence, {
      headers: this.getHeaders()
    });
  }

  updateCompetence(id: number, competence: Partial<Competence>): Observable<{ message: string; competence: Competence }> {
    return this.http.put<{ message: string; competence: Competence }>(`${this.API_URL}/competences/${id}`, competence, {
      headers: this.getHeaders()
    });
  }

  getCategories(): Observable<{ categories: string[] }> {
    return this.http.get<{ categories: string[] }>(`${this.API_URL}/competences/categories`, {
      headers: this.getHeaders()
    });
  }

  getCompetencesCollaborateur(collaborateurId: number): Observable<{ competences: CollaborateurCompetence[] }> {
    return this.http.get<{ competences: CollaborateurCompetence[] }>(`${this.API_URL}/collaborateurs/${collaborateurId}/competences`, {
      headers: this.getHeaders()
    });
  }

  addCompetenceCollaborateur(collaborateurId: number, data: {
    competence_id: number;
    niveau: string;
    certifie?: boolean;
    date_acquisition?: string;
  }): Observable<{ message: string; competence: CollaborateurCompetence }> {
    return this.http.post<{ message: string; competence: CollaborateurCompetence }>(`${this.API_URL}/collaborateurs/${collaborateurId}/competences`, data, {
      headers: this.getHeaders()
    });
  }

  importCollaborateursCSV(file: File): Observable<{
    message: string;
    collaborateurs_crees: number;
    erreurs: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      ...(token && { Authorization: `Bearer ${token}` })
    });
    
    return this.http.post<{
      message: string;
      collaborateurs_crees: number;
      erreurs: string[];
    }>(`${this.API_URL}/collaborateurs/import-csv`, formData, {
      headers: headers
    });
  }

  getNiveauxCompetence(): string[] {
    return ['debutant', 'intermediaire', 'avance', 'expert'];
  }

  getNiveauCompetenceLabel(niveau: string): string {
    const labels: { [key: string]: string } = {
      'debutant': 'Débutant',
      'intermediaire': 'Intermédiaire',
      'avance': 'Avancé',
      'expert': 'Expert'
    };
    return labels[niveau] || niveau;
  }

  getNiveauColor(niveau: string): string {
    const colors: { [key: string]: string } = {
      'debutant': 'basic',
      'intermediaire': 'primary',
      'avance': 'accent',
      'expert': 'warn'
    };
    return colors[niveau] || 'basic';
  }

  generateCSVTemplate(): string {
    const headers = [
      'nom',
      'prenom', 
      'email',
      'poste',
      'date_embauche',
      'telephone',
      'adresse',
      'ville',
      'code_postal',
      'salaire',
      'competences'
    ];
    
    const example = [
      'Dupont',
      'Jean',
      'jean.dupont@email.com',
      'Développeur',
      '2024-01-15',
      '0123456789',
      '123 Rue de la Paix',
      'Paris',
      '75001',
      '3500',
      'JavaScript,Python,SQL'
    ];
    
    return [headers.join(','), example.join(',')].join('\n');
  }

  downloadCSVTemplate(): void {
    const csvContent = this.generateCSVTemplate();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'template_import_collaborateurs.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}