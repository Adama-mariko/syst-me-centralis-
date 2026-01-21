import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

Chart.register(...registerables);

interface DashboardStats {
  collaborateurs: number;
  entreprises: number;
  placements: number;
  validations_en_attente: number;
}

interface StatusDistribution {
  label: string;
  count: number;
  percentage: number;
  color: string;
}

interface RecentActivity {
  title: string;
  description: string;
  time: string;
  type: string;
  icon: string;
}

interface PendingValidation {
  id: number;
  title: string;
  description: string;
  type: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class DashboardComponent implements OnInit, AfterViewInit {
  @ViewChild('placementsChart') placementsChart!: ElementRef<HTMLCanvasElement>;

  stats: DashboardStats = {
    collaborateurs: 156,
    entreprises: 23,
    placements: 89,
    validations_en_attente: 7
  };

  statusDistribution: StatusDistribution[] = [
    { label: 'Actifs', count: 142, percentage: 91, color: '#10b981' },
    { label: 'En congé', count: 8, percentage: 5, color: '#f59e0b' },
    { label: 'Arrêt maladie', count: 4, percentage: 3, color: '#ef4444' },
    { label: 'Inactifs', count: 2, percentage: 1, color: '#6b7280' }
  ];

  recentActivities: RecentActivity[] = [
    {
      title: 'Nouveau placement validé',
      description: 'Jean Dupont placé chez TechCorp',
      time: 'Il y a 2 heures',
      type: 'placement',
      icon: 'assignment'
    },
    {
      title: 'Collaborateur validé',
      description: 'Marie Martin validée par RH',
      time: 'Il y a 4 heures',
      type: 'validation',
      icon: 'check_circle'
    },
    {
      title: 'Entreprise modifiée',
      description: 'Informations de contact mises à jour',
      time: 'Il y a 6 heures',
      type: 'modification',
      icon: 'edit'
    },
    {
      title: 'Nouveau remplacement',
      description: 'Remplacement planifié pour congés',
      time: 'Il y a 1 jour',
      type: 'placement',
      icon: 'swap_horiz'
    }
  ];

  pendingValidations: PendingValidation[] = [
    {
      id: 1,
      title: 'Placement en attente',
      description: 'Pierre Durand - Développeur chez WebAgency',
      type: 'placement'
    },
    {
      id: 2,
      title: 'Nouveau collaborateur',
      description: 'Sophie Leblanc - Designer',
      type: 'collaborateur'
    },
    {
      id: 3,
      title: 'Modification salaire',
      description: 'Augmentation pour Marc Rousseau',
      type: 'modification'
    }
  ];

  private chart: Chart | null = null;

  constructor() {}

  ngOnInit(): void {
    // Charger les données du dashboard
    this.loadDashboardData();
  }

  ngAfterViewInit(): void {
    this.createPlacementsChart();
  }

  private loadDashboardData(): void {
    // Ici, vous feriez des appels API pour récupérer les vraies données
    // Pour la démo, nous utilisons des données statiques
  }

  private createPlacementsChart(): void {
    const ctx = this.placementsChart.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
        datasets: [
          {
            label: 'Placements',
            data: [12, 19, 15, 25, 22, 30],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Validations',
            data: [8, 15, 12, 20, 18, 25],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
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
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#f1f5f9'
            }
          },
          x: {
            grid: {
              color: '#f1f5f9'
            }
          }
        }
      }
    };

    this.chart = new Chart(ctx, config);
  }

  validateItem(item: PendingValidation): void {
    console.log('Validation de:', item);
    // Ici, vous feriez un appel API pour valider l'élément
    this.pendingValidations = this.pendingValidations.filter(p => p.id !== item.id);
  }

  rejectItem(item: PendingValidation): void {
    console.log('Rejet de:', item);
    // Ici, vous feriez un appel API pour rejeter l'élément
    this.pendingValidations = this.pendingValidations.filter(p => p.id !== item.id);
  }
}