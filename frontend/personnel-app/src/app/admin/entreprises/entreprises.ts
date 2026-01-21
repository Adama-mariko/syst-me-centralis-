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
import { Router } from '@angular/router';

import { EntrepriseService } from '../../core/services/entreprise.service';
import { CollaborateurService } from '../../core/services/collaborateur.service';
import { PlacementService } from '../../core/services/placement.service';
import { Entreprise } from '../../core/models/entreprise.model';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Placement } from '../../core/models/placement.model';
import { EntrepriseDialogComponent } from './entreprise-dialog/entreprise-dialog';

@Component({
  selector: 'app-entreprises',
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
  templateUrl: './entreprises.html',
  styleUrl: './entreprises.scss'
})
export class EntreprisesComponent implements OnInit {
  entreprises: Entreprise[] = [];
  filteredEntreprises: Entreprise[] = [];
  collaborateurs: Collaborateur[] = [];
  placements: Placement[] = [];
  isLoading = false;

  // Filtres
  searchTerm = '';
  selectedVille = '';
  selectedStatus = '';
  villes: string[] = [];

  constructor(
    private entrepriseService: EntrepriseService,
    private collaborateurService: CollaborateurService,
    private placementService: PlacementService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Charger toutes les données en parallèle
    Promise.all([
      this.entrepriseService.getEntreprises().toPromise(),
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.placementService.getPlacements().toPromise()
    ]).then(([entreprisesResponse, collaborateursResponse, placementsResponse]) => {
      this.entreprises = entreprisesResponse?.entreprises || [];
      this.collaborateurs = collaborateursResponse?.collaborateurs || [];
      this.placements = placementsResponse?.placements || [];
      
      // Extraire les villes uniques
      this.villes = [...new Set(this.entreprises.map(e => e.ville))].sort();
      
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
    let filtered = [...this.entreprises];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(entreprise => 
        entreprise.nom.toLowerCase().includes(term) ||
        entreprise.siret.toLowerCase().includes(term) ||
        entreprise.ville.toLowerCase().includes(term) ||
        entreprise.adresse.toLowerCase().includes(term) ||
        (entreprise.email && entreprise.email.toLowerCase().includes(term))
      );
    }

    // Filtre par ville
    if (this.selectedVille) {
      filtered = filtered.filter(entreprise => entreprise.ville === this.selectedVille);
    }

    // Filtre par statut
    if (this.selectedStatus !== '') {
      const isActive = this.selectedStatus === 'true';
      filtered = filtered.filter(entreprise => entreprise.is_active === isActive);
    }

    this.filteredEntreprises = filtered;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedVille = '';
    this.selectedStatus = '';
    this.applyFilters();
  }

  getCollaborateursCount(entrepriseId: number): number {
    return this.collaborateurs.filter(c => c.entreprise_actuelle_id === entrepriseId).length;
  }

  getPlacementsCount(entrepriseId: number): number {
    return this.placements.filter(p => p.entreprise_id === entrepriseId).length;
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(EntrepriseDialogComponent, {
      width: '700px',
      data: { isEditMode: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  viewEntreprise(entreprise: Entreprise): void {
    // TODO: Ouvrir la vue détaillée
    console.log('Voir entreprise:', entreprise);
  }

  editEntreprise(entreprise: Entreprise): void {
    const dialogRef = this.dialog.open(EntrepriseDialogComponent, {
      width: '700px',
      data: { entreprise, isEditMode: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  viewCollaborateurs(entreprise: Entreprise): void {
    // Naviguer vers la liste des collaborateurs filtrée par entreprise
    this.router.navigate(['/admin/collaborateurs'], {
      queryParams: { entreprise: entreprise.id }
    });
  }

  createUser(entreprise: Entreprise): void {
    // TODO: Ouvrir le dialog de création d'utilisateur RH
    console.log('Créer utilisateur RH pour:', entreprise);
  }

  toggleStatus(entreprise: Entreprise): void {
    const newStatus = !entreprise.is_active;
    const action = newStatus ? 'activer' : 'désactiver';
    
    if (confirm(`Êtes-vous sûr de vouloir ${action} l'entreprise ${entreprise.nom} ?`)) {
      this.entrepriseService.updateEntreprise(entreprise.id, { is_active: newStatus }).subscribe({
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

  deleteEntreprise(entreprise: Entreprise): void {
    const collaborateursCount = this.getCollaborateursCount(entreprise.id);
    
    if (collaborateursCount > 0) {
      this.snackBar.open(
        `Impossible de supprimer: ${collaborateursCount} collaborateur(s) assigné(s)`, 
        'Fermer', 
        { duration: 4000, panelClass: ['warning-snackbar'] }
      );
      return;
    }

    if (confirm(`Êtes-vous sûr de vouloir supprimer l'entreprise ${entreprise.nom} ?`)) {
      this.entrepriseService.deleteEntreprise(entreprise.id).subscribe({
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