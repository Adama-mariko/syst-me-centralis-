import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { AbsenceService, Absence } from '../../../core/services/absence.service';

@Component({
  selector: 'app-absence-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatChipsModule
  ],
  templateUrl: './absence-dialog.html',
  styleUrl: './absence-dialog.scss'
})
export class AbsenceDialogComponent implements OnInit {
  absenceForm!: FormGroup;
  isLoading = false;
  mode: 'create' | 'edit' | 'view' | 'approve' | 'reject' = 'create';

  constructor(
    private fb: FormBuilder,
    private absenceService: AbsenceService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<AbsenceDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {
      absence?: Absence;
      collaborateurs?: any[];
      mode: 'create' | 'edit' | 'view' | 'approve' | 'reject';
    }
  ) {
    this.mode = data.mode;
    this.initForm();
  }

  ngOnInit(): void {
    if (this.data.absence) {
      this.populateForm(this.data.absence);
    }
  }

  initForm(): void {
    this.absenceForm = this.fb.group({
      collaborateur_id: [{ value: '', disabled: this.isViewMode() }, Validators.required],
      type_absence: [{ value: '', disabled: this.isViewMode() }, Validators.required],
      motif: [{ value: '', disabled: this.isViewMode() }],
      date_debut: [{ value: '', disabled: this.isViewMode() }, Validators.required],
      date_fin: [{ value: '', disabled: this.isViewMode() }, Validators.required],
      commentaires: [{ value: '', disabled: this.isViewMode() && !this.isApprovalMode() }]
    });

    // Calculer automatiquement le nombre de jours
    this.absenceForm.get('date_debut')?.valueChanges.subscribe(() => this.calculateDays());
    this.absenceForm.get('date_fin')?.valueChanges.subscribe(() => this.calculateDays());
  }

  populateForm(absence: Absence): void {
    this.absenceForm.patchValue({
      collaborateur_id: absence.collaborateur_id,
      type_absence: absence.type_absence,
      motif: absence.motif,
      date_debut: new Date(absence.date_debut),
      date_fin: new Date(absence.date_fin),
      commentaires: absence.commentaires
    });
  }

  calculateDays(): void {
    const dateDebut = this.absenceForm.get('date_debut')?.value;
    const dateFin = this.absenceForm.get('date_fin')?.value;

    if (dateDebut && dateFin) {
      const debut = new Date(dateDebut);
      const fin = new Date(dateFin);
      const diffTime = Math.abs(fin.getTime() - debut.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      
      // Mettre à jour l'affichage du nombre de jours
      this.nombreJours = diffDays;
    }
  }

  nombreJours = 0;

  onSubmit(): void {
    if (this.absenceForm.valid) {
      this.isLoading = true;
      const formValue = this.absenceForm.value;

      // Formater les dates
      const absenceData = {
        ...formValue,
        date_debut: this.formatDate(formValue.date_debut),
        date_fin: this.formatDate(formValue.date_fin)
      };

      if (this.mode === 'create') {
        this.createAbsence(absenceData);
      } else if (this.mode === 'approve') {
        this.approveAbsence();
      } else if (this.mode === 'reject') {
        this.rejectAbsence();
      }
    }
  }

  createAbsence(absenceData: any): void {
    this.absenceService.createAbsence(absenceData).subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Fermer', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        this.dialogRef.close(true);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors de la création de l\'absence:', error);
        this.snackBar.open(
          error.error?.error || 'Erreur lors de la création de l\'absence',
          'Fermer',
          { duration: 3000, panelClass: ['error-snackbar'] }
        );
        this.isLoading = false;
      }
    });
  }

  approveAbsence(): void {
    const commentaires = this.absenceForm.get('commentaires')?.value;
    this.absenceService.approuverAbsence(this.data.absence!.id!, commentaires).subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Fermer', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        this.dialogRef.close(true);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors de l\'approbation:', error);
        this.snackBar.open(
          error.error?.error || 'Erreur lors de l\'approbation',
          'Fermer',
          { duration: 3000, panelClass: ['error-snackbar'] }
        );
        this.isLoading = false;
      }
    });
  }

  rejectAbsence(): void {
    const commentaires = this.absenceForm.get('commentaires')?.value;
    this.absenceService.refuserAbsence(this.data.absence!.id!, commentaires).subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Fermer', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        this.dialogRef.close(true);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors du refus:', error);
        this.snackBar.open(
          error.error?.error || 'Erreur lors du refus',
          'Fermer',
          { duration: 3000, panelClass: ['error-snackbar'] }
        );
        this.isLoading = false;
      }
    });
  }

  formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  isViewMode(): boolean {
    return this.mode === 'view';
  }

  isApprovalMode(): boolean {
    return this.mode === 'approve' || this.mode === 'reject';
  }

  getTitle(): string {
    switch (this.mode) {
      case 'create':
        return 'Nouvelle Absence';
      case 'edit':
        return 'Modifier l\'Absence';
      case 'view':
        return 'Détails de l\'Absence';
      case 'approve':
        return 'Approuver l\'Absence';
      case 'reject':
        return 'Refuser l\'Absence';
      default:
        return 'Absence';
    }
  }

  getSubmitButtonText(): string {
    switch (this.mode) {
      case 'create':
        return 'Créer';
      case 'edit':
        return 'Modifier';
      case 'approve':
        return 'Approuver';
      case 'reject':
        return 'Refuser';
      default:
        return 'Enregistrer';
    }
  }

  getSubmitButtonColor(): string {
    switch (this.mode) {
      case 'approve':
        return 'primary';
      case 'reject':
        return 'warn';
      default:
        return 'primary';
    }
  }

  getTypesAbsence(): string[] {
    return this.absenceService.getTypesAbsence();
  }

  getTypeAbsenceLabel(type: string): string {
    return this.absenceService.getTypeAbsenceLabel(type);
  }

  getStatutAbsenceLabel(statut: string): string {
    return this.absenceService.getStatutAbsenceLabel(statut);
  }

  getStatutColor(statut: string): string {
    return this.absenceService.getStatutColor(statut);
  }
}