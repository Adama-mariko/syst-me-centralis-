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
    return this.apiService.get<{remplacements: Remplacement[]}>('/remplacements');
  }

  getRemplacement(id: number): Observable<{remplacement: Remplacement}> {
    return this.apiService.get<{remplacement: Remplacement}>(`/remplacements/${id}`);
  }

  createRemplacement(remplacement: Partial<Remplacement>): Observable<{remplacement: Remplacement, message: string}> {
    console.log('[DEBUG] Service createRemplacement appelé avec:', remplacement);
    return this.apiService.post<{remplacement: Remplacement, message: string}>('/remplacements', remplacement);
  }

  updateRemplacement(id: number, remplacement: Partial<Remplacement>): Observable<{remplacement: Remplacement, message: string}> {
    return this.apiService.put<{remplacement: Remplacement, message: string}>(`/remplacements/${id}`, remplacement);
  }

  deleteRemplacement(id: number): Observable<{message: string}> {
    return this.apiService.delete<{message: string}>(`/remplacements/${id}`);
  }
}