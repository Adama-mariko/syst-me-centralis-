import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialog } from '@angular/material/dialog';
import { RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from '../../core/services/auth.service';
import { User } from '../../core/models/user.model';
import { ProfileComponent } from '../profile/profile';
import { SettingsComponent } from '../settings/settings';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule,
    MatBadgeModule,
    MatDividerModule
  ],
  templateUrl: './layout.html',
  styleUrl: './layout.scss'
})
export class LayoutComponent implements OnInit {
  currentUser: User | null = null;
  pageTitle = 'Tableau de bord';
  
  // État des sous-menus
  expandedMenus = {
    entreprises: false,
    collaborateurs: false,
    rapports: false
  };

  private pageTitles: { [key: string]: string } = {
    '/admin/dashboard': 'Tableau de bord Admin',
    '/admin/users': 'Gestion des utilisateurs',
    '/admin/entreprises': 'Gestion des entreprises',
    '/admin/collaborateurs': 'Gestion des collaborateurs',
    '/admin/absences': 'Gestion des absences',
    '/admin/rapports': 'Rapports et statistiques',
    '/admin/placements': 'Gestion des placements',
    '/admin/remplacements': 'Gestion des remplacements',
    '/admin/mouvements': 'Traçabilité des mouvements',
    '/admin/notifications': 'Centre de notifications',
    '/admin/competences': 'Gestion des compétences',
    '/rh/dashboard': 'Tableau de bord RH',
    '/rh/collaborateurs': 'Mes collaborateurs',
    '/rh/absences': 'Gestion des absences',
    '/rh/placements': 'Placements',
    '/rh/validations': 'Validations'
  };

  constructor(
    private authService: AuthService,
    private router: Router,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    // S'abonner aux changements d'utilisateur
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    // Mettre à jour le titre de la page selon la route
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.pageTitle = this.pageTitles[event.url] || 'Personnel Manager';
      });
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isRH(): boolean {
    return this.authService.isRH();
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

  // Nouvelle fonction pour basculer les sous-menus
  toggleMenu(menuName: keyof typeof this.expandedMenus): void {
    // Fermer tous les autres menus
    Object.keys(this.expandedMenus).forEach(key => {
      if (key !== menuName) {
        this.expandedMenus[key as keyof typeof this.expandedMenus] = false;
      }
    });
    // Basculer le menu sélectionné
    this.expandedMenus[menuName] = !this.expandedMenus[menuName];
  }

  // Nouvelle fonction pour naviguer
  navigateTo(route: string): void {
    // Vérifier que la route existe avant de naviguer
    if (route && route.length > 0) {
      this.router.navigate([route]).catch(error => {
        console.error('Erreur de navigation:', error);
        // En cas d'erreur, rediriger vers le dashboard approprié
        const fallbackRoute = this.isAdmin() ? '/admin/dashboard' : '/rh/dashboard';
        this.router.navigate([fallbackRoute]);
      });
    }
  }

  // Nouvelle fonction pour vérifier si une route est active
  isRouteActive(route: string): boolean {
    if (!route) return false;
    return this.router.url.startsWith(route);
  }

  openProfile(): void {
    const dialogRef = this.dialog.open(ProfileComponent, {
      width: '600px',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe(result => {
      // Optionnel: traiter le résultat si nécessaire
      if (result) {
        console.log('Profil mis à jour:', result);
      }
    });
  }

  openSettings(): void {
    const dialogRef = this.dialog.open(SettingsComponent, {
      width: '700px',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe(result => {
      // Optionnel: traiter les nouveaux paramètres
      if (result) {
        console.log('Paramètres mis à jour:', result);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}