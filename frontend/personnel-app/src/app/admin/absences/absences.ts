import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { AbsenceService, Absence } from '../../core/services/absence.service';
import { CollaborateurService } from '../../core/services/collaborateur.service';
import { AbsenceDialogComponent } from './absence-dialog/absence-dialog';

@Component({
  selector: 'app-absences',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule
  ],
  templateUrl: './absences.html',
  styleUrl: './absences.scss'
})
export class AbsencesComponent implements OnInit {
  displayedColumns: string[] = [
    'collaborateur',
    'type_absence',
    'periode',
    'nombre_jours',
    'statut',
    'demandeur',
    'date_creation',
    'actions'
  ];

  absences: Absence[] = [];
  totalAbsences = 0;
  currentPage = 1;
  pageSize = 10;
  isLoading = false;

  filterForm: FormGroup;
  collaborateurs: any[] = [];

  constructor(
    private absenceService: AbsenceService,
    private collaborateurService: CollaborateurService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private fb: FormBuilder
  ) {
    this.filterForm = this.fb.group({
      statut: [''],
      type_absence: [''],
      collaborateur_id: [''],
      date_debut: [''],
      date_fin: ['']
    });
  }

  ngOnInit(): void {
    this.loadAbsences();
    this.loadCollaborateurs();
    
    // Écouter les changements de filtres
    this.filterForm.valueChanges.subscribe(() => {
      this.currentPage = 1;
      this.loadAbsences();
    });
  }

  loadAbsences(): void {
    this.isLoading = true;
    const filters = this.getActiveFilters();

    this.absenceService.getAbsences(this.currentPage, this.pageSize, filters)
      .subscribe({
        next: (response) => {
          this.absences = response.absences;
          this.totalAbsences = response.total;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Erreur lors du chargement des absences:', error);
          this.snackBar.open('Erreur lors du chargement des absences', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
          this.isLoading = false;
        }
      });
  }

  loadCollaborateurs(): void {
    this.collaborateurService.getCollaborateurs().subscribe({
      next: (response) => {
        this.collaborateurs = response.collaborateurs;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des collaborateurs:', error);
      }
    });
  }

  getActiveFilters(): any {
    const formValue = this.filterForm.value;
    const filters: any = {};

    Object.keys(formValue).forEach(key => {
      if (formValue[key] && formValue[key] !== '') {
        if (key === 'date_debut' || key === 'date_fin') {
          filters[key] = formValue[key].toISOString().split('T')[0];
        } else {
          filters[key] = formValue[key];
        }
      }
    });

    return filters;
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadAbsences();
  }

  clearFilters(): void {
    this.filterForm.reset();
  }

  openAbsenceDialog(absence?: Absence): void {
    const dialogRef = this.dialog.open(AbsenceDialogComponent, {
      width: '600px',
      data: {
        absence: absence || null,
        collaborateurs: this.collaborateurs,
        mode: absence ? 'edit' : 'create'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadAbsences();
      }
    });
  }

  approuverAbsence(absence: Absence): void {
    const dialogRef = this.dialog.open(AbsenceDialogComponent, {
      width: '500px',
      data: {
        absence,
        mode: 'approve'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadAbsences();
      }
    });
  }

  refuserAbsence(absence: Absence): void {
    const dialogRef = this.dialog.open(AbsenceDialogComponent, {
      width: '500px',
      data: {
        absence,
        mode: 'reject'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadAbsences();
      }
    });
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

  getTypesAbsence(): string[] {
    return this.absenceService.getTypesAbsence();
  }

  getStatutsAbsence(): string[] {
    return this.absenceService.getStatutsAbsence();
  }

  formatPeriode(absence: Absence): string {
    const debut = new Date(absence.date_debut).toLocaleDateString('fr-FR');
    const fin = new Date(absence.date_fin).toLocaleDateString('fr-FR');
    return `${debut} - ${fin}`;
  }

  canApprove(absence: Absence): boolean {
    return absence.statut === 'en_attente';
  }

  canReject(absence: Absence): boolean {
    return absence.statut === 'en_attente';
  }
}