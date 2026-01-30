import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { map, catchError, of, take, filter, switchMap } from 'rxjs';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  // Si l'utilisateur n'est pas encore chargé, le charger d'abord
  const currentUser = authService.getCurrentUserValue();
  if (!currentUser) {
    return authService.getCurrentUser().pipe(
      map(() => true),
      catchError(() => {
        router.navigate(['/login']);
        return of(false);
      })
    );
  }

  return true;
};

export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  // Vérifier si l'utilisateur est déjà chargé
  const currentUser = authService.getCurrentUserValue();
  
  if (!currentUser) {
    // Charger l'utilisateur et attendre le résultat
    return authService.getCurrentUser().pipe(
      switchMap(() => authService.currentUser$),
      filter(user => user !== null),
      take(1),
      map(user => {
        if (user && user.role === 'admin') {
          return true;
        }
        // Si pas admin, rediriger vers RH ou login
        if (user && user.role === 'rh_entreprise') {
          router.navigate(['/rh/dashboard']);
        } else {
          router.navigate(['/login']);
        }
        return false;
      }),
      catchError(() => {
        router.navigate(['/login']);
        return of(false);
      })
    );
  }

  // Utilisateur déjà chargé, vérifier le rôle
  if (currentUser.role === 'admin') {
    return true;
  }

  // Rediriger selon le rôle
  if (currentUser.role === 'rh_entreprise') {
    router.navigate(['/rh/dashboard']);
  } else {
    router.navigate(['/login']);
  }
  return false;
};

export const rhGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  // Vérifier si l'utilisateur est déjà chargé
  const currentUser = authService.getCurrentUserValue();
  
  if (!currentUser) {
    // Charger l'utilisateur et attendre le résultat
    return authService.getCurrentUser().pipe(
      switchMap(() => authService.currentUser$),
      filter(user => user !== null),
      take(1),
      map(user => {
        if (user && user.role === 'rh_entreprise') {
          return true;
        }
        // Si pas RH, rediriger vers admin ou login
        if (user && user.role === 'admin') {
          router.navigate(['/admin/dashboard']);
        } else {
          router.navigate(['/login']);
        }
        return false;
      }),
      catchError(() => {
        router.navigate(['/login']);
        return of(false);
      })
    );
  }

  // Utilisateur déjà chargé, vérifier le rôle
  if (currentUser.role === 'rh_entreprise') {
    return true;
  }

  // Rediriger selon le rôle
  if (currentUser.role === 'admin') {
    router.navigate(['/admin/dashboard']);
  } else {
    router.navigate(['/login']);
  }
  return false;
};