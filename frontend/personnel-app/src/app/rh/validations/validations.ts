import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';

import { CollaborateurService } from '../../core/services/collaborateur.service';
import { Collaborateur } from '../../core/models/collaborateur.model';

interface ValidationItem {
  id: number;
  type: 'collaborateur' | 'placement' | 'absence';
  description: string;
  date: Date;
  statut: 'en_attente' | 'approuve' | 'refuse';
  data?: any;
}

@Component({
  selector: 'app-validations',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatDividerModule
  ],
  templateUrl: './validations.html',
  styleUrls: ['./validations.scss']
})
export class ValidationsComponent implements OnInit {
  isLoading = false;
  validations: ValidationItem[] = [];
  collaborateurs: Collaborateur[] = [];
  displayedColumns: string[] = ['type', 'description', 'date', 'statut', 'actions'];

  constructor(
    private snackBar: MatSnackBar,
    private collaborateurService: CollaborateurService
  ) {}

  ngOnInit(): void {
    this.loadValidations();
  }

  loadValidations(): void {
    this.isLoading = true;
    
    // Charger les collaborateurs qui nécessitent une validation
    this.collaborateurService.getCollaborateurs().subscribe({
      next: (response) => {
        this.collaborateurs = response.collaborateurs;
        this.generateValidations();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des collaborateurs:', error);
        this.isLoading = false;
        this.snackBar.open('Erreur lors du chargement des données', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  generateValidations(): void {
    this.validations = [];
    
    // Ajouter les collaborateurs récemment créés qui nécessitent une validation
    this.collaborateurs.forEach(collaborateur => {
      // Considérer qu'un collaborateur créé récemment (moins de 7 jours) nécessite une validation
      const createdDate = new Date(collaborateur.created_at || Date.now());
      const daysDiff = Math.floor((Date.now() - createdDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (daysDiff <= 7) {
        this.validations.push({
          id: collaborateur.id,
          type: 'collaborateur',
          description: `Validation du nouveau collaborateur ${collaborateur.prenom} ${collaborateur.nom} - ${collaborateur.poste}`,
          date: createdDate,
          statut: 'en_attente',
          data: collaborateur
        });
      }
    });

    // Ajouter quelques validations d'exemple pour les autres types
    this.validations.push(
      {
        id: 999,
        type: 'placement',
        description: 'Validation placement Jean Dupont chez TechCorp',
        date: new Date(),
        statut: 'en_attente'
      },
      {
        id: 998,
        type: 'absence',
        description: 'Demande congé Marie Martin du 15/02 au 20/02',
        date: new Date(),
        statut: 'en_attente'
      }
    );
  }

  approuver(validation: ValidationItem): void {
    validation.statut = 'approuve';
    
    // Si c'est un collaborateur, on peut appeler le service de validation
    if (validation.type === 'collaborateur' && validation.data) {
      this.collaborateurService.validateCollaborateur(validation.data.id).subscribe({
        next: (response) => {
          this.snackBar.open('Collaborateur validé avec succès', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
        },
        error: (error) => {
          console.error('Erreur lors de la validation:', error);
          this.snackBar.open('Validation approuvée localement', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
        }
      });
    } else {
      this.snackBar.open('Validation approuvée avec succès', 'Fermer', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    }
  }

  refuser(validation: ValidationItem): void {
    validation.statut = 'refuse';
    this.snackBar.open('Validation refusée', 'Fermer', {
      duration: 3000,
      panelClass: ['error-snackbar']
    });
  }

  getStatutLabel(statut: string): string {
    switch (statut) {
      case 'en_attente': return 'En attente';
      case 'approuve': return 'Approuvé';
      case 'refuse': return 'Refusé';
      default: return statut;
    }
  }

  getStatutClass(statut: string): string {
    switch (statut) {
      case 'en_attente': return 'status-pending';
      case 'approuve': return 'status-active';
      case 'refuse': return 'status-inactive';
      default: return '';
    }
  }

  getValidationsByStatus(statut: string): ValidationItem[] {
    return this.validations.filter(v => v.statut === statut);
  }

  getTypeIcon(type: string): string {
    switch (type) {
      case 'collaborateur': return 'person_add';
      case 'placement': return 'assignment';
      case 'absence': return 'event_busy';
      default: return 'help_outline';
    }
  }

  getTypeLabel(type: string): string {
    switch (type) {
      case 'collaborateur': return 'Collaborateur';
      case 'placement': return 'Placement';
      case 'absence': return 'Absence';
      default: return type;
    }
  }

  refreshValidations(): void {
    this.loadValidations();
  }
}