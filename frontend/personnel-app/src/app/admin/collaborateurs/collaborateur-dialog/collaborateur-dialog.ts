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
import { MatSnackBar } from '@angular/material/snack-bar';

import { CollaborateurService } from '../../../core/services/collaborateur.service';
import { EntrepriseService } from '../../../core/services/entreprise.service';
import { Collaborateur } from '../../../core/models/collaborateur.model';
import { Entreprise } from '../../../core/models/entreprise.model';

export interface CollaborateurDialogData {
  collaborateur?: Collaborateur;
  isEditMode: boolean;
}

@Component({
  selector: 'app-collaborateur-dialog',
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
    MatProgressSpinnerModule
  ],
  templateUrl: './collaborateur-dialog.html',
  styleUrl: './collaborateur-dialog.scss'
})
export class CollaborateurDialogComponent implements OnInit {
  collaborateurForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;
  entreprises: Entreprise[] = [];
  selectedImageUrl: string | null = null;
  selectedImageFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<CollaborateurDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CollaborateurDialogData,
    private collaborateurService: CollaborateurService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.isEditMode = data.isEditMode;
    this.collaborateurForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadEntreprises();
    
    if (this.isEditMode && this.data.collaborateur) {
      this.populateForm(this.data.collaborateur);
      // Charger l'image existante si elle existe
      if (this.data.collaborateur.photo_url) {
        // Ne pas définir selectedImageUrl pour l'image existante, 
        // elle sera affichée via getImageUrl dans le template
        console.log('Image existante trouvée:', this.data.collaborateur.photo_url);
      }
    }
  }

  // Nouvelle méthode pour gérer la sélection d'image
  onImageSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      console.log('Fichier sélectionné:', file.name, file.type, file.size);
      
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

      this.selectedImageFile = file;

      // Créer une URL de prévisualisation
      const reader = new FileReader();
      reader.onload = (e: any) => {
        console.log('Image chargée, URL:', e.target.result?.substring(0, 50) + '...');
        this.selectedImageUrl = e.target.result;
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

  // Nouvelle méthode pour supprimer l'image
  removeImage(): void {
    this.selectedImageUrl = null;
    this.selectedImageFile = null;
  }

  private createForm(): FormGroup {
    return this.fb.group({
      prenom: ['', [Validators.required]],
      nom: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      telephone: [''],
      date_naissance: [''],
      adresse: [''],
      ville: [''],
      code_postal: [''],
      poste: ['', [Validators.required]],
      date_embauche: ['', [Validators.required]],
      competences: [''],
      salaire: [''],
      entreprise_actuelle_id: [''],
      statut: ['actif']
    });
  }

  private loadEntreprises(): void {
    this.entrepriseService.getEntreprises().subscribe({
      next: (response) => {
        this.entreprises = response.entreprises;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des entreprises:', error);
      }
    });
  }

  private populateForm(collaborateur: Collaborateur): void {
    this.collaborateurForm.patchValue({
      prenom: collaborateur.prenom,
      nom: collaborateur.nom,
      email: collaborateur.email,
      telephone: collaborateur.telephone || '',
      date_naissance: collaborateur.date_naissance || '',
      adresse: collaborateur.adresse || '',
      ville: collaborateur.ville || '',
      code_postal: collaborateur.code_postal || '',
      poste: collaborateur.poste,
      date_embauche: collaborateur.date_embauche,
      competences: collaborateur.competences || '',
      salaire: collaborateur.salaire || '',
      entreprise_actuelle_id: collaborateur.entreprise_actuelle_id || '',
      statut: collaborateur.statut
    });
  }

  onSave(): void {
    if (this.collaborateurForm.valid) {
      this.isLoading = true;
      
      // Créer FormData pour l'upload de fichier
      const formData = new FormData();
      
      // Ajouter les données du formulaire
      Object.keys(this.collaborateurForm.value).forEach(key => {
        const value = this.collaborateurForm.value[key];
        if (value !== '' && value !== null && value !== undefined) {
          formData.append(key, value);
        }
      });

      // Ajouter l'image si elle est sélectionnée
      if (this.selectedImageFile) {
        formData.append('photo', this.selectedImageFile);
      }

      const request = this.isEditMode 
        ? this.collaborateurService.updateCollaborateurWithPhoto(this.data.collaborateur!.id, formData)
        : this.collaborateurService.createCollaborateurWithPhoto(formData);

      request.subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.dialogRef.close(response.collaborateur);
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