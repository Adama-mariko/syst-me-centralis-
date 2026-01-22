import { Component, Inject } from '@angular/core';
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
import { MatSnackBar } from '@angular/material/snack-bar';
import { RapportService } from '../../../core/services/rapport.service';
import { EntrepriseService } from '../../../core/services/entreprise.service';

@Component({
  selector: 'app-rapport-dialog',
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
    MatProgressSpinnerModule
  ],
  template: `
    <div class="rapport-dialog">
      <h2 mat-dialog-title>
        <mat-icon>assessment</mat-icon>
        {{ getTitle() }}
      </h2>

      <mat-dialog-content>
        <form [formGroup]="rapportForm" *ngIf="data.type !== 'view'">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Date de début</mat-label>
            <input matInput [matDatepicker]="pickerDebut" formControlName="periode_debut">
            <mat-datepicker-toggle matSuffix [for]="pickerDebut"></mat-datepicker-toggle>
            <mat-datepicker #pickerDebut></mat-datepicker>
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Date de fin</mat-label>
            <input matInput [matDatepicker]="pickerFin" formControlName="periode_fin">
            <mat-datepicker-toggle matSuffix [for]="pickerFin"></mat-datepicker-toggle>
            <mat-datepicker #pickerFin></mat-datepicker>
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width" *ngIf="entreprises.length > 0">
            <mat-label>Entreprise (optionnel)</mat-label>
            <mat-select formControlName="entreprise_id">
              <mat-option value="">Toutes les entreprises</mat-option>
              <mat-option *ngFor="let entreprise of entreprises" [value]="entreprise.id">
                {{ entreprise.nom }}
              </mat-option>
            </mat-select>
          </mat-form-field>
        </form>

        <div *ngIf="data.type === 'view' && data.donnees" class="rapport-data">
          <h3>Statistiques</h3>
          <pre>{{ data.donnees | json }}</pre>
        </div>
      </mat-dialog-content>

      <mat-dialog-actions>
        <button mat-stroked-button mat-dialog-close>Annuler</button>
        <button mat-raised-button color="primary" (click)="onSubmit()" 
                [disabled]="rapportForm.invalid || isLoading" *ngIf="data.type !== 'view'">
          <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
          Générer
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .rapport-dialog {
      .full-width {
        width: 100%;
        margin-bottom: 16px;
      }
      
      .rapport-data {
        max-height: 400px;
        overflow-y: auto;
        
        pre {
          background: #f5f5f5;
          padding: 16px;
          border-radius: 4px;
          font-size: 12px;
        }
      }
    }
  `]
})
export class RapportDialogComponent {
  rapportForm!: FormGroup;
  isLoading = false;
  entreprises: any[] = [];

  constructor(
    private fb: FormBuilder,
    private rapportService: RapportService,
    private entrepriseService: EntrepriseService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<RapportDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.rapportForm = this.fb.group({
      periode_debut: ['', Validators.required],
      periode_fin: ['', Validators.required],
      entreprise_id: ['']
    });

    this.loadEntreprises();
  }

  loadEntreprises(): void {
    this.entrepriseService.getEntreprises().subscribe({
      next: (response) => {
        this.entreprises = response.entreprises;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des entreprises:', error);
      }
    });
  }

  getTitle(): string {
    if (this.data.type === 'view') {
      return 'Détails du Rapport';
    }
    return this.data.type === 'placements' ? 'Rapport des Placements' : 'Rapport des Absences';
  }

  onSubmit(): void {
    if (this.rapportForm.valid) {
      this.isLoading = true;
      const formValue = this.rapportForm.value;
      
      const data = {
        periode_debut: this.formatDate(formValue.periode_debut),
        periode_fin: this.formatDate(formValue.periode_fin),
        entreprise_id: formValue.entreprise_id || undefined
      };

      const request = this.data.type === 'placements' 
        ? this.rapportService.genererRapportPlacements(data)
        : this.rapportService.genererRapportAbsences(data);

      request.subscribe({
        next: (response) => {
          this.dialogRef.close(true);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Erreur lors de la génération du rapport:', error);
          this.snackBar.open('Erreur lors de la génération du rapport', 'Fermer', {
            duration: 3000
          });
          this.isLoading = false;
        }
      });
    }
  }

  formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }
}