import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { EntrepriseService } from '../../../core/services/entreprise.service';
import { Entreprise } from '../../../core/models/entreprise.model';

export interface EntrepriseDialogData {
  entreprise?: Entreprise;
  isEditMode: boolean;
}

@Component({
  selector: 'app-entreprise-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './entreprise-dialog.html',
  styleUrl: './entreprise-dialog.scss'
})
export class EntrepriseDialogComponent implements OnInit {
  entrepriseForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<EntrepriseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EntrepriseDialogData,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.isEditMode = data.isEditMode;
    this.entrepriseForm = this.createForm();
  }

  ngOnInit(): void {
    if (this.isEditMode && this.data.entreprise) {
      this.populateForm(this.data.entreprise);
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      nom: ['', [Validators.required]],
      siret: ['', [Validators.required, Validators.pattern(/^\d{14}$/)]],
      adresse: ['', [Validators.required]],
      ville: ['', [Validators.required]],
      code_postal: ['', [Validators.required]],
      telephone: [''],
      email: ['', [Validators.email]],
      contact_rh_nom: [''],
      contact_rh_email: ['', [Validators.email]],
      contact_rh_telephone: [''],
      is_active: [true]
    });
  }

  private populateForm(entreprise: Entreprise): void {
    this.entrepriseForm.patchValue({
      nom: entreprise.nom,
      siret: entreprise.siret,
      adresse: entreprise.adresse,
      ville: entreprise.ville,
      code_postal: entreprise.code_postal,
      telephone: entreprise.telephone || '',
      email: entreprise.email || '',
      contact_rh_nom: entreprise.contact_rh_nom || '',
      contact_rh_email: entreprise.contact_rh_email || '',
      contact_rh_telephone: entreprise.contact_rh_telephone || '',
      is_active: entreprise.is_active
    });
  }

  onSave(): void {
    if (this.entrepriseForm.valid) {
      this.isLoading = true;
      const formData = { ...this.entrepriseForm.value };
      
      // Nettoyer les données vides
      Object.keys(formData).forEach(key => {
        if (formData[key] === '' || formData[key] === null) {
          delete formData[key];
        }
      });

      const request = this.isEditMode 
        ? this.entrepriseService.updateEntreprise(this.data.entreprise!.id, formData)
        : this.entrepriseService.createEntreprise(formData);

      request.subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.dialogRef.close(response.entreprise);
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