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

import { RemplacementService } from '../../../core/services/remplacement.service';
import { CollaborateurService } from '../../../core/services/collaborateur.service';
import { EntrepriseService } from '../../../core/services/entreprise.service';
import { Remplacement } from '../../../core/models/remplacement.model';
import { Collaborateur } from '../../../core/models/collaborateur.model';
import { Entreprise } from '../../../core/models/entreprise.model';

export interface RemplacementDialogData {
  remplacement?: Remplacement;
  isEditMode: boolean;
}

@Component({
  selector: 'app-remplacement-dialog',
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
  templateUrl: './remplacement-dialog.html',
  styleUrl: './remplacement-dialog.scss'
})
export class RemplacementDialogComponent implements OnInit {
  remplacementForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<RemplacementDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: RemplacementDialogData,
    private remplacementService: RemplacementService,
    private collaborateurService: CollaborateurService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.isEditMode = data.isEditMode;
    this.remplacementForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadData();
    
    if (this.isEditMode && this.data.remplacement) {
      this.populateForm(this.data.remplacement);
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      collaborateur_remplacant_id: ['', [Validators.required]],
      collaborateur_remplace_id: ['', [Validators.required]],
      entreprise_id: ['', [Validators.required]],
      motif: ['', [Validators.required]],
      date_debut: ['', [Validators.required]],
      date_fin: ['', [Validators.required]],
      statut: ['planifie', [Validators.required]],
      notes: ['']
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

  private populateForm(remplacement: Remplacement): void {
    this.remplacementForm.patchValue({
      collaborateur_remplacant_id: remplacement.collaborateur_remplacant_id,
      collaborateur_remplace_id: remplacement.collaborateur_remplace_id,
      entreprise_id: remplacement.entreprise_id,
      motif: remplacement.motif,
      date_debut: remplacement.date_debut,
      date_fin: remplacement.date_fin,
      statut: remplacement.statut,
      notes: remplacement.notes || ''
    });
  }

  onSave(): void {
    if (this.remplacementForm.valid) {
      this.isLoading = true;
      
      const formData = this.remplacementForm.value;
      
      const request = this.isEditMode 
        ? this.remplacementService.updateRemplacement(this.data.remplacement!.id, formData)
        : this.remplacementService.createRemplacement(formData);

      request.subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.dialogRef.close(response.remplacement);
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