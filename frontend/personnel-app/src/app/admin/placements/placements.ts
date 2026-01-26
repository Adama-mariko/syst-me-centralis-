import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { PlacementService } from '../../core/services/placement.service';
import { CollaborateurService } from '../../core/services/collaborateur.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { Placement } from '../../core/models/placement.model';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Entreprise } from '../../core/models/entreprise.model';
import { PlacementDialogComponent } from './placement-dialog/placement-dialog';

@Component({
  selector: 'app-placements',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatMenuModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatDividerModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './placements.html',
  styleUrl: './placements.scss'
})
export class PlacementsComponent implements OnInit {
  placements: Placement[] = [];
  filteredPlacements: Placement[] = [];
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];
  isLoading = false;

  // Filtres
  searchTerm = '';
  selectedStatus = '';
  selectedEntreprise = '';
  selectedCollaborateur = '';

  // Configuration du tableau
  displayedColumns: string[] = [
    'collaborateur',
    'entreprise', 
    'poste',
    'date_debut',
    'date_fin',
    'statut',
    'salaire',
    'actions'
  ];

  constructor(
    private placementService: PlacementService,
    private collaborateurService: CollaborateurService,
    private entrepriseService: EntrepriseService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Charger toutes les données en parallèle
    Promise.all([
      this.placementService.getPlacements().toPromise(),
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([placementsResponse, collaborateursResponse, entreprisesResponse]) => {
      this.placements = placementsResponse?.placements || [];
      this.collaborateurs = collaborateursResponse?.collaborateurs || [];
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
    let filtered = [...this.placements];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(placement => {
        const collaborateur = this.getCollaborateurName(placement.collaborateur_id);
        const entreprise = this.getEntrepriseName(placement.entreprise_id);
        return collaborateur.toLowerCase().includes(term) ||
               entreprise.toLowerCase().includes(term) ||
               placement.poste_demande.toLowerCase().includes(term);
      });
    }

    // Filtre par statut
    if (this.selectedStatus) {
      filtered = filtered.filter(placement => placement.statut === this.selectedStatus);
    }

    // Filtre par entreprise
    if (this.selectedEntreprise) {
      filtered = filtered.filter(placement => 
        placement.entreprise_id === Number(this.selectedEntreprise)
      );
    }

    // Filtre par collaborateur
    if (this.selectedCollaborateur) {
      filtered = filtered.filter(placement => 
        placement.collaborateur_id === Number(this.selectedCollaborateur)
      );
    }

    this.filteredPlacements = filtered;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedEntreprise = '';
    this.selectedCollaborateur = '';
    this.applyFilters();
  }

  getCollaborateurName(collaborateurId: number): string {
    const collaborateur = this.collaborateurs.find(c => c.id === collaborateurId);
    return collaborateur ? `${collaborateur.prenom} ${collaborateur.nom}` : '';
  }

  getEntrepriseName(entrepriseId: number): string {
    const entreprise = this.entreprises.find(e => e.id === entrepriseId);
    return entreprise?.nom || '';
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'en_cours': 'En cours',
      'termine': 'Terminé',
      'annule': 'Annulé',
      'en_attente': 'En attente',
      'confirme': 'Confirmé'
    };
    return labels[status] || status;
  }

  getStatusClass(status: string): string {
    const classes: { [key: string]: string } = {
      'en_cours': 'status-active',
      'termine': 'status-completed',
      'annule': 'status-cancelled',
      'en_attente': 'status-pending',
      'confirme': 'status-confirmed'
    };
    return classes[status] || '';
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(PlacementDialogComponent, {
      width: '80%',
      maxWidth: '900px',
      height: 'auto',
      maxHeight: '90vh',
      data: { isEditMode: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  editPlacement(placement: Placement): void {
    const dialogRef = this.dialog.open(PlacementDialogComponent, {
      width: '80%',
      maxWidth: '900px',
      height: 'auto',
      maxHeight: '90vh',
      data: { placement, isEditMode: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  viewPlacement(placement: Placement): void {
    // TODO: Ouvrir la vue détaillée
    console.log('Voir placement:', placement);
  }

  viewDocument(placement: Placement): void {
    if (placement.document_url) {
      window.open('http://localhost:5000' + placement.document_url, '_blank');
    }
  }

  deletePlacement(placement: Placement): void {
    const collaborateurName = this.getCollaborateurName(placement.collaborateur_id);
    const entrepriseName = this.getEntrepriseName(placement.entreprise_id);
    
    if (confirm(`Êtes-vous sûr de vouloir supprimer le placement de ${collaborateurName} chez ${entrepriseName} ?`)) {
      this.placementService.deletePlacement(placement.id).subscribe({
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

  isImage(url: string): boolean {
    if (!url) return false;
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    return imageExtensions.some(ext => url.toLowerCase().endsWith(ext));
  }
}