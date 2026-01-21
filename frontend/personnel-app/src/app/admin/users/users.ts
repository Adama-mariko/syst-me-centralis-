import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { User } from '../../core/models/user.model';
import { Entreprise } from '../../core/models/entreprise.model';
import { UserDialogComponent } from './user-dialog/user-dialog';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatMenuModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatDividerModule
  ],
  templateUrl: './users.html',
  styleUrl: './users.scss'
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  filteredUsers: User[] = [];
  entreprises: Entreprise[] = [];
  isLoading = false;
  currentUserId: number | null = null;

  // Filtres
  searchTerm = '';
  selectedRole = '';
  selectedStatus = '';

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private entrepriseService: EntrepriseService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    // Récupérer l'ID de l'utilisateur connecté
    this.authService.currentUser$.subscribe(user => {
      this.currentUserId = user?.id || null;
    });
    
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Charger les utilisateurs et entreprises en parallèle
    Promise.all([
      this.apiService.get<{users: User[]}>('/admin/users').toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([usersResponse, entreprisesResponse]) => {
      this.users = usersResponse?.users || [];
      this.entreprises = entreprisesResponse?.entreprises || [];
      this.applyFilters();
      this.isLoading = false;
    }).catch(error => {
      console.error('Erreur lors du chargement:', error);
      this.snackBar.open('Erreur lors du chargement des données', 'Fermer', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      this.isLoading = false;
    });
  }

  applyFilters(): void {
    let filtered = [...this.users];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(user => 
        user.nom.toLowerCase().includes(term) ||
        user.prenom.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term)
      );
    }

    // Filtre par rôle
    if (this.selectedRole) {
      filtered = filtered.filter(user => user.role === this.selectedRole);
    }

    // Filtre par statut
    if (this.selectedStatus !== '') {
      const isActive = this.selectedStatus === 'true';
      filtered = filtered.filter(user => user.is_active === isActive);
    }

    this.filteredUsers = filtered;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedRole = '';
    this.selectedStatus = '';
    this.applyFilters();
  }

  getRoleIcon(role: string): string {
    switch (role) {
      case 'admin':
        return 'admin_panel_settings';
      case 'rh_entreprise':
        return 'business_center';
      default:
        return 'person';
    }
  }

  getRoleLabel(role: string): string {
    switch (role) {
      case 'admin':
        return 'Administrateur';
      case 'rh_entreprise':
        return 'RH Entreprise';
      default:
        return role;
    }
  }

  getEntrepriseName(entrepriseId: number): string {
    const entreprise = this.entreprises.find(e => e.id === entrepriseId);
    return entreprise?.nom || 'Non assigné';
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('fr-FR');
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(UserDialogComponent, {
      width: '600px',
      data: { isEditMode: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  viewUser(user: User): void {
    // TODO: Ouvrir la vue détaillée
    console.log('Voir utilisateur:', user);
  }

  editUser(user: User): void {
    const dialogRef = this.dialog.open(UserDialogComponent, {
      width: '600px',
      data: { user, isEditMode: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  resetPassword(user: User): void {
    if (confirm(`Réinitialiser le mot de passe de ${user.prenom} ${user.nom} ?`)) {
      // TODO: Implémenter la réinitialisation du mot de passe
      this.snackBar.open('Fonctionnalité en cours de développement', 'Fermer', {
        duration: 3000,
        panelClass: ['info-snackbar']
      });
    }
  }

  toggleStatus(user: User): void {
    if (user.id === this.currentUserId) {
      this.snackBar.open('Vous ne pouvez pas désactiver votre propre compte', 'Fermer', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    const newStatus = !user.is_active;
    const action = newStatus ? 'activer' : 'désactiver';
    
    if (confirm(`Êtes-vous sûr de vouloir ${action} l'utilisateur ${user.prenom} ${user.nom} ?`)) {
      this.apiService.put<{user: User, message: string}>(`/admin/users/${user.id}`, { 
        is_active: newStatus 
      }).subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadData();
        },
        error: (error) => {
          this.snackBar.open('Erreur lors de la modification', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  deleteUser(user: User): void {
    if (user.id === this.currentUserId) {
      this.snackBar.open('Vous ne pouvez pas supprimer votre propre compte', 'Fermer', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    if (confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${user.prenom} ${user.nom} ?`)) {
      this.apiService.delete<{message: string}>(`/admin/users/${user.id}`).subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadData();
        },
        error: (error) => {
          this.snackBar.open('Erreur lors de la suppression', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }
}