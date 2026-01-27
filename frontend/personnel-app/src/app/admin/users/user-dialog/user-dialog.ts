import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { ApiService } from '../../../core/services/api.service';
import { EntrepriseService } from '../../../core/services/entreprise.service';
import { User } from '../../../core/models/user.model';
import { Entreprise } from '../../../core/models/entreprise.model';

export interface UserDialogData {
  user?: User;
  isEditMode: boolean;
}

@Component({
  selector: 'app-user-dialog',
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
    MatSlideToggleModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './user-dialog.html',
  styleUrl: './user-dialog.scss'
})
export class UserDialogComponent implements OnInit {
  userForm: FormGroup;
  isEditMode: boolean;
  isLoading = false;
  hidePassword = true;
  hideConfirmPassword = true;
  showEntrepriseField = false;
  entreprises: Entreprise[] = [];
  
  // Avatar
  avatarFile: File | null = null;
  avatarPreview: string | null = null;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<UserDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: UserDialogData,
    private apiService: ApiService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.isEditMode = data.isEditMode;
    this.userForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadEntreprises();
    
    if (this.isEditMode && this.data.user) {
      this.populateForm(this.data.user);
    }
  }

  private createForm(): FormGroup {
    const formConfig: any = {
      prenom: ['', [Validators.required]],
      nom: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      role: ['', [Validators.required]],
      entreprise_id: [''],
      is_active: [true]
    };

    // Ajouter les champs de mot de passe uniquement en mode création
    if (!this.isEditMode) {
      formConfig.password = ['', [Validators.required, Validators.minLength(6)]];
      formConfig.confirmPassword = ['', [Validators.required]];
    }

    const form = this.fb.group(formConfig);
    
    // Validator personnalisé pour vérifier que les mots de passe correspondent
    if (!this.isEditMode) {
      form.setValidators(this.passwordMatchValidator);
    }

    return form;
  }

  private passwordMatchValidator(control: AbstractControl): {[key: string]: any} | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { 'passwordMismatch': true };
    }
    return null;
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

  private populateForm(user: User): void {
    this.userForm.patchValue({
      prenom: user.prenom,
      nom: user.nom,
      email: user.email,
      role: user.role,
      entreprise_id: user.entreprise_id || '',
      is_active: user.is_active
    });

    // Charger l'avatar existant
    if (user.avatar_url) {
      this.avatarPreview = user.avatar_url;
    }

    // Déclencher la logique d'affichage du champ entreprise
    this.onRoleChange();
  }

  onAvatarSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Vérifier le type de fichier
      if (!file.type.startsWith('image/')) {
        this.snackBar.open('Veuillez sélectionner une image', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        return;
      }

      // Vérifier la taille (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.snackBar.open('L\'image ne doit pas dépasser 5MB', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        return;
      }

      this.avatarFile = file;

      // Créer un aperçu
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.avatarPreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  removeAvatar(): void {
    this.avatarFile = null;
    this.avatarPreview = null;
  }

  onRoleChange(): void {
    const role = this.userForm.get('role')?.value;
    this.showEntrepriseField = role === 'rh_entreprise';
    
    const entrepriseControl = this.userForm.get('entreprise_id');
    if (this.showEntrepriseField) {
      entrepriseControl?.setValidators([Validators.required]);
    } else {
      entrepriseControl?.clearValidators();
      entrepriseControl?.setValue('');
    }
    entrepriseControl?.updateValueAndValidity();
  }

  onSave(): void {
    if (this.userForm.valid) {
      this.isLoading = true;
      const formData = { ...this.userForm.value };
      
      // Nettoyer les données
      if (!formData.entreprise_id) {
        delete formData.entreprise_id;
      }
      
      // Supprimer confirmPassword des données envoyées
      if (formData.confirmPassword) {
        delete formData.confirmPassword;
      }

      const request = this.isEditMode 
        ? this.apiService.put<{user: User, message: string}>(`/admin/users/${this.data.user!.id}`, formData)
        : this.apiService.post<{user: User, message: string}>('/admin/users', formData);

      request.subscribe({
        next: (response) => {
          // Si un avatar a été sélectionné, l'uploader séparément
          if (this.avatarFile) {
            this.uploadAvatar(response.user.id);
          } else {
            this.isLoading = false;
            this.snackBar.open(response.message, 'Fermer', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
            this.dialogRef.close(response.user);
          }
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

  private uploadAvatar(userId: number): void {
    const formData = new FormData();
    formData.append('avatar', this.avatarFile!);

    this.apiService.post<{user: User, message: string}>(`/admin/users/${userId}/avatar`, formData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.snackBar.open('Utilisateur et avatar sauvegardés avec succès', 'Fermer', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        // Mettre à jour l'aperçu avec la nouvelle URL
        this.avatarPreview = response.user.avatar_url || null;
        this.dialogRef.close(response.user);
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open('Utilisateur créé mais erreur lors de l\'upload de l\'avatar', 'Fermer', {
          duration: 4000,
          panelClass: ['error-snackbar']
        });
        // Fermer quand même le dialog car l'utilisateur est créé
        this.dialogRef.close();
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}