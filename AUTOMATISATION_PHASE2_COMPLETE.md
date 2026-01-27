# Automatisation des Tâches Administratives - Phase 2

## ✅ PHASE 2 TERMINÉE: Tâches Planifiées et Mise à Jour Automatique

### 📋 Ce qui a été implémenté:

#### 1. **Scheduler APScheduler Installé et Configuré**

**Bibliothèque:** APScheduler 3.10.4
- Scheduler en arrière-plan (BackgroundScheduler)
- Intégré au démarrage de l'application Flask
- 5 tâches planifiées actives

#### 2. **Tâches Automatiques Planifiées**

**Tâche 1: Mise à jour automatique des statuts**
- ⏰ **Quand:** Chaque jour à 8h00
- 🎯 **Actions:**
  - Placements qui commencent aujourd'hui → Statut "En cours"
  - Placements qui se terminent aujourd'hui → Statut "Terminé"
  - Remplacements qui commencent → Statut "En cours"
  - Remplacements qui se terminent → Statut "Terminé"
  - Collaborateurs qui reviennent d'absence → Statut "Actif"
- 📝 **Traçabilité:** Chaque changement est enregistré dans les mouvements

**Tâche 2: Rappels placements expirant bientôt**
- ⏰ **Quand:** Chaque jour à 8h30
- 🎯 **Actions:**
  - Détecte les placements se terminant dans 7 jours
  - Envoie notification aux admins
  - Permet d'anticiper les renouvellements

**Tâche 3: Rappels validations en attente**
- ⏰ **Quand:** Chaque jour à 9h00
- 🎯 **Actions:**
  - Placements en attente depuis plus de 48h
  - Absences en attente depuis plus de 24h
  - Envoie rappels aux RH

**Tâche 4: Rapport hebdomadaire**
- ⏰ **Quand:** Chaque lundi à 9h00
- 🎯 **Actions:**
  - Statistiques des 7 derniers jours
  - Placements créés
  - Remplacements créés
  - Absences demandées
  - Envoi aux admins

**Tâche 5: Rapport mensuel**
- ⏰ **Quand:** 1er du mois à 9h00
- 🎯 **Actions:**
  - Statistiques du mois écoulé
  - Placements créés
  - Remplacements créés
  - Absences demandées
  - Envoi aux admins

#### 3. **Routes API pour Gérer les Tâches**

**Routes admin uniquement:**

```
GET  /api/scheduler/jobs
     → Liste des tâches planifiées avec prochaine exécution

POST /api/scheduler/jobs/{job_id}/execute
     → Exécuter une tâche immédiatement (pour tests)

POST /api/scheduler/update-statuts
     → Mettre à jour les statuts maintenant (pour tests)

POST /api/scheduler/rappels-placements
     → Envoyer les rappels maintenant (pour tests)

POST /api/scheduler/rapport-hebdomadaire
     → Générer le rapport hebdomadaire maintenant

POST /api/scheduler/rapport-mensuel
     → Générer le rapport mensuel maintenant
```

#### 4. **Service SchedulerService**

**Méthodes principales:**
```python
SchedulerService.init_scheduler(app)
    → Initialiser et démarrer le scheduler

SchedulerService.mettre_a_jour_statuts(app)
    → Mise à jour automatique des statuts

SchedulerService.envoyer_rappels_placements(app)
    → Envoyer rappels placements expirant

SchedulerService.envoyer_rappels_validations(app)
    → Envoyer rappels validations en attente

SchedulerService.generer_rapport_hebdomadaire(app)
    → Générer rapport hebdomadaire

SchedulerService.generer_rapport_mensuel(app)
    → Générer rapport mensuel

SchedulerService.get_jobs_info()
    → Récupérer infos sur les tâches

SchedulerService.executer_maintenant(job_id, app)
    → Exécuter une tâche immédiatement
```

---

## 🎯 EXEMPLES D'UTILISATION

### Exemple 1: Mise à jour automatique des statuts

**Scénario:**
- Aujourd'hui: 27 janvier 2026
- Placement A: date_debut = 27/01/2026, statut = "Confirmé"
- Placement B: date_fin = 27/01/2026, statut = "En cours"

**À 8h00 automatiquement:**
- Placement A → Statut "En cours"
- Placement B → Statut "Terminé"
- Mouvements enregistrés dans la traçabilité
- Logs dans la console

### Exemple 2: Rappel placement expirant

**Scénario:**
- Aujourd'hui: 27 janvier 2026
- Placement C: date_fin = 03/02/2026 (dans 7 jours)

**À 8h30 automatiquement:**
- Notification envoyée aux admins
- Message: "Le placement de Jean Martin chez AGIR expire dans 7 jours"
- Permet d'anticiper le renouvellement

### Exemple 3: Rapport hebdomadaire

**Scénario:**
- Lundi 27 janvier 2026

**À 9h00 automatiquement:**
- Calcul des statistiques des 7 derniers jours
- Génération du rapport
- Envoi aux admins (TODO: email)

---

## 📊 LOGS ET MONITORING

Le scheduler génère des logs détaillés:

```
INFO:apscheduler.scheduler:Scheduler started
INFO:app.services.scheduler_service:✅ Scheduler démarré avec succès
INFO:app.services.scheduler_service:📅 Tâches planifiées: 5

INFO:app.services.scheduler_service:🔄 Début de la mise à jour automatique des statuts...
INFO:app.services.scheduler_service:✓ Placement 5 démarré
INFO:app.services.scheduler_service:✓ Placement 3 terminé
INFO:app.services.scheduler_service:✅ Mise à jour terminée:
INFO:app.services.scheduler_service:   - 2 placements démarrés
INFO:app.services.scheduler_service:   - 1 placements terminés
INFO:app.services.scheduler_service:   - 0 remplacements démarrés
INFO:app.services.scheduler_service:   - 0 remplacements terminés
INFO:app.services.scheduler_service:   - 0 collaborateurs de retour
```

---

## 🧪 TESTS RECOMMANDÉS

### Test 1: Vérifier les tâches planifiées

**API:**
```bash
GET http://localhost:5000/api/scheduler/jobs
Authorization: Bearer {token_admin}
```

**Réponse attendue:**
```json
{
  "jobs": [
    {
      "id": "mise_a_jour_statuts",
      "name": "Mise à jour automatique des statuts",
      "next_run": "2026-01-28T08:00:00",
      "trigger": "cron[hour='8', minute='0']"
    },
    ...
  ],
  "total": 5
}
```

### Test 2: Exécuter mise à jour maintenant

**API:**
```bash
POST http://localhost:5000/api/scheduler/update-statuts
Authorization: Bearer {token_admin}
```

**Réponse attendue:**
```json
{
  "message": "Mise à jour des statuts effectuée",
  "compteurs": {
    "placements_demarres": 0,
    "placements_termines": 0,
    "remplacements_demarres": 0,
    "remplacements_termines": 0,
    "collaborateurs_retour": 0
  }
}
```

### Test 3: Créer un placement pour demain

1. Créer un placement avec date_debut = demain
2. Attendre 8h00 le lendemain (ou exécuter manuellement)
3. Vérifier que le statut passe à "En cours"
4. Vérifier la traçabilité

---

## 📁 Fichiers Créés/Modifiés

### Backend:

1. **`backend/requirements.txt`**
   - Ajout APScheduler==3.10.4

2. **`backend/app/services/scheduler_service.py`** (NOUVEAU)
   - Service complet de gestion des tâches planifiées
   - 5 tâches automatiques
   - Logging détaillé

3. **`backend/app/routes/scheduler.py`** (NOUVEAU)
   - Routes API pour gérer les tâches
   - Exécution manuelle pour tests

4. **`backend/app/routes/__init__.py`**
   - Enregistrement du blueprint scheduler

5. **`backend/main.py`**
   - Initialisation du scheduler au démarrage

---

## ⚙️ CONFIGURATION

### Variables d'environnement (optionnel):

```env
# Fuseau horaire (par défaut: système)
TZ=Europe/Paris

# Activer/désactiver le scheduler
SCHEDULER_ENABLED=true
```

---

## 🎯 PROCHAINES AMÉLIORATIONS

### Phase 3: Détection de Conflits (À venir)

1. **Avant création de placement:**
   - Vérifier si collaborateur déjà placé
   - Vérifier si collaborateur en absence
   - Bloquer si conflit détecté

2. **Avant création de remplacement:**
   - Vérifier disponibilité du remplaçant
   - Alerter si déjà en mission

3. **Validation intelligente:**
   - Suggestions automatiques de remplaçants
   - Détection de chevauchements de dates

---

## ✅ RÉSULTAT

Le système effectue maintenant **automatiquement** les tâches administratives répétitives:

✅ Mise à jour des statuts selon les dates
✅ Rappels pour actions importantes
✅ Génération de rapports périodiques
✅ Traçabilité complète de toutes les actions
✅ Logs détaillés pour monitoring

**Gain de temps estimé:** 2-3 heures par semaine pour les administrateurs

**Phase 2 terminée avec succès!** 🎉

---

## 📊 STATISTIQUES

**Tâches automatiques:** 5
**Routes API ajoutées:** 6
**Fréquence d'exécution:** 
- Quotidien: 3 tâches
- Hebdomadaire: 1 tâche
- Mensuel: 1 tâche

**Prochaine session:** Phase 3 - Détection de Conflits
