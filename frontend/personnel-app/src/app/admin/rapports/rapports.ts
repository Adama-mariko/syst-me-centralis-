import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatGridListModule } from '@angular/material/grid-list';
import { RapportService, Rapport, Statistiques } from '../../core/services/rapport.service';
import { RapportDialogComponent } from './rapport-dialog/rapport-dialog';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-rapports',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatPaginatorModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatGridListModule
  ],
  templateUrl: './rapports.html',
  styleUrl: './rapports.scss'
})
export class RapportsComponent implements OnInit {
  displayedColumns: string[] = [
    'titre',
    'type_rapport',
    'periode',
    'statut',
    'generateur',
    'date_creation',
    'actions'
  ];

  rapports: Rapport[] = [];
  totalRapports = 0;
  currentPage = 1;
  pageSize = 10;
  isLoading = false;

  statistiques: Statistiques | null = null;
  isLoadingStats = false;

  constructor(
    private rapportService: RapportService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadRapports();
    this.loadStatistiques();
  }

  loadRapports(): void {
    this.isLoading = true;
    this.rapportService.getRapports(this.currentPage, this.pageSize)
      .subscribe({
        next: (response) => {
          this.rapports = response.rapports;
          this.totalRapports = response.total;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Erreur lors du chargement des rapports:', error);
          this.snackBar.open('Erreur lors du chargement des rapports', 'Fermer', {
            duration: 3000,
            panelClass: ['error-snackbar']
          });
          this.isLoading = false;
        }
      });
  }

  loadStatistiques(): void {
    this.isLoadingStats = true;
    this.rapportService.getStatistiquesGlobales()
      .subscribe({
        next: (response) => {
          this.statistiques = response.statistiques;
          this.isLoadingStats = false;
          this.createEvolutionChart();
        },
        error: (error) => {
          console.error('Erreur lors du chargement des statistiques:', error);
          this.isLoadingStats = false;
        }
      });
  }

  createEvolutionChart(): void {
    if (!this.statistiques?.evolution_mensuelle) return;

    setTimeout(() => {
      const canvas = document.getElementById('evolutionChart') as HTMLCanvasElement;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.statistiques!.evolution_mensuelle.map(item => item.mois),
          datasets: [
            {
              label: 'Placements',
              data: this.statistiques!.evolution_mensuelle.map(item => item.placements),
              borderColor: '#6366f1',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              tension: 0.4,
              fill: true
            },
            {
              label: 'Absences',
              data: this.statistiques!.evolution_mensuelle.map(item => item.absences),
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              tension: 0.4,
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: 'Évolution mensuelle (6 derniers mois)'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }, 100);
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadRapports();
  }

  openRapportDialog(type: 'placements' | 'absences'): void {
    const dialogRef = this.dialog.open(RapportDialogComponent, {
      width: '600px',
      data: { type }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadRapports();
        this.snackBar.open('Rapport généré avec succès', 'Fermer', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
      }
    });
  }

  downloadRapport(rapport: Rapport): void {
    if (rapport.statut !== 'genere') {
      this.snackBar.open('Le rapport n\'est pas encore généré', 'Fermer', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    this.rapportService.downloadCSV(rapport);
  }

  viewRapportDetails(rapport: Rapport): void {
    if (!rapport.donnees_json) {
      this.snackBar.open('Aucune donnée disponible pour ce rapport', 'Fermer', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    try {
      const donnees = JSON.parse(rapport.donnees_json);
      const dialogRef = this.dialog.open(RapportDialogComponent, {
        width: '800px',
        data: { 
          type: 'view',
          rapport,
          donnees
        }
      });
    } catch (error) {
      this.snackBar.open('Erreur lors de l\'affichage des données', 'Fermer', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  getTypeRapportLabel(type: string): string {
    return this.rapportService.getTypeRapportLabel(type);
  }

  getStatutRapportLabel(statut: string): string {
    return this.rapportService.getStatutRapportLabel(statut);
  }

  getStatutColor(statut: string): string {
    return this.rapportService.getStatutColor(statut);
  }

  formatPeriode(rapport: Rapport): string {
    const debut = new Date(rapport.periode_debut).toLocaleDateString('fr-FR');
    const fin = new Date(rapport.periode_fin).toLocaleDateString('fr-FR');
    return `${debut} - ${fin}`;
  }

  canDownload(rapport: Rapport): boolean {
    return rapport.statut === 'genere';
  }

  canView(rapport: Rapport): boolean {
    return rapport.statut === 'genere' && !!rapport.donnees_json;
  }
}