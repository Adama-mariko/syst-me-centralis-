# Upload de Documents pour les Placements

## Fonctionnalité Ajoutée

Vous pouvez maintenant uploader des documents (contrats, lettres de mission, etc.) lors de la création ou modification d'un placement.

## Modifications Apportées

### Backend

#### 1. Modèle Placement (`backend/app/models/placement.py`)
- Ajout du champ `document_url` pour stocker l'URL du document

#### 2. Routes Placement (`backend/app/routes/placements.py`)
- Ajout de la fonction `save_document()` pour gérer l'upload
- Modification de `create_placement()` pour accepter FormData avec fichier
- Modification de `update_placement()` pour accepter FormData avec fichier
- Gestion de la suppression de l'ancien document lors de la mise à jour

#### 3. Dossier de Stockage
- Création du dossier `backend/uploads/placements/` pour stocker les documents

### Frontend

#### 1. Modèle Placement (`frontend/.../placement.model.ts`)
- Ajout du champ `document_url?: string`

#### 2. Service Placement (`frontend/.../placement.service.ts`)
- Ajout de `createPlacementWithFile(formData: FormData)`
- Ajout de `updatePlacementWithFile(id, formData: FormData)`

#### 3. Dialog Placement (`frontend/.../placement-dialog/`)
- Ajout de l'input file avec bouton stylisé
- Ajout de la prévisualisation du fichier sélectionné
- Ajout de la validation du type et de la taille du fichier
- Ajout du bouton pour supprimer le fichier sélectionné

## Utilisation

### Créer un Placement avec Document

1. Cliquez sur "Nouveau placement"
2. Remplissez le formulaire
3. Dans la section "Document", cliquez sur "Choisir un fichier"
4. Sélectionnez un fichier (PDF, Word, ou image)
5. Le nom du fichier s'affiche avec une icône
6. Cliquez sur "Créer"

### Modifier un Placement et Changer le Document

1. Cliquez sur "Modifier" sur un placement existant
2. Si un document existe déjà, son nom s'affiche
3. Cliquez sur "Choisir un fichier" pour remplacer le document
4. Ou cliquez sur l'icône "X" pour supprimer le document
5. Cliquez sur "Modifier"

## Formats Acceptés

- **PDF** : `.pdf`
- **Word** : `.doc`, `.docx`
- **Images** : `.jpg`, `.jpeg`, `.png`

## Taille Maximale

- **5 MB** par fichier

## Validation

Le système vérifie automatiquement :
- ✅ Le type de fichier (formats autorisés uniquement)
- ✅ La taille du fichier (max 5MB)
- ✅ L'existence du fichier

Si le fichier ne respecte pas ces critères, un message d'erreur s'affiche.

## Stockage

Les documents sont stockés dans :
```
backend/uploads/placements/
```

Chaque fichier est renommé avec un UUID unique pour éviter les conflits :
```
{uuid}.{extension}
```

Exemple : `a1b2c3d4e5f6.pdf`

## URL du Document

L'URL du document est stockée dans la base de données :
```
/uploads/placements/{uuid}.{extension}
```

Cette URL peut être utilisée pour télécharger ou afficher le document.

## Interface Utilisateur

### Section Document

La section "Document" apparaît dans le formulaire de placement avec :

1. **Bouton "Choisir un fichier"**
   - Style moderne avec bordure en pointillés
   - Icône d'upload
   - Effet hover avec animation

2. **Prévisualisation du Fichier**
   - Icône de document
   - Nom du fichier
   - Bouton pour supprimer (icône X)
   - Fond vert clair pour indiquer la sélection

3. **Indication des Formats**
   - Message informatif avec icône
   - Liste des formats acceptés
   - Taille maximale

## Migration de la Base de Données

Un script de migration a été créé pour ajouter la colonne `document_url` :

```bash
cd backend
python add_document_placement.py
```

Ou exécutez le SQL directement :
```sql
ALTER TABLE placements ADD COLUMN document_url VARCHAR(255) DEFAULT NULL;
```

## Sécurité

- ✅ Validation du type de fichier côté serveur
- ✅ Validation de la taille du fichier
- ✅ Noms de fichiers sécurisés avec UUID
- ✅ Vérification des permissions utilisateur
- ✅ Suppression de l'ancien document lors du remplacement

## Prochaines Étapes

Pour utiliser cette fonctionnalité :

1. **Exécutez la migration** pour ajouter la colonne à la base de données
2. **Redémarrez le backend** si nécessaire
3. **Actualisez le frontend** (déjà compilé automatiquement)
4. **Testez** en créant un nouveau placement avec un document

Le projet est déjà en cours d'exécution, donc actualisez simplement la page pour voir les changements !
