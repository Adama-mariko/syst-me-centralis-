import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Mouvement {
  id: number;
  type_mouvement: string;
  description: string;
  collaborateur_id?: number;
  entreprise_id?: number;
  placement_id?: number;
  remplacement_id?: number;
  absence_id?: number;
  user_id: number;
  donnees_avant?: string;
  donnees_apres?: string;
  created_at: string;
}

export interface MouvementsResponse {
  mouvements: Mouvement[];
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class MouvementService {
  private apiUrl = '/mouvements';

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) {}

  getMouvements(filters?: {
    collaborateur_id?: number;
    entreprise_id?: number;
    type_mouvement?: string;
    limit?: number;
  }): Observable<MouvementsResponse> {
    let url = this.apiUrl;
    
    if (filters) {
      const params: string[] = [];
      
      if (filters.collaborateur_id) {
        params.push(`collaborateur_id=${filters.collaborateur_id}`);
      }
      if (filters.entreprise_id) {
        params.push(`entreprise_id=${filters.entreprise_id}`);
      }
      if (filters.type_mouvement) {
        params.push(`type_mouvement=${filters.type_mouvement}`);
      }
      if (filters.limit) {
        params.push(`limit=${filters.limit}`);
      }
      
      if (params.length > 0) {
        url += '?' + params.join('&');
      }
    }

    return this.apiService.get<MouvementsResponse>(url);
  }

  getMouvement(id: number): Observable<{ mouvement: Mouvement }> {
    return this.apiService.get<{ mouvement: Mouvement }>(`${this.apiUrl}/${id}`);
  }
}
