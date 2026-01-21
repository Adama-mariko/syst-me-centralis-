import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Collaborateur } from '../models/collaborateur.model';

@Injectable({
  providedIn: 'root'
})
export class CollaborateurService {
  constructor(private apiService: ApiService) {}

  getCollaborateurs(): Observable<{collaborateurs: Collaborateur[]}> {
    return this.apiService.get<{collaborateurs: Collaborateur[]}>('/collaborateurs');
  }

  getCollaborateur(id: number): Observable<{collaborateur: Collaborateur}> {
    return this.apiService.get<{collaborateur: Collaborateur}>(`/collaborateurs/${id}`);
  }

  createCollaborateur(collaborateur: Partial<Collaborateur>): Observable<{collaborateur: Collaborateur, message: string}> {
    return this.apiService.post<{collaborateur: Collaborateur, message: string}>('/collaborateurs', collaborateur);
  }

  updateCollaborateur(id: number, collaborateur: Partial<Collaborateur>): Observable<{collaborateur: Collaborateur, message: string}> {
    return this.apiService.put<{collaborateur: Collaborateur, message: string}>(`/collaborateurs/${id}`, collaborateur);
  }

  deleteCollaborateur(id: number): Observable<{message: string}> {
    return this.apiService.delete<{message: string}>(`/collaborateurs/${id}`);
  }

  validateCollaborateur(id: number): Observable<{collaborateur: Collaborateur, message: string}> {
    return this.apiService.post<{collaborateur: Collaborateur, message: string}>(`/rh/collaborateurs/${id}/validate`, {});
  }
}