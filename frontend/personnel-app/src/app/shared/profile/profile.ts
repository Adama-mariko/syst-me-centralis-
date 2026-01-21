import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { AuthService } from '../../core/services/auth.service';
import { ApiService } from '../../core/services/api.service';
import { EntrepriseService } from '../../core/services/entreprise.service';
import { User } from '../../core/models/user.model';
import { Entreprise } from '../../core/models/entreprise.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.scss'
})
export class ProfileComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  
  profileForm: FormGroup;
  currentUser: User | null = null;
  entreprises: Entreprise[] = [];
  isEditing = false;
  isLoading = false;
  hidePassword = true;
  hideConfirmPassword = true;
  selectedFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ProfileComponent>,
    private authService: AuthService,
    private apiService: ApiService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar
  ) {
    this.profileForm = this.createForm();
  }

  ngOnInit(): void {
    // Récupérer l'utilisateur connecté
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.populateForm(user);
      }
    });

    // Charger les entreprises pour l'affichage
    this.loadEntreprises();
  }

  private createForm(): FormGroup {
    const form = this.fb.group({
      prenom: ['', [Validators.required]],
      nom: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      newPassword: ['', [Validators.minLength(6)]],
      confirmPassword: ['']
    });

    // Validator pour vérifier que les mots de passe correspondent
    form.setValidators(this.passwordMatchValidator);
    return form;
  }

  private passwordMatchValidator(control: AbstractControl): {[key: string]: any} | null {
    const newPassword = control.get('newPassword');
    const confirmPassword = control.get('confirmPassword');
    
    if (newPassword && confirmPassword && newPassword.value && 
        newPassword.value !== confirmPassword.value) {
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
    this.profileForm.patchValue({
      prenom: user.prenom,
      nom: user.nom,
      email: user.email,
      newPassword: '',
      confirmPassword: ''
    });
  }

  getRoleIcon(role: string): string {
    switch (role) {
      case 'admin':
        return 'admin_panel_settings';
      case 'rh_entreprise':
        return 'business_center';
      default:
        return 'person';
    }
  }

  getRoleLabel(role: string): string {
    switch (role) {
      case 'admin':
        return 'Administrateur';
      case 'rh_entreprise':
        return 'RH Entreprise';
      default:
        return role;
    }
  }

  getEntrepriseName(entrepriseId: number): string {
    const entreprise = this.entreprises.find(e => e.id === entrepriseId);
    return entreprise?.nom || 'Non assigné';
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      // Réinitialiser le formulaire si on annule
      if (this.currentUser) {
        this.populateForm(this.currentUser);
      }
    }
  }

  onSave(): void {
    if (this.profileForm.valid && this.currentUser) {
      this.isLoading = true;
      const formData = { ...this.profileForm.value };
      
      // Supprimer les champs de mot de passe s'ils sont vides
      if (!formData.newPassword) {
        delete formData.newPassword;
        delete formData.confirmPassword;
      } else {
        // Renommer newPassword en password pour l'API
        formData.password = formData.newPassword;
        delete formData.newPassword;
        delete formData.confirmPassword;
      }

      this.apiService.put<{user: User, message: string}>(`/admin/users/${this.currentUser.id}`, formData)
        .subscribe({
          next: (response) => {
            this.isLoading = false;
            this.isEditing = false;
            this.snackBar.open(response.message, 'Fermer', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
            
            // Mettre à jour l'utilisateur connecté
            this.authService.getCurrentUser().subscribe();
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
    if (this.isEditing) {
      this.toggleEdit();
    } else {
      this.dialogRef.close();
    }
  }

  changeAvatar(): void {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      
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
        this.snackBar.open('La taille du fichier ne doit pas dépasser 5MB', 'Fermer', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        return;
      }

      this.selectedFile = file;
      this.uploadAvatar();
    }
  }

  private uploadAvatar(): void {
    if (!this.selectedFile || !this.currentUser) {
      console.log('DEBUG: Pas de fichier sélectionné ou pas d\'utilisateur');
      return;
    }

    console.log('DEBUG: Début upload avatar');
    console.log('DEBUG: Fichier:', this.selectedFile.name, 'Taille:', this.selectedFile.size);
    console.log('DEBUG: User ID:', this.currentUser.id);

    this.isLoading = true;
    const formData = new FormData();
    formData.append('avatar', this.selectedFile);

    console.log('DEBUG: FormData créé, envoi vers:', `/admin/users/${this.currentUser.id}/avatar`);

    this.apiService.post<{avatar_url: string, message: string}>(`/admin/users/${this.currentUser.id}/avatar`, formData)
      .subscribe({
        next: (response) => {
          console.log('DEBUG: Réponse reçue:', response);
          this.isLoading = false;
          this.snackBar.open(response.message, 'Fermer', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          
          // Mettre à jour l'avatar de l'utilisateur
          if (this.currentUser) {
            this.currentUser.avatar_url = response.avatar_url;
          }
          
          // Rafraîchir les données utilisateur
          this.authService.getCurrentUser().subscribe();
        },
        error: (error) => {
          console.error('DEBUG: Erreur upload:', error);
          this.isLoading = false;
          const message = error.error?.message || 'Erreur lors du téléchargement de l\'image';
          this.snackBar.open(message, 'Fermer', {
            duration: 4000,
            panelClass: ['error-snackbar']
          });
        }
      });
  }
}