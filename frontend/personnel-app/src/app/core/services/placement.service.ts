import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ApiService } from './api.service';
import { Placement } from '../models/placement.model';

@Injectable({
  providedIn: 'root'
})
export class PlacementService {
  private readonly API_URL = 'http://localhost:5000/api';

  constructor(
    private apiService: ApiService,
    private http: HttpClient
  ) {}

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
    return this.apiService.put<{placement: Placement, message: string}>(`/placements/${id}/validate`, {});
  }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      ...(token && { Authorization: `Bearer ${token}` })
    });
  }

  createPlacementWithFile(formData: FormData): Observable<{placement: Placement, message: string}> {
    return this.http.post<{placement: Placement, message: string}>(
      `${this.API_URL}/placements`,
      formData,
      { headers: this.getHeaders() }
    );
  }

  updatePlacementWithFile(id: number, formData: FormData): Observable<{placement: Placement, message: string}> {
    return this.http.put<{placement: Placement, message: string}>(
      `${this.API_URL}/placements/${id}`,
      formData,
      { headers: this.getHeaders() }
    );
  }
}