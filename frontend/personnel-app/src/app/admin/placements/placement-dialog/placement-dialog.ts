import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar } from '@angular/material/snack-bar';

import { PlacementService } from '../../../core/services/placement.service';
import { CollaborateurService } from '../../../core/services/collaborateur.service';
import { EntrepriseService } from '../../../core/services/entreprise.service';
import { Placement } from '../../../core/models/placement.model';
import { Collaborateur } from '../../../core/models/collaborateur.model';
import { Entreprise } from '../../../core/models/entreprise.model';

export interface PlacementDialogData {
  placement?: Placement;
  isEditMode: boolean;
}

@Component({
  selector: 'app-placement-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './placement-dialog.html',
  styleUrl: './placement-dialog.scss'
})
export class PlacementDialogComponent implements OnInit {
  placementForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<PlacementDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PlacementDialogData,
    private placementService: PlacementService,
    private collaborateurService: CollaborateurService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.isEditMode = data.isEditMode;
    this.placementForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadData();
    
    if (this.isEditMode && this.data.placement) {
      this.populateForm(this.data.placement);
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      collaborateur_id: ['', [Validators.required]],
      entreprise_id: ['', [Validators.required]],
      poste: ['', [Validators.required]],
      date_debut: ['', [Validators.required]],
      date_fin: [''],
      salaire: ['', [Validators.required, Validators.min(0)]],
      statut: ['en_attente', [Validators.required]],
      description: [''],
      conditions: ['']
    });
  }

  private loadData(): void {
    Promise.all([
      this.collaborateurService.getCollaborateurs().toPromise(),
      this.entrepriseService.getEntreprises().toPromise()
    ]).then(([collaborateursResponse, entreprisesResponse]) => {
      this.collaborateurs = collaborateursResponse?.collaborateurs || [];
      this.entreprises = entreprisesResponse?.entreprises || [];
    }).catch(error => {
      console.error('Erreur lors du chargement:', error);
    });
  }

  private populateForm(placement: Placement): void {
    this.placementForm.patchValue({
      collaborateur_id: placement.collaborateur_id,
      entreprise_id: placement.entreprise_id,
      poste: placement.poste,
      date_debut: placement.date_debut,
      date_fin: placement.date_fin || '',
      salaire: placement.salaire,
      statut: placement.statut,
      description: placement.description || '',
      conditions: placement.conditions || ''
    });
  }

  onSave(): void {
    if (this.placementForm.valid) {
      this.isLoading = true;
      
      const formData = this.placementForm.value;
      
      const request = this.isEditMode 
        ? this.placementService.updatePlacement(this.data.placement!.id, formData)
        : this.placementService.createPlacement(formData);

      request.subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.dialogRef.close(response.placement);
        },
        error: (error) => {
          this.isLoading = false;
          const message = error.error?.message || 'Erreur lors de la sauvegarde';
          this.snackBar.open(message, 'Fermer', {
            duration: 4000,
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}