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
  providers: [provideNativeDateAdapter()],
  templateUrl: './placement-dialog.html',
  styleUrl: './placement-dialog.scss'
})
export class PlacementDialogComponent implements OnInit {
  placementForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;
  collaborateurs: Collaborateur[] = [];
  entreprises: Entreprise[] = [];
  selectedFile: File | null = null;
  documentPreview: string | null = null;
  existingDocumentUrl: string | null = null;

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
    const form = this.fb.group({
      collaborateur_id: ['', [Validators.required]],
      entreprise_id: ['', [Validators.required]],
      poste_demande: ['', [Validators.required, Validators.minLength(2)]],
      date_debut: [null, [Validators.required]], // Utiliser null au lieu de chaîne vide
      date_fin: [null], // Utiliser null au lieu de chaîne vide
      salaire_propose: ['', [Validators.required, Validators.min(0)]],
      statut: ['en_attente', [Validators.required]],
      description: [''],
      commentaires: ['']
    });

    return form;
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
      poste_demande: placement.poste_demande,
      date_debut: placement.date_debut,
      date_fin: placement.date_fin || '',
      salaire_propose: placement.salaire_propose,
      statut: placement.statut,
      description: placement.description || '',
      commentaires: placement.commentaires || ''
    });
    
    // Stocker l'URL du document existant
    if (placement.document_url) {
      this.existingDocumentUrl = placement.document_url;
      this.documentPreview = placement.document_url;
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Vérifier le type de fichier (PDF, Word, images)
      const allowedTypes = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'image/jpeg', 'image/png', 'image/jpg'];
      
      if (!allowedTypes.includes(file.type)) {
        this.snackBar.open('Type de fichier non autorisé. Utilisez PDF, Word ou images.', 'Fermer', {
          duration: 4000,
          panelClass: ['error-snackbar']
        });
        return;
      }
      
      // Vérifier la taille (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.snackBar.open('Le fichier est trop volumineux (max 5MB)', 'Fermer', {
          duration: 4000,
          panelClass: ['error-snackbar']
        });
        return;
      }
      
      this.selectedFile = file;
      this.documentPreview = file.name;
    }
  }

  removeDocument(): void {
    this.selectedFile = null;
    this.documentPreview = null;
    this.existingDocumentUrl = null;
  }

  isImage(url: string): boolean {
    if (!url) return false;
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    return imageExtensions.some(ext => url.toLowerCase().endsWith(ext));
  }

  getFileName(url: string): string {
    if (!url) return '';
    const parts = url.split('/');
    return parts[parts.length - 1];
  }

  onSave(): void {
    if (this.placementForm.valid) {
      this.isLoading = true;
      
      const formValue = this.placementForm.value;
      
      // Créer un FormData pour envoyer le fichier
      const formData = new FormData();
      formData.append('collaborateur_id', formValue.collaborateur_id.toString());
      formData.append('entreprise_id', formValue.entreprise_id.toString());
      formData.append('poste_demande', formValue.poste_demande);
      
      // Convertir les dates au format ISO
      if (formValue.date_debut) {
        const dateDebut = new Date(formValue.date_debut);
        formData.append('date_debut', dateDebut.toISOString().split('T')[0]);
      }
      if (formValue.date_fin) {
        const dateFin = new Date(formValue.date_fin);
        formData.append('date_fin', dateFin.toISOString().split('T')[0]);
      }
      
      formData.append('salaire_propose', formValue.salaire_propose.toString());
      formData.append('statut', formValue.statut);
      if (formValue.description) {
        formData.append('description', formValue.description);
      }
      if (formValue.commentaires) {
        formData.append('commentaires', formValue.commentaires);
      }
      
      // Ajouter le fichier s'il y en a un
      if (this.selectedFile) {
        formData.append('document', this.selectedFile);
      }
      
      const request = this.isEditMode 
        ? this.placementService.updatePlacementWithFile(this.data.placement!.id, formData)
        : this.placementService.createPlacementWithFile(formData);

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
    } else {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.placementForm.controls).forEach(key => {
        this.placementForm.get(key)?.markAsTouched();
      });
      
      this.snackBar.open('Veuillez corriger les erreurs dans le formulaire', 'Fermer', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  // Méthode pour débugger l'état du formulaire
  checkFormStatus(): void {
    console.log('=== FORM STATUS ===');
    console.log('Form valid:', this.placementForm.valid);
    console.log('Form value:', this.placementForm.value);
    
    Object.keys(this.placementForm.controls).forEach(key => {
      const control = this.placementForm.get(key);
      console.log(`${key}:`, {
        value: control?.value,
        valid: control?.valid,
        errors: control?.errors,
        touched: control?.touched,
        dirty: control?.dirty
      });
    });
  }

  // Méthodes pour ouvrir les calendriers manuellement
  openStartDatePicker(picker: any): void {
    picker.open();
  }

  openEndDatePicker(picker: any): void {
    picker.open();
  }
}