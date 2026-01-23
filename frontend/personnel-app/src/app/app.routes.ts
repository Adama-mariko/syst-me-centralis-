import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login';
import { LayoutComponent } from './shared/layout/layout';
import { DashboardComponent } from './admin/dashboard/dashboard';
import { CollaborateursComponent } from './admin/collaborateurs/collaborateurs';
import { EntreprisesComponent } from './admin/entreprises/entreprises';
import { UsersComponent } from './admin/users/users';
import { AbsencesComponent } from './admin/absences/absences';
import { RapportsComponent } from './admin/rapports/rapports';
import { authGuard, adminGuard, rhGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'admin',
        canActivate: [adminGuard],
        children: [
          { path: 'dashboard', component: DashboardComponent },
          { path: 'collaborateurs', component: CollaborateursComponent },
          { path: 'entreprises', component: EntreprisesComponent },
          { path: 'users', component: UsersComponent },
          { path: 'absences', component: AbsencesComponent },
          { path: 'rapports', component: RapportsComponent },
          { path: 'placements', component: DashboardComponent }, // TODO: Créer le composant
          { path: 'remplacements', component: DashboardComponent }, // TODO: Créer le composant
          { path: 'mouvements', component: DashboardComponent }, // TODO: Créer le composant
          { path: 'notifications', component: DashboardComponent }, // TODO: Créer le composant
          { path: 'competences', component: DashboardComponent }, // TODO: Créer le composant
          { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
        ]
      },
      {
        path: 'rh',
        canActivate: [rhGuard],
        children: [
          { path: 'dashboard', component: DashboardComponent },
          { path: 'collaborateurs', component: CollaborateursComponent },
          { path: 'entreprises', component: EntreprisesComponent },
          { path: 'absences', component: AbsencesComponent },
          { path: 'placements', component: DashboardComponent }, // TODO: Créer le composant
          { path: 'validations', component: DashboardComponent }, // TODO: Créer le composant
          { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
        ]
      }
    ]
  }
];