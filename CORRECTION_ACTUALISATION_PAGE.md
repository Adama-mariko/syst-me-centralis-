# Correction du problème d'actualisation de page

## Date : 29 janvier 2026

## Problème identifié
Lorsqu'un utilisateur Admin actualisait le navigateur sur une page admin (ex: `/admin/collaborateurs`), il était redirigé vers l'interface RH (`/rh/dashboard`) au lieu de rester sur la même page.

## Cause du problème
Les guards `adminGuard` et `rhGuard` ne géraient pas correctement le cas où l'utilisateur n'était pas encore chargé lors de l'actualisation :

1. **Chargement asynchrone** : Lors de l'actualisation, l'utilisateur n'est pas immédiatement disponible dans le `BehaviorSubject`
2. **Décision prématurée** : Les guards laissaient passer temporairement (`return true`) sans attendre le chargement complet
3. **Redirection incorrecte** : Une fois l'utilisateur chargé, une redirection incorrecte se produisait

## Solution appliquée

### 1. Ajout de `getCurrentUserValue()` dans `AuthService`
```typescript
getCurrentUserValue(): User | null {
  return this.currentUserSubject.value;
}
```
Cette méthode permet d'obtenir la valeur synchrone de l'utilisateur actuel.

### 2. Modification des guards pour attendre le chargement

**Avant** :
```typescript
// Laissait passer temporairement sans vérifier
if (!user) {
  authService.getCurrentUser().subscribe();
  return true; // ❌ Problème ici
}
```

**Après** :
```typescript
// Vérifie d'abord si l'utilisateur est déjà chargé
const currentUser = authService.getCurrentUserValue();

if (!currentUser) {
  // Charge l'utilisateur et ATTEND le résultat avant de décider
  return authService.getCurrentUser().pipe(
    switchMap(() => authService.currentUser$),
    filter(user => user !== null),
    take(1),
    map(user => {
      // Vérifie le rôle et redirige si nécessaire
      if (user && user.role === 'admin') {
        return true;
      }
      // Redirection appropriée selon le rôle
      if (user && user.role === 'rh_entreprise') {
        router.navigate(['/rh/dashboard']);
      } else {
        router.navigate(['/login']);
      }
      return false;
    })
  );
}

// Si déjà chargé, vérification immédiate
if (currentUser.role === 'admin') {
  return true;
}
```

### 3. Gestion des redirections selon le rôle

- **Admin** accédant à une route RH → redirigé vers `/admin/dashboard`
- **RH** accédant à une route Admin → redirigé vers `/rh/dashboard`
- **Non authentifié** → redirigé vers `/login`

## Fichiers modifiés

1. `frontend/personnel-app/src/app/core/guards/auth.guard.ts`
   - Modification de `authGuard`
   - Modification de `adminGuard`
   - Modification de `rhGuard`

2. `frontend/personnel-app/src/app/core/services/auth.service.ts`
   - Ajout de `getCurrentUserValue()`

## Résultat attendu

✅ Un utilisateur Admin qui actualise une page admin reste sur cette page
✅ Un utilisateur RH qui actualise une page RH reste sur cette page
✅ Les redirections se font correctement selon le rôle
✅ Pas de déconnexion lors de l'actualisation

## Test à effectuer

1. Se connecter en tant qu'Admin
2. Naviguer vers `/admin/collaborateurs`
3. Actualiser le navigateur (F5)
4. **Résultat attendu** : Rester sur `/admin/collaborateurs`

5. Se connecter en tant qu'RH
6. Naviguer vers `/rh/validations`
7. Actualiser le navigateur (F5)
8. **Résultat attendu** : Rester sur `/rh/validations`
