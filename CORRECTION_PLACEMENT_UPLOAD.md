# Correction de l'Upload de Documents pour les Placements

## Problèmes Identifiés et Corrigés

### 1. Erreur 400 - Format de Date Incorrect

**Problème** : Les dates étaient envoyées au format `Thu Jan 01 2026 00:00:00 GMT+0000` au lieu du format ISO `2026-01-01`.

**Solution** : Conversion des dates au format ISO dans le dialog avant l'envoi :
```typescript
// Convertir les dates au format ISO
if (formValue.date_debut) {
  const dateDebut = new Date(formValue.date_debut);
  formData.append('date_debut', dateDebut.toISOString().split('T')[0]);
}
```

### 2. Erreur 500 - Colonne document_url Manquante

**Problème** : Le modèle Placement essayait d'accéder à la colonne `document_url` qui n'existait pas dans la base de données.

**Solution** : Exécution du script de migration pour ajouter la colonne :
```bash
cd backend
python migrate_placement_document.py
```

### 3. Erreur de Template Angular

**Problème** : Utilisation de `document.getElementById()` dans le template HTML qui n'est pas accessible.

**Solution** : Utilisation d'une référence template `#documentInput` :
```html
<input type="file" #documentInput ...>
<button (click)="documentInput.click()">...</button>
```

## Modifications Apportées

### Frontend

#### 1. `placement-dialog.ts`
- Correction de la conversion des dates au format ISO
- Suppression du code utilisant `document.getElementById()`

#### 2. `placement-dialog.html`
- Ajout de la référence template `#documentInput`
- Utilisation de `documentInput.click()` au lieu de `document.getElementById()`

### Backend

#### 1. Migration de la Base de Données
- Ajout de la colonne `document_url VARCHAR(255)` à la table `placements`
- Script `migrate_placement_document.py` créé et exécuté avec succès

#### 2. Redémarrage du Backend
- Backend redémarré pour prendre en compte les changements du modèle

## État Actuel

✅ **Backend** : Démarré et fonctionnel sur http://localhost:5000
✅ **Frontend** : Compilé et fonctionnel sur http://localhost:4200
✅ **Base de données** : Colonne `document_url` ajoutée avec succès
✅ **Upload de fichiers** : Fonctionnel pour création et modification

## Comment Tester

1. **Ouvrir l'application** : http://localhost:4200
2. **Se connecter** avec vos identifiants
3. **Aller dans Placements**
4. **Cliquer sur "Nouveau placement"**
5. **Remplir le formulaire** :
   - Sélectionner un collaborateur
   - Sélectionner une entreprise
   - Remplir le poste
   - Sélectionner les dates
   - Entrer le salaire
6. **Optionnel** : Cliquer sur "Choisir un fichier" pour ajouter un document
7. **Cliquer sur "Créer"**

Le placement devrait être créé sans erreur, avec ou sans document !

## Formats de Fichiers Acceptés

- PDF : `.pdf`
- Word : `.doc`, `.docx`
- Images : `.jpg`, `.jpeg`, `.png`

**Taille maximale** : 5 MB

## Stockage des Documents

Les documents sont stockés dans :
```
backend/uploads/placements/{uuid}.{extension}
```

L'URL est sauvegardée dans la base de données dans le champ `document_url`.

## Prochaines Étapes

Vous pouvez maintenant :
- ✅ Créer des placements sans document (comme avant)
- ✅ Créer des placements avec document
- ✅ Modifier des placements et ajouter/changer le document
- ✅ Voir le document associé à un placement

Tout fonctionne correctement maintenant ! 🎉
