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
import { PlacementService } from '../../core/services/placement.service';
import { RemplacementService } from '../../core/services/remplacement.service';
import { AbsenceService } from '../../core/services/absence.service';
import { Collaborateur } from '../../core/models/collaborateur.model';
import { Placement } from '../../core/models/placement.model';
import { Remplacement } from '../../core/models/remplacement.model';

interface ValidationItem {
  id: number;
  type: 'collaborateur' | 'placement' | 'remplacement' | 'absence';
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
  placements: Placement[] = [];
  remplacements: Remplacement[] = [];
  absences: any[] = [];
  displayedColumns: string[] = ['type', 'description', 'date', 'statut', 'actions'];

  constructor(
    private snackBar: MatSnackBar,
    private collaborateurService: CollaborateurService,
    private placementService: PlacementService,
    private remplacementService: RemplacementService,
    private absenceService: AbsenceService
  ) {}

  ngOnInit(): void {
    this.loadValidations();
  }

  loadValidations(): void {
    this.isLoading = true;
    console.log('[DEBUG] === CHARGEMENT DES VALIDATIONS RH ===');
    
    // Charger toutes les données en parallèle
    Promise.all([
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.placementService.getPlacements().toPromise(),
      this.remplacementService.getRemplacements().toPromise(),
      this.absenceService.getAbsences(1, 100).toPromise() // Récupérer toutes les absences, pas seulement celles en attente
    ]).then(([collaborateursResponse, placementsResponse, remplacementsResponse, absencesResponse]) => {
      console.log('[DEBUG] === RÉPONSES REÇUES ===');
      console.log('[DEBUG] Collaborateurs response:', collaborateursResponse);
      console.log('[DEBUG] Placements response:', placementsResponse);
      console.log('[DEBUG] Remplacements response:', remplacementsResponse);
      console.log('[DEBUG] Absences en attente response:', absencesResponse);
      
      this.collaborateurs = collaborateursResponse?.collaborateurs || [];
      this.placements = placementsResponse?.placements || [];
      this.remplacements = remplacementsResponse?.remplacements || [];
      this.absences = absencesResponse?.absences || []; // getAbsences() returns { absences: [...] }
      
      console.log('[DEBUG] === DONNÉES EXTRAITES ===');
      console.log(`[DEBUG] Collaborateurs: ${this.collaborateurs.length} éléments`);
      console.log(`[DEBUG] Placements: ${this.placements.length} éléments`);
      console.log(`[DEBUG] Remplacements: ${this.remplacements.length} éléments`);
      console.log(`[DEBUG] Absences: ${this.absences.length} éléments`);
      
      // Afficher le détail des placements
      if (this.placements.length > 0) {
        console.log('[DEBUG] Détail des placements:');
        this.placements.forEach(p => {
          console.log(`[DEBUG] - Placement ${p.id}: statut=${p.statut}, collaborateur=${p.collaborateur_id}, entreprise=${p.entreprise_id}`);
        });
      }
      
      // Afficher le détail des remplacements
      if (this.remplacements.length > 0) {
        console.log('[DEBUG] Détail des remplacements:');
        this.remplacements.forEach(r => {
          console.log(`[DEBUG] - Remplacement ${r.id}: statut=${r.statut}, remplace=${r.remplace_id}, remplacant=${r.remplacant_id}`);
        });
      }
      
      // Afficher le détail des absences
      if (this.absences.length > 0) {
        console.log('[DEBUG] Détail des absences:');
        this.absences.forEach(a => {
          console.log(`[DEBUG] - Absence ${a.id}: statut=${a.statut}, collaborateur=${a.collaborateur_id}, type=${a.type_absence}`);
        });
      }
      
      this.generateValidations();
      this.isLoading = false;
    }).catch(error => {
      console.error('[ERROR] Erreur lors du chargement:', error);
      this.isLoading = false;
      this.snackBar.open('Erreur lors du chargement des données', 'Fermer', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    });
  }

  generateValidations(): void {
    this.validations = [];
    
    console.log('[DEBUG] === GÉNÉRATION DES VALIDATIONS ===');
    console.log(`[DEBUG] Collaborateurs reçus: ${this.collaborateurs.length}`);
    console.log(`[DEBUG] Placements reçus: ${this.placements.length}`);
    console.log(`[DEBUG] Remplacements reçus: ${this.remplacements.length}`);
    console.log(`[DEBUG] Absences reçues: ${this.absences.length}`);
    
    // Ajouter TOUS les collaborateurs (validés et non validés)
    this.collaborateurs.forEach(collaborateur => {
      const statut = collaborateur.is_validated_by_rh ? 'approuve' : 'en_attente';
      console.log(`[DEBUG] - Collaborateur ${collaborateur.id}: ${collaborateur.prenom} ${collaborateur.nom} (validé: ${collaborateur.is_validated_by_rh})`);
      this.validations.push({
        id: collaborateur.id,
        type: 'collaborateur',
        description: `Validation du collaborateur ${collaborateur.prenom} ${collaborateur.nom} - ${collaborateur.poste}`,
        date: new Date(collaborateur.created_at || Date.now()),
        statut: statut,
        data: collaborateur
      });
    });

    // Ajouter TOUS les placements (tous statuts)
    this.placements.forEach(placement => {
      console.log(`[DEBUG] - Placement ${placement.id}: statut=${placement.statut}, collaborateur=${placement.collaborateur_id}, entreprise=${placement.entreprise_id}`);
      const collaborateur = this.collaborateurs.find(c => c.id === placement.collaborateur_id);
      
      // Mapper les statuts de placement vers les statuts de validation
      let statutValidation: 'en_attente' | 'approuve' | 'refuse' = 'en_attente';
      if (placement.statut === 'confirme' || placement.statut === 'en_cours' || placement.statut === 'termine') {
        statutValidation = 'approuve';
      } else if (placement.statut === 'annule') {
        statutValidation = 'refuse';
      }
      
      this.validations.push({
        id: placement.id,
        type: 'placement',
        description: `Placement ${collaborateur?.prenom} ${collaborateur?.nom} - ${placement.poste_demande}`,
        date: new Date(placement.created_at || Date.now()),
        statut: statutValidation,
        data: placement
      });
    });

    // Ajouter TOUS les remplacements (tous statuts)
    this.remplacements.forEach(remplacement => {
      console.log(`[DEBUG] - Remplacement ${remplacement.id}: statut=${remplacement.statut}, remplace=${remplacement.remplace_id}, remplacant=${remplacement.remplacant_id}`);
      const remplace = this.collaborateurs.find(c => c.id === remplacement.remplace_id);
      const remplacant = this.collaborateurs.find(c => c.id === remplacement.remplacant_id);
      
      // Mapper les statuts de remplacement vers les statuts de validation
      let statutValidation: 'en_attente' | 'approuve' | 'refuse' = 'en_attente';
      if (remplacement.statut === 'en_cours' || remplacement.statut === 'termine') {
        statutValidation = 'approuve';
      } else if (remplacement.statut === 'annule') {
        statutValidation = 'refuse';
      }
      
      this.validations.push({
        id: remplacement.id,
        type: 'remplacement',
        description: `Remplacement ${remplace?.prenom} ${remplace?.nom} par ${remplacant?.prenom} ${remplacant?.nom}`,
        date: new Date(remplacement.created_at || Date.now()),
        statut: statutValidation,
        data: remplacement
      });
    });

    // Ajouter TOUTES les absences (tous statuts)
    this.absences.forEach(absence => {
      console.log(`[DEBUG] - Absence ${absence.id}: statut=${absence.statut}, collaborateur=${absence.collaborateur_id}, type=${absence.type_absence}`);
      const collaborateur = this.collaborateurs.find(c => c.id === absence.collaborateur_id);
      
      // Mapper les statuts d'absence vers les statuts de validation
      let statutValidation: 'en_attente' | 'approuve' | 'refuse' = 'en_attente';
      if (absence.statut === 'approuve') {
        statutValidation = 'approuve';
      } else if (absence.statut === 'refuse') {
        statutValidation = 'refuse';
      }
      
      this.validations.push({
        id: absence.id,
        type: 'absence',
        description: `Absence ${collaborateur?.prenom} ${collaborateur?.nom} - ${this.getTypeAbsenceLabel(absence.type_absence)} (${absence.nombre_jours} jours)`,
        date: new Date(absence.created_at || Date.now()),
        statut: statutValidation,
        data: absence
      });
    });

    console.log(`[DEBUG] === RÉSUMÉ FINAL ===`);
    console.log(`[DEBUG] Total validations générées: ${this.validations.length}`);
    console.log(`[DEBUG] - En attente: ${this.getValidationsByStatus('en_attente').length}`);
    console.log(`[DEBUG] - Approuvées: ${this.getValidationsByStatus('approuve').length}`);
    console.log(`[DEBUG] - Refusées: ${this.getValidationsByStatus('refuse').length}`);
    
    // Détail des statuts d'absences
    const absencesParStatut = this.absences.reduce((acc: any, absence) => {
      acc[absence.statut] = (acc[absence.statut] || 0) + 1;
      return acc;
    }, {});
    console.log(`[DEBUG] Répartition absences par statut:`, absencesParStatut);
  }

  approuver(validation: ValidationItem): void {
    if (validation.type === 'collaborateur' && validation.data) {
      // Validation d'un collaborateur
      this.collaborateurService.validateCollaborateur(validation.data.id).subscribe({
        next: (response) => {
          this.snackBar.open('Collaborateur validé avec succès', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors de la validation:', error);
          this.snackBar.open('Erreur lors de la validation du collaborateur', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else if (validation.type === 'placement' && validation.data) {
      // Validation d'un placement
      this.placementService.validatePlacement(validation.data.id).subscribe({
        next: (response) => {
          this.snackBar.open('Placement validé avec succès', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors de la validation:', error);
          this.snackBar.open('Erreur lors de la validation du placement', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else if (validation.type === 'remplacement' && validation.data) {
      // Validation d'un remplacement - changer le statut à "en_cours"
      const updateData: Partial<Remplacement> = { statut: 'en_cours' as any };
      this.remplacementService.updateRemplacement(validation.data.id, updateData).subscribe({
        next: (response) => {
          this.snackBar.open('Remplacement validé avec succès', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors de la validation:', error);
          this.snackBar.open('Erreur lors de la validation du remplacement', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else if (validation.type === 'absence' && validation.data) {
      // Validation d'une absence
      this.absenceService.approuverAbsence(validation.data.id).subscribe({
        next: (response) => {
          this.snackBar.open('Absence approuvée avec succès', 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors de l\'approbation:', error);
          this.snackBar.open('Erreur lors de l\'approbation de l\'absence', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  refuser(validation: ValidationItem): void {
    if (validation.type === 'absence' && validation.data) {
      // Refus d'une absence
      this.absenceService.refuserAbsence(validation.data.id).subscribe({
        next: (response) => {
          this.snackBar.open('Absence refusée', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors du refus:', error);
          this.snackBar.open('Erreur lors du refus de l\'absence', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else if (validation.type === 'placement' && validation.data) {
      // Refus d'un placement - changer le statut à "annule"
      const updateData: Partial<Placement> = { statut: 'annule' as any };
      this.placementService.updatePlacement(validation.data.id, updateData).subscribe({
        next: (response) => {
          this.snackBar.open('Placement refusé', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors du refus:', error);
          this.snackBar.open('Erreur lors du refus du placement', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else if (validation.type === 'remplacement' && validation.data) {
      // Refus d'un remplacement - changer le statut à "annule"
      const updateData: Partial<Remplacement> = { statut: 'annule' as any };
      this.remplacementService.updateRemplacement(validation.data.id, updateData).subscribe({
        next: (response) => {
          this.snackBar.open('Remplacement refusé', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
          this.loadValidations(); // Recharger pour mettre à jour la liste
        },
        error: (error) => {
          console.error('Erreur lors du refus:', error);
          this.snackBar.open('Erreur lors du refus du remplacement', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else {
      // Pour les autres types (collaborateurs - pas de refus possible)
      this.snackBar.open('Cette opération ne peut pas être refusée', 'Fermer', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
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
      case 'remplacement': return 'swap_horiz';
      case 'absence': return 'event_busy';
      default: return 'help_outline';
    }
  }

  getTypeLabel(type: string): string {
    switch (type) {
      case 'collaborateur': return 'Collaborateur';
      case 'placement': return 'Placement';
      case 'remplacement': return 'Remplacement';
      case 'absence': return 'Absence';
      default: return type;
    }
  }

  refreshValidations(): void {
    this.loadValidations();
  }

  getTypeAbsenceLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'conge_paye': 'Congé payé',
      'conge_sans_solde': 'Congé sans solde',
      'maladie': 'Maladie',
      'formation': 'Formation',
      'maternite': 'Maternité',
      'paternite': 'Paternité',
      'autre': 'Autre'
    };
    return labels[type] || type;
  }
}