import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Entreprise } from '../models/entreprise.model';

@Injectable({
  providedIn: 'root'
})
export class EntrepriseService {
  constructor(private apiService: ApiService) {}

  getEntreprises(): Observable<{entreprises: Entreprise[]}> {
    return this.apiService.get<{entreprises: Entreprise[]}>('/entreprises');
  }

  getEntreprise(id: number): Observable<{entreprise: Entreprise}> {
    return this.apiService.get<{entreprise: Entreprise}>(`/entreprises/${id}`);
  }

  createEntreprise(entreprise: Partial<Entreprise>): Observable<{entreprise: Entreprise, message: string}> {
    return this.apiService.post<{entreprise: Entreprise, message: string}>('/entreprises', entreprise);
  }

  updateEntreprise(id: number, entreprise: Partial<Entreprise>): Observable<{entreprise: Entreprise, message: string}> {
    return this.apiService.put<{entreprise: Entreprise, message: string}>(`/entreprises/${id}`, entreprise);
  }

  deleteEntreprise(id: number): Observable<{message: string}> {
    return this.apiService.delete<{message: string}>(`/entreprises/${id}`);
  }
}