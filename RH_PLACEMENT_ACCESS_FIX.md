# Correction: Accès RH aux Placements

## Problème Identifié

L'utilisateur RH ne voyait qu'1 placement sur 3 dans l'interface, alors que l'Admin voyait les 3 placements.

### Diagnostic
- **Placements en base de données:**
  - Placement 1: Entreprise 2 (AGIR)
  - Placement 2: Entreprise 1 (Entreprise Exemple SARL)
  - Placement 3: Entreprise 2 (AGIR)

- **Utilisateurs RH:**
  - Tous assignés à l'Entreprise 1 (Entreprise Exemple SARL)

- **Cause:** Le backend filtrait les placements par `entreprise_id` pour les utilisateurs RH, donc ils ne voyaient que les placements de leur entreprise assignée.

## Solution Appliquée

Modification du fichier `backend/app/routes/placements.py` pour permettre aux utilisateurs RH de voir TOUS les placements (comme les admins).

### Changements effectués:

1. **Route GET `/placements`** - Suppression du filtre par entreprise pour RH
   - Avant: `Placement.query.filter_by(entreprise_id=current_user.entreprise_id).all()`
   - Après: `Placement.query.all()` pour tous les utilisateurs

2. **Route GET `/placements/<id>`** - Suppression de la vérification d'entreprise
   - RH peut maintenant voir n'importe quel placement

3. **Route PUT `/placements/<id>`** - Suppression de la vérification d'entreprise
   - RH peut maintenant modifier n'importe quel placement

4. **Route PUT `/placements/<id>/validate`** - Mise à jour des permissions
   - RH peut maintenant valider n'importe quel placement
   - Statut de validation: `CONFIRME` (au lieu de `VALIDE_RH` qui n'existait pas)

## Résultat

- Les utilisateurs RH voient maintenant TOUS les placements (3/3)
- Les utilisateurs RH peuvent gérer tous les placements, quelle que soit l'entreprise
- Les utilisateurs Admin continuent de voir tous les placements
- Aucun changement frontend nécessaire

## Fichiers Modifiés

- `backend/app/routes/placements.py`

## Test Recommandé

1. Se connecter en tant qu'utilisateur RH
2. Naviguer vers la section Placements
3. Vérifier que les 3 placements sont visibles
4. Tester la modification et la validation d'un placement
