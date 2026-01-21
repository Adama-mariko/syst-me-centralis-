import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Placement } from '../models/placement.model';

@Injectable({
  providedIn: 'root'
})
export class PlacementService {
  constructor(private apiService: ApiService) {}

  getPlacements(): Observable<{placements: Placement[]}> {
    return this.apiService.get<{placements: Placement[]}>('/placements');
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

  validatePlacement(id: number): Observable<{placement: Placement, message: string}> {
    return this.apiService.post<{placement: Placement, message: string}>(`/rh/placements/${id}/validate`, {});
  }
}