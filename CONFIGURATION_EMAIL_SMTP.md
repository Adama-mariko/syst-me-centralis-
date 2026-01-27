# Configuration des Emails SMTP

## 📧 Pourquoi configurer les emails?

Les **collaborateurs n'ont pas accès à l'application**. Ils reçoivent toutes les informations par email:
- Création de leur profil
- Nouveaux placements
- Validations de placements
- Remplacements
- Absences approuvées/refusées

**Seuls les Admin et RH se connectent à l'application.**

---

## 🔧 Configuration SMTP

### Option 1: Gmail (Recommandé pour tests)

#### Étape 1: Activer l'authentification à 2 facteurs
1. Allez sur https://myaccount.google.com/security
2. Activez "Validation en deux étapes"

#### Étape 2: Créer un mot de passe d'application
1. Allez sur https://myaccount.google.com/apppasswords
2. Sélectionnez "Autre (nom personnalisé)"
3. Entrez "Système Personnel"
4. Cliquez sur "Générer"
5. **Copiez le mot de passe généré** (16 caractères)

#### Étape 3: Configurer le fichier .env

Créez/modifiez le fichier `backend/.env`:

```env
# Email Configuration - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=votre-email@gmail.com
SMTP_FROM_NAME=Système de Gestion Personnel
```

**Remplacez:**
- `votre-email@gmail.com` par votre email Gmail
- `xxxx xxxx xxxx xxxx` par le mot de passe d'application généré

---

### Option 2: Outlook/Hotmail

```env
# Email Configuration - Outlook
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@outlook.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_FROM_EMAIL=votre-email@outlook.com
SMTP_FROM_NAME=Système de Gestion Personnel
```

---

### Option 3: Yahoo Mail

```env
# Email Configuration - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@yahoo.com
SMTP_PASSWORD=votre-mot-de-passe-application
SMTP_FROM_EMAIL=votre-email@yahoo.com
SMTP_FROM_NAME=Système de Gestion Personnel
```

**Note:** Yahoo nécessite aussi un mot de passe d'application.

---

### Option 4: Serveur SMTP personnalisé

Si vous avez un serveur SMTP d'entreprise:

```env
# Email Configuration - Serveur personnalisé
SMTP_SERVER=smtp.votre-entreprise.com
SMTP_PORT=587
SMTP_USERNAME=noreply@votre-entreprise.com
SMTP_PASSWORD=mot-de-passe-smtp
SMTP_FROM_EMAIL=noreply@votre-entreprise.com
SMTP_FROM_NAME=Gestion Personnel - Votre Entreprise
```

---

## 🧪 Tester la Configuration

### Méthode 1: Via l'API

```bash
POST http://localhost:5000/api/notifications/test-email
Authorization: Bearer {token_admin}
Content-Type: application/json

{
  "email": "test@example.com",
  "sujet": "Test Email",
  "message": "Ceci est un email de test"
}
```

### Méthode 2: Via Python

Créez un fichier `backend/test_email.py`:

```python
from main import create_app
from app.services.notification_service import NotificationService
from app.models.notification import TypeNotification

app = create_app()

with app.app_context():
    # Envoyer un email de test
    notification = NotificationService.creer_notification(
        TypeNotification.AUTRE,
        None,
        "votre-email-test@gmail.com",  # Remplacez par votre email
        "Test Email SMTP",
        "Si vous recevez cet email, la configuration SMTP fonctionne correctement!"
    )
    
    print(f"✅ Email de test envoyé à votre-email-test@gmail.com")
    print(f"Vérifiez votre boîte de réception (et spam)")
```

Exécutez:
```bash
cd backend
python test_email.py
```

---

## 📋 Emails Automatiques Envoyés

### 1. Création de Collaborateur
**À:** Collaborateur
**Sujet:** "Bienvenue dans le système de gestion de personnel"
**Contenu:** Informations du profil créé

### 2. Nouveau Placement
**À:** Collaborateur + RH de l'entreprise
**Sujet:** "Nouveau placement proposé - [Entreprise]"
**Contenu:** Détails du placement

### 3. Placement Validé
**À:** Collaborateur
**Sujet:** "Placement validé - [Poste]"
**Contenu:** Confirmation et date de début

### 4. Nouveau Remplacement
**À:** Remplaçant + Remplacé
**Sujet:** "Nouveau remplacement - [Type]"
**Contenu:** Détails du remplacement

### 5. Demande d'Absence
**À:** RH
**Sujet:** "Demande d'absence - [Collaborateur]"
**Contenu:** Détails de la demande

### 6. Absence Approuvée
**À:** Collaborateur
**Sujet:** "Absence approuvée - [Type]"
**Contenu:** Confirmation

### 7. Absence Refusée
**À:** Collaborateur
**Sujet:** "Absence refusée - [Type]"
**Contenu:** Raison du refus

### 8. Validation Requise (Admin/RH)
**À:** Admin/RH (dans l'application)
**Sujet:** "Validation requise: [Action]"
**Contenu:** Demande de validation

---

## 🔒 Sécurité

### Bonnes Pratiques:

1. **Ne jamais commiter le fichier .env**
   - Déjà dans `.gitignore`
   - Contient des informations sensibles

2. **Utiliser des mots de passe d'application**
   - Plus sécurisé que le mot de passe principal
   - Peut être révoqué facilement

3. **Limiter les permissions**
   - Utilisez un compte dédié pour l'envoi
   - Pas de compte personnel

4. **Surveiller l'utilisation**
   - Gmail: 500 emails/jour max
   - Outlook: 300 emails/jour max
   - Yahoo: 500 emails/jour max

---

## ❌ Dépannage

### Erreur: "Authentication failed"
- Vérifiez le nom d'utilisateur et mot de passe
- Pour Gmail: Utilisez un mot de passe d'application
- Vérifiez que l'authentification 2FA est activée

### Erreur: "Connection refused"
- Vérifiez le serveur SMTP et le port
- Vérifiez votre connexion internet
- Vérifiez que le port 587 n'est pas bloqué

### Emails dans les spams
- Ajoutez un SPF record à votre domaine
- Utilisez un serveur SMTP professionnel
- Demandez aux destinataires d'ajouter l'expéditeur aux contacts

### Emails non reçus
- Vérifiez les logs du backend
- Vérifiez le dossier spam
- Vérifiez que l'email du destinataire est correct

---

## 📊 Mode Simulation (Développement)

Si vous ne configurez pas SMTP, le système fonctionne en **mode simulation**:
- Les emails ne sont pas envoyés
- Les messages sont affichés dans les logs du backend
- Utile pour le développement

Pour activer le mode simulation, laissez `SMTP_SERVER=localhost` dans `.env`.

---

## ✅ Checklist de Configuration

- [ ] Compte email créé/configuré
- [ ] Mot de passe d'application généré (Gmail/Yahoo)
- [ ] Fichier `.env` créé avec les bonnes valeurs
- [ ] Test d'envoi effectué
- [ ] Email de test reçu
- [ ] Backend redémarré

---

## 🎯 Prochaines Étapes

Une fois les emails configurés:
1. Créez un collaborateur → Il reçoit un email
2. Créez un placement → Le collaborateur et le RH reçoivent un email
3. Validez un placement → Le collaborateur reçoit un email
4. Testez tous les scénarios

**Les emails sont essentiels car les collaborateurs n'ont pas accès à l'application!**
