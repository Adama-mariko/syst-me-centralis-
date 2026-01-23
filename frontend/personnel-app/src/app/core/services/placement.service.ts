import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { ApiService } from './api.service';
import { Placement } from '../models/placement.model';

@Injectable({
  providedIn: 'root'
})
export class PlacementService {
  constructor(private apiService: ApiService) {}

  getPlacements(): Observable<{placements: Placement[]}> {
    // Retourner des données vides pour l'instant
    return of({ placements: [] });
  }

  getPlacement(id: number): Observable<{placement: Placement}> {
    return this.apiService.get<{placement: Placement}>(`/placements/${id}`);
  }

  createPlacement(placement: Partial<Placement>): Observable<{placement: Placement, message: string}> {
    return this.apiService.post<{placement: Placement, message: string}>('/placements', placement);
  }

  updatePlacement(id: number, placement: Partial<Placement>): Observable<{placement: Placement, message: string}> {
    return this.apiService.put<{placement: Placement, message: string}>(`/placements/${id}`, placement);
  }

  deletePlacement(id: number): Observable<{message: string}> {
    return this.apiService.delete<{message: string}>(`/placements/${id}`);
  }
}