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

import { RemplacementService } from '../../core/services/remplacement.service';
import { CollaborateurService } from '../../core/services/collaborateur.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { Remplacement } from '../../core/models/remplacement.model';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Entreprise } from '../../core/models/entreprise.model';
import { RemplacementDialogComponent } from './remplacement-dialog/remplacement-dialog';

@Component({
  selector: 'app-remplacements',
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
  templateUrl: './remplacements.html',
  styleUrl: './remplacements.scss'
})
export class RemplacementsComponent implements OnInit {
  remplacements: Remplacement[] = [];
  filteredRemplacements: Remplacement[] = [];
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];
  isLoading = false;

  // Filtres
  searchTerm = '';
  selectedStatus = '';
  selectedEntreprise = '';
  selectedType = '';

  // Configuration du tableau
  displayedColumns: string[] = [
    'collaborateur_remplacant',
    'collaborateur_remplace', 
    'entreprise',
    'motif',
    'date_debut',
    'date_fin',
    'statut',
    'actions'
  ];

  constructor(
    private remplacementService: RemplacementService,
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
      this.remplacementService.getRemplacements().toPromise(),
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([remplacementsResponse, collaborateursResponse, entreprisesResponse]) => {
      this.remplacements = remplacementsResponse?.remplacements || [];
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
    let filtered = [...this.remplacements];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(remplacement => {
        const remplacant = this.getCollaborateurName(remplacement.collaborateur_remplacant_id);
        const remplace = this.getCollaborateurName(remplacement.collaborateur_remplace_id);
        const entreprise = this.getEntrepriseName(remplacement.entreprise_id);
        return remplacant.toLowerCase().includes(term) ||
               remplace.toLowerCase().includes(term) ||
               entreprise.toLowerCase().includes(term) ||
               remplacement.motif.toLowerCase().includes(term);
      });
    }

    // Filtre par statut
    if (this.selectedStatus) {
      filtered = filtered.filter(remplacement => remplacement.statut === this.selectedStatus);
    }

    // Filtre par entreprise
    if (this.selectedEntreprise) {
      filtered = filtered.filter(remplacement => 
        remplacement.entreprise_id === Number(this.selectedEntreprise)
      );
    }

    this.filteredRemplacements = filtered;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedEntreprise = '';
    this.selectedType = '';
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
      'planifie': 'Planifié',
      'en_cours': 'En cours',
      'termine': 'Terminé',
      'annule': 'Annulé'
    };
    return labels[status] || status;
  }

  getStatusClass(status: string): string {
    const classes: { [key: string]: string } = {
      'planifie': 'status-planned',
      'en_cours': 'status-active',
      'termine': 'status-completed',
      'annule': 'status-cancelled'
    };
    return classes[status] || '';
  }

  getMotifIcon(motif: string): string {
    const icons: { [key: string]: string } = {
      'conge': 'beach_access',
      'maladie': 'local_hospital',
      'formation': 'school',
      'autre': 'help_outline'
    };
    return icons[motif] || 'swap_horiz';
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(RemplacementDialogComponent, {
      width: '95vw',
      maxWidth: '95vw',
      height: '90vh',
      maxHeight: '90vh',
      panelClass: 'large-dialog',
      data: { isEditMode: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  editRemplacement(remplacement: Remplacement): void {
    const dialogRef = this.dialog.open(RemplacementDialogComponent, {
      width: '95vw',
      maxWidth: '95vw',
      height: '90vh',
      maxHeight: '90vh',
      panelClass: 'large-dialog',
      data: { remplacement, isEditMode: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  viewRemplacement(remplacement: Remplacement): void {
    // TODO: Ouvrir la vue détaillée
    console.log('Voir remplacement:', remplacement);
  }

  deleteRemplacement(remplacement: Remplacement): void {
    const remplacantName = this.getCollaborateurName(remplacement.collaborateur_remplacant_id);
    const remplaceName = this.getCollaborateurName(remplacement.collaborateur_remplace_id);
    
    if (confirm(`Êtes-vous sûr de vouloir supprimer le remplacement de ${remplaceName} par ${remplacantName} ?`)) {
      this.remplacementService.deleteRemplacement(remplacement.id).subscribe({
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