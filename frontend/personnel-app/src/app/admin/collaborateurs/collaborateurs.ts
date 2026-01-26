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
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { CollaborateurService } from '../../core/services/collaborateur.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Entreprise } from '../../core/models/entreprise.model';
import { CollaborateurDialogComponent } from './collaborateur-dialog/collaborateur-dialog';

@Component({
  selector: 'app-collaborateurs',
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
    MatDividerModule
  ],
  templateUrl: './collaborateurs.html',
  styleUrl: './collaborateurs.scss'
})
export class CollaborateursComponent implements OnInit {
  collaborateurs: Collaborateur[] = [];
  filteredCollaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];
  isLoading = false;

  // Filtres
  searchTerm = '';
  selectedStatus = '';
  selectedEntreprise = '';

  // Configuration du tableau
  displayedColumns: string[] = [
    'avatar',
    'numero_employe', 
    'nom_complet', 
    'poste', 
    'entreprise', 
    'statut', 
    'validation', 
    'actions'
  ];

  constructor(
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
    
    // Charger les collaborateurs et entreprises en parallèle
    Promise.all([
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([collaborateursResponse, entreprisesResponse]) => {
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
    let filtered = [...this.collaborateurs];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(collab => 
        collab.nom.toLowerCase().includes(term) ||
        collab.prenom.toLowerCase().includes(term) ||
        collab.email.toLowerCase().includes(term) ||
        collab.poste.toLowerCase().includes(term) ||
        collab.numero_employe.toLowerCase().includes(term)
      );
    }

    // Filtre par statut
    if (this.selectedStatus) {
      filtered = filtered.filter(collab => collab.statut === this.selectedStatus);
    }

    // Filtre par entreprise
    if (this.selectedEntreprise) {
      filtered = filtered.filter(collab => 
        collab.entreprise_actuelle_id === Number(this.selectedEntreprise)
      );
    }

    this.filteredCollaborateurs = filtered;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedEntreprise = '';
    this.applyFilters();
  }

  getEntrepriseName(entrepriseId?: number): string {
    if (!entrepriseId) return '';
    const entreprise = this.entreprises.find(e => e.id === entrepriseId);
    return entreprise?.nom || '';
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'actif': 'Actif',
      'inactif': 'Inactif',
      'en_conge': 'En congé',
      'arret_maladie': 'Arrêt maladie'
    };
    return labels[status] || status;
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CollaborateurDialogComponent, {
      width: '80%',
      maxWidth: '900px',
      height: 'auto',
      maxHeight: '90vh',
      data: { isEditMode: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  viewCollaborateur(collaborateur: Collaborateur): void {
    // TODO: Ouvrir la vue détaillée
    console.log('Voir collaborateur:', collaborateur);
  }

  editCollaborateur(collaborateur: Collaborateur): void {
    const dialogRef = this.dialog.open(CollaborateurDialogComponent, {
      width: '80%',
      maxWidth: '900px',
      height: 'auto',
      maxHeight: '90vh',
      data: { collaborateur, isEditMode: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData(); // Recharger la liste
      }
    });
  }

  createPlacement(collaborateur: Collaborateur): void {
    // TODO: Ouvrir le dialog de création de placement
    console.log('Créer placement pour:', collaborateur);
  }

  deleteCollaborateur(collaborateur: Collaborateur): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${collaborateur.prenom} ${collaborateur.nom} ?`)) {
      this.collaborateurService.deleteCollaborateur(collaborateur.id).subscribe({
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

  getImageUrl(photoUrl: string | undefined): string {
    if (!photoUrl) return '';
    // Si l'URL commence déjà par http, la retourner telle quelle
    if (photoUrl.startsWith('http')) {
      return photoUrl;
    }
    // Sinon, construire l'URL complète avec le backend
    return `http://localhost:5000${photoUrl}`;
  }
}