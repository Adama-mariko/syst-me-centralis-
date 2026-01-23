import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { ApiService } from './api.service';
import { Remplacement } from '../models/remplacement.model';

@Injectable({
  providedIn: 'root'
})
export class RemplacementService {
  constructor(private apiService: ApiService) {}

  getRemplacements(): Observable<{remplacements: Remplacement[]}> {
    // Retourner des données vides pour l'instant
    return of({ remplacements: [] });
  }

  getRemplacement(id: number): Observable<{remplacement: Remplacement}> {
    return this.apiService.get<{remplacement: Remplacement}>(`/remplacements/${id}`);
  }

  createRemplacement(remplacement: Partial<Remplacement>): Observable<{remplacement: Remplacement, message: string}> {
    return this.apiService.post<{remplacement: Remplacement, message: string}>('/remplacements', remplacement);
  }

  updateRemplacement(id: number, remplacement: Partial<Remplacement>): Observable<{remplacement: Remplacement, message: string}> {
    return this.apiService.put<{remplacement: Remplacement, message: string}>(`/remplacements/${id}`, remplacement);
  }

  deleteRemplacement(id: number): Observable<{message: string}> {
    return this.apiService.delete<{message: string}>(`/remplacements/${id}`);
  }
}