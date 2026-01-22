import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { ApiService } from './api.service';

export interface Notification {
  id?: number;
  type_notification: string;
  destinataire_user_id?: number;
  destinataire_email?: string;
  destinataire?: {
    id: number;
    nom: string;
    prenom: string;
    email: string;
  };
  sujet: string;
  message: string;
  statut: string;
  date_envoi?: string;
  tentatives: number;
  erreur_message?: string;
  placement_id?: number;
  absence_id?: number;
  remplacement_id?: number;
  created_at?: string;
}

export interface NotificationResponse {
  notifications: Notification[];
  total: number;
  pages: number;
  current_page: number;
}

export interface StatistiquesNotifications {
  par_statut: { [key: string]: number };
  par_type: { [key: string]: number };
  notifications_24h: number;
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private readonly API_URL = 'http://localhost:5000/api';
  private unreadCountSubject = new BehaviorSubject<number>(0);
  public unreadCount$ = this.unreadCountSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadUnreadCount();
  }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    });
  }

  getNotifications(page: number = 1, perPage: number = 20, filters?: any): Observable<NotificationResponse> {
    let params: any = { page, per_page: perPage };
    if (filters) {
      params = { ...params, ...filters };
    }
    
    const queryString = new URLSearchParams(params).toString();
    return this.http.get<NotificationResponse>(`${this.API_URL}/notifications?${queryString}`, {
      headers: this.getHeaders()
    });
  }

  getAllNotifications(page: number = 1, perPage: number = 20, filters?: any): Observable<NotificationResponse> {
    let params: any = { page, per_page: perPage };
    if (filters) {
      params = { ...params, ...filters };
    }
    
    const queryString = new URLSearchParams(params).toString();
    return this.http.get<NotificationResponse>(`${this.API_URL}/notifications/all?${queryString}`, {
      headers: this.getHeaders()
    });
  }

  renvoyerNotification(id: number): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_URL}/notifications/${id}/renvoyer`, {}, {
      headers: this.getHeaders()
    });
  }

  renvoyerNotificationsEnAttente(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_URL}/notifications/renvoyer-en-attente`, {}, {
      headers: this.getHeaders()
    });
  }

  getStatistiquesNotifications(): Observable<{ statistiques: StatistiquesNotifications }> {
    return this.http.get<{ statistiques: StatistiquesNotifications }>(`${this.API_URL}/notifications/statistiques`, {
      headers: this.getHeaders()
    });
  }

  private loadUnreadCount(): void {
    this.getNotifications(1, 1, { statut: 'en_attente' }).subscribe(response => {
      this.unreadCountSubject.next(response.total);
    });
  }

  refreshUnreadCount(): void {
    this.loadUnreadCount();
  }

  getTypeNotificationLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'placement_cree': 'Placement créé',
      'placement_valide': 'Placement validé',
      'placement_refuse': 'Placement refusé',
      'absence_demandee': 'Absence demandée',
      'absence_approuvee': 'Absence approuvée',
      'absence_refusee': 'Absence refusée',
      'remplacement_propose': 'Remplacement proposé',
      'rappel_validation': 'Rappel de validation',
      'autre': 'Autre'
    };
    return labels[type] || type;
  }

  getStatutNotificationLabel(statut: string): string {
    const labels: { [key: string]: string } = {
      'en_attente': 'En attente',
      'envoye': 'Envoyé',
      'echec': 'Échec'
    };
    return labels[statut] || statut;
  }

  getStatutColor(statut: string): string {
    const colors: { [key: string]: string } = {
      'en_attente': 'warn',
      'envoye': 'primary',
      'echec': 'accent'
    };
    return colors[statut] || 'basic';
  }

  getTypeIcon(type: string): string {
    const icons: { [key: string]: string } = {
      'placement_cree': 'work',
      'placement_valide': 'check_circle',
      'placement_refuse': 'cancel',
      'absence_demandee': 'event_busy',
      'absence_approuvee': 'event_available',
      'absence_refusee': 'event_busy',
      'remplacement_propose': 'swap_horiz',
      'rappel_validation': 'notification_important',
      'autre': 'info'
    };
    return icons[type] || 'notifications';
  }
}