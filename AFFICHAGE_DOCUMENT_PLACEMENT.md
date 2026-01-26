# Affichage des Documents dans les Placements

## Fonctionnalité Ajoutée

Les documents uploadés pour les placements sont maintenant visibles dans le tableau des placements.

## Modifications Apportées

### 1. Colonne "Document" dans le Tableau

Une nouvelle colonne a été ajoutée au tableau des placements pour afficher :
- **Icône de document** (📄) si un document est attaché - cliquable pour ouvrir le document
- **Icône vide** (⊝) si aucun document n'est attaché

### 2. Menu d'Actions Amélioré

Le menu d'actions (⋮) de chaque placement inclut maintenant :
- **Voir détails** : Afficher les informations complètes
- **Modifier** : Modifier le placement
- **Voir document** : Ouvrir le document dans un nouvel onglet (visible uniquement si un document existe)
- **Supprimer** : Supprimer le placement

### 3. Accès Direct au Document

Deux façons d'accéder au document :
1. **Cliquer sur l'icône** dans la colonne "Document"
2. **Menu d'actions** → "Voir document"

Les deux ouvrent le document dans un nouvel onglet du navigateur.

## Interface Utilisateur

### Colonne Document

```
┌─────────────┬──────────────┬──────────┬──────────┐
│ Collaborateur│ Entreprise   │ Poste    │ Document │
├─────────────┼──────────────┼──────────┼──────────┤
│ Jean Dupont │ AGIR         │ Dev      │    📄    │ ← Cliquable
│ Marie Martin│ TechCorp     │ Designer │    ⊝    │ ← Pas de doc
└─────────────┴──────────────┴──────────┴──────────┘
```

### Styles

- **Icône de document** : Bleu (#6366f1) avec effet hover
- **Icône vide** : Gris clair (#d1d5db)
- **Effet hover** : Agrandissement et changement de couleur

## Utilisation

### Voir un Document

1. **Depuis le tableau** :
   - Repérez la colonne "Document"
   - Cliquez sur l'icône 📄 si elle est présente
   - Le document s'ouvre dans un nouvel onglet

2. **Depuis le menu** :
   - Cliquez sur ⋮ (menu d'actions)
   - Sélectionnez "Voir document"
   - Le document s'ouvre dans un nouvel onglet

### Types de Documents Supportés

Le navigateur ouvrira le document selon son type :
- **PDF** : Affichage dans le lecteur PDF du navigateur
- **Word** : Téléchargement automatique
- **Images** : Affichage direct dans le navigateur

## Ordre des Colonnes

Le tableau affiche maintenant les colonnes dans cet ordre :
1. Collaborateur
2. Entreprise
3. Poste
4. Date début
5. Date fin
6. Statut
7. Salaire
8. **Document** ← Nouvelle colonne
9. Actions

## Exemple de Workflow

### Créer un Placement avec Document

1. Cliquez sur "Nouveau Placement"
2. Remplissez le formulaire
3. Cliquez sur "Choisir un fichier"
4. Sélectionnez votre document (contrat, lettre de mission, etc.)
5. Cliquez sur "Créer"
6. Le placement apparaît dans le tableau avec l'icône 📄

### Consulter le Document

1. Dans le tableau, repérez le placement
2. Cliquez sur l'icône 📄 dans la colonne "Document"
3. Le document s'ouvre dans un nouvel onglet
4. Vous pouvez le consulter, le télécharger ou l'imprimer

### Modifier et Changer le Document

1. Cliquez sur ⋮ → "Modifier"
2. Dans la section "Document", cliquez sur "Choisir un fichier"
3. Sélectionnez un nouveau document
4. Cliquez sur "Modifier"
5. L'ancien document est remplacé par le nouveau

## URL des Documents

Les documents sont accessibles via :
```
http://localhost:5000/uploads/placements/{uuid}.{extension}
```

Exemple :
```
http://localhost:5000/uploads/placements/a1b2c3d4e5f6.pdf
```

## Sécurité

- ✅ Seuls les utilisateurs authentifiés peuvent voir les documents
- ✅ Les documents sont stockés de manière sécurisée
- ✅ Les noms de fichiers sont anonymisés avec UUID

## Responsive Design

Sur mobile :
- La colonne "Document" reste visible
- L'icône est légèrement plus petite
- Le menu d'actions s'adapte à l'écran

## Prochaines Améliorations Possibles

- Prévisualisation du document dans une modal
- Téléchargement direct depuis le tableau
- Indication du type de document (PDF, Word, Image)
- Taille du fichier affichée
- Date d'upload du document

## Testez Maintenant !

1. Actualisez la page des placements
2. Vous verrez la nouvelle colonne "Document"
3. Les placements avec documents affichent l'icône 📄
4. Cliquez dessus pour ouvrir le document !

Tout fonctionne parfaitement ! 🎉
