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
import { MatNativeDateModule, provideNativeDateAdapter } from '@angular/material/core';
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
  providers: [provideNativeDateAdapter()],
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
      remplacant_id: ['', [Validators.required]],
      remplace_id: ['', [Validators.required]],
      type_remplacement: ['temporaire', [Validators.required]],
      motif: ['', [Validators.required]],
      date_debut: ['', [Validators.required]],
      date_fin: ['', [Validators.required]],
      commentaires: ['']
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
      remplacant_id: remplacement.remplacant_id,
      remplace_id: remplacement.remplace_id,
      type_remplacement: remplacement.type_remplacement,
      motif: remplacement.motif,
      date_debut: remplacement.date_debut,
      date_fin: remplacement.date_fin,
      commentaires: remplacement.commentaires || ''
    });
  }

  onSave(): void {
    if (this.remplacementForm.valid) {
      this.isLoading = true;
      
      const formData = this.remplacementForm.value;
      console.log('[DEBUG] Données du formulaire:', formData);
      
      // Formatage des dates si nécessaire
      if (formData.date_debut instanceof Date) {
        formData.date_debut = formData.date_debut.toISOString();
      }
      if (formData.date_fin instanceof Date) {
        formData.date_fin = formData.date_fin.toISOString();
      }
      
      console.log('[DEBUG] Données formatées à envoyer:', formData);
      
      const request = this.isEditMode 
        ? this.remplacementService.updateRemplacement(this.data.remplacement!.id, formData)
        : this.remplacementService.createRemplacement(formData);

      request.subscribe({
        next: (response) => {
          console.log('[DEBUG] Réponse du serveur:', response);
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.dialogRef.close(response.remplacement);
        },
        error: (error) => {
          console.error('[ERROR] Erreur lors de la sauvegarde:', error);
          console.error('[ERROR] Détails de l\'erreur:', error.error);
          this.isLoading = false;
          const message = error.error?.message || error.error?.error || 'Erreur lors de la sauvegarde';
          this.snackBar.open(message, 'Fermer', {
            duration: 4000,
            panelClass: ['error-snackbar']
          });
        }
      });
    } else {
      console.log('[DEBUG] Formulaire invalide:', this.remplacementForm.errors);
      console.log('[DEBUG] Erreurs par champ:');
      Object.keys(this.remplacementForm.controls).forEach(key => {
        const control = this.remplacementForm.get(key);
        if (control && control.errors) {
          console.log(`[DEBUG] ${key}:`, control.errors);
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}