import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar } from '@angular/material/snack-bar';

import { MouvementService, Mouvement } from '../../core/services/mouvement.service';
import { CollaborateurService } from '../../core/services/collaborateur.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Entreprise } from '../../core/models/entreprise.model';

@Component({
  selector: 'app-tracabilite',
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
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
    MatTooltipModule
  ],
  templateUrl: './tracabilite.html',
  styleUrl: './tracabilite.scss'
})
export class TracabiliteComponent implements OnInit {
  mouvements: Mouvement[] = [];
  filteredMouvements: Mouvement[] = [];
  paginatedMouvements: Mouvement[] = [];
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];
  isLoading = false;

  // Filtres
  searchTerm = '';
  selectedType = '';
  selectedCollaborateur = '';
  selectedEntreprise = '';

  // Pagination
  pageSize = 50;
  pageIndex = 0;
  totalItems = 0;

  // Types de mouvements
  typesMovements = [
    { value: 'placement_cree', label: 'Placement créé', icon: 'add_circle', color: '#4CAF50' },
    { value: 'placement_modifie', label: 'Placement modifié', icon: 'edit', color: '#FF9800' },
    { value: 'placement_valide', label: 'Placement validé', icon: 'check_circle', color: '#2196F3' },
    { value: 'placement_supprime', label: 'Placement supprimé', icon: 'delete', color: '#F44336' },
    { value: 'remplacement_cree', label: 'Remplacement créé', icon: 'swap_horiz', color: '#9C27B0' },
    { value: 'remplacement_modifie', label: 'Remplacement modifié', icon: 'edit', color: '#FF9800' },
    { value: 'remplacement_supprime', label: 'Remplacement supprimé', icon: 'delete', color: '#F44336' },
    { value: 'absence_demande', label: 'Absence demandée', icon: 'event_busy', color: '#00BCD4' },
    { value: 'absence_approuve', label: 'Absence approuvée', icon: 'done', color: '#4CAF50' },
    { value: 'absence_refuse', label: 'Absence refusée', icon: 'close', color: '#F44336' },
    { value: 'collaborateur_cree', label: 'Collaborateur créé', icon: 'person_add', color: '#4CAF50' },
    { value: 'collaborateur_modifie', label: 'Collaborateur modifié', icon: 'person', color: '#FF9800' },
    { value: 'collaborateur_statut_change', label: 'Statut collaborateur changé', icon: 'swap_horiz', color: '#2196F3' },
    { value: 'entreprise_cree', label: 'Entreprise créée', icon: 'business', color: '#4CAF50' },
    { value: 'entreprise_modifie', label: 'Entreprise modifiée', icon: 'business', color: '#FF9800' },
    { value: 'utilisateur_cree', label: 'Utilisateur créé', icon: 'person_add', color: '#4CAF50' },
    { value: 'utilisateur_modifie', label: 'Utilisateur modifié', icon: 'person', color: '#FF9800' },
    { value: 'utilisateur_role_change', label: 'Rôle utilisateur changé', icon: 'admin_panel_settings', color: '#2196F3' },
    { value: 'competence_ajout', label: 'Compétence ajoutée', icon: 'add', color: '#4CAF50' },
    { value: 'competence_modification', label: 'Compétence modifiée', icon: 'edit', color: '#FF9800' }
  ];

  constructor(
    private mouvementService: MouvementService,
    private collaborateurService: CollaborateurService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;

    Promise.all([
      this.mouvementService.getMouvements({ limit: 1000 }).toPromise(),
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([mouvementsResponse, collaborateursResponse, entreprisesResponse]) => {
      this.mouvements = mouvementsResponse?.mouvements || [];
      this.collaborateurs = collaborateursResponse?.collaborateurs || [];
      this.entreprises = entreprisesResponse?.entreprises || [];
      this.applyFilters();
      this.isLoading = false;
    }).catch(error => {
      console.error('Erreur lors du chargement:', error);
      this.snackBar.open('Erreur lors du chargement des données', 'Fermer', {
        duration: 3000
      });
      this.isLoading = false;
    });
  }

  applyFilters(): void {
    let filtered = [...this.mouvements];

    // Filtre par terme de recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(mouvement =>
        mouvement.description.toLowerCase().includes(term)
      );
    }

    // Filtre par type
    if (this.selectedType) {
      filtered = filtered.filter(mouvement => mouvement.type_mouvement === this.selectedType);
    }

    // Filtre par collaborateur
    if (this.selectedCollaborateur) {
      filtered = filtered.filter(mouvement =>
        mouvement.collaborateur_id === Number(this.selectedCollaborateur)
      );
    }

    // Filtre par entreprise
    if (this.selectedEntreprise) {
      filtered = filtered.filter(mouvement =>
        mouvement.entreprise_id === Number(this.selectedEntreprise)
      );
    }

    this.filteredMouvements = filtered;
    this.totalItems = filtered.length;
    this.pageIndex = 0;
    this.updatePaginatedData();
  }

  updatePaginatedData(): void {
    const startIndex = this.pageIndex * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.paginatedMouvements = this.filteredMouvements.slice(startIndex, endIndex);
  }

  onPageChange(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.updatePaginatedData();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedType = '';
    this.selectedCollaborateur = '';
    this.selectedEntreprise = '';
    this.applyFilters();
  }

  getTypeInfo(type: string): any {
    return this.typesMovements.find(t => t.value === type) || {
      label: type,
      icon: 'info',
      color: '#757575'
    };
  }

  getCollaborateurName(collaborateurId: number): string {
    const collaborateur = this.collaborateurs.find(c => c.id === collaborateurId);
    return collaborateur ? `${collaborateur.prenom} ${collaborateur.nom}` : 'N/A';
  }

  getEntrepriseName(entrepriseId: number): string {
    const entreprise = this.entreprises.find(e => e.id === entrepriseId);
    return entreprise?.nom || 'N/A';
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  exportToCSV(): void {
    const headers = ['Date', 'Type', 'Description', 'Collaborateur', 'Entreprise'];
    const rows = this.filteredMouvements.map(m => [
      this.formatDate(m.created_at),
      this.getTypeInfo(m.type_mouvement).label,
      m.description,
      m.collaborateur_id ? this.getCollaborateurName(m.collaborateur_id) : '',
      m.entreprise_id ? this.getEntrepriseName(m.entreprise_id) : ''
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
      csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tracabilite_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    this.snackBar.open('Export CSV réussi', 'Fermer', { duration: 3000 });
  }

  viewDetails(mouvement: Mouvement): void {
    // TODO: Ouvrir un dialog avec les détails complets
    console.log('Détails du mouvement:', mouvement);
  }
}
