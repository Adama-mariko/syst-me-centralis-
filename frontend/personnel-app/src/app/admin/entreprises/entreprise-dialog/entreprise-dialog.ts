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
  selectedLogoUrl: string | null = null;
  selectedLogoFile: File | null = null;

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
      // Charger le logo existant si il existe
      if (this.data.entreprise.logo_url) {
        console.log('Logo existant trouvé:', this.data.entreprise.logo_url);
      }
    }
  }

  // Nouvelle méthode pour gérer la sélection de logo
  onLogoSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      console.log('Logo sélectionné:', file.name, file.type, file.size);
      
      // Vérifier le type de fichier
      if (!file.type.startsWith('image/')) {
        this.snackBar.open('Veuillez sélectionner un fichier image valide', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        return;
      }

      // Vérifier la taille du fichier (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.snackBar.open('La taille de l\'image ne doit pas dépasser 5MB', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        return;
      }

      this.selectedLogoFile = file;

      // Créer une URL de prévisualisation
      const reader = new FileReader();
      reader.onload = (e: any) => {
        console.log('Logo chargé, URL:', e.target.result?.substring(0, 50) + '...');
        this.selectedLogoUrl = e.target.result;
      };
      reader.onerror = (error) => {
        console.error('Erreur lors de la lecture du fichier:', error);
        this.snackBar.open('Erreur lors de la lecture du fichier', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
      };
      reader.readAsDataURL(file);
    } else {
      console.log('Aucun fichier sélectionné');
    }
  }

  // Nouvelle méthode pour supprimer le logo
  removeLogo(): void {
    this.selectedLogoUrl = null;
    this.selectedLogoFile = null;
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
      
      // Créer FormData pour l'upload de fichier
      const formData = new FormData();
      
      // Ajouter les données du formulaire
      Object.keys(this.entrepriseForm.value).forEach(key => {
        const value = this.entrepriseForm.value[key];
        if (value !== '' && value !== null && value !== undefined) {
          formData.append(key, value);
        }
      });

      // Ajouter le logo si il est sélectionné
      if (this.selectedLogoFile) {
        formData.append('logo', this.selectedLogoFile);
      }

      const request = this.isEditMode 
        ? this.entrepriseService.updateEntrepriseWithLogo(this.data.entreprise!.id, formData)
        : this.entrepriseService.createEntrepriseWithLogo(formData);

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

  getLogoUrl(logoUrl: string | undefined): string {
    if (!logoUrl) return '';
    // Si l'URL commence déjà par http, la retourner telle quelle
    if (logoUrl.startsWith('http')) {
      return logoUrl;
    }
    // Sinon, construire l'URL complète avec le backend
    return `http://localhost:5000${logoUrl}`;
  }
}