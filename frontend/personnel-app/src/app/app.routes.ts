import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login';
import { LayoutComponent } from './shared/layout/layout';
import { DashboardComponent } from './admin/dashboard/dashboard';
import { CollaborateursComponent } from './admin/collaborateurs/collaborateurs';
import { EntreprisesComponent } from './admin/entreprises/entreprises';
import { UsersComponent } from './admin/users/users';
import { AbsencesComponent } from './admin/absences/absences';
import { RapportsComponent } from './admin/rapports/rapports';
import { PlacementsComponent } from './admin/placements/placements';
import { RemplacementsComponent } from './admin/remplacements/remplacements';
import { TracabiliteComponent } from './admin/tracabilite/tracabilite';
import { ValidationsComponent } from './rh/validations/validations';
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
          { path: 'placements', component: PlacementsComponent },
          { path: 'remplacements', component: RemplacementsComponent },
          { path: 'tracabilite', component: TracabiliteComponent },
          { path: 'mouvements', component: TracabiliteComponent }, // Alias
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
          { path: 'placements', component: PlacementsComponent },
          { path: 'validations', component: ValidationsComponent },
          { path: 'tracabilite', component: TracabiliteComponent },
          { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
        ]
      }
    ]
  }
];