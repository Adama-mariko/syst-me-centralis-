# Guide de Configuration Gmail pour l'Envoi d'Emails

## Problème Actuel
L'erreur `Username and Password not accepted` indique que Gmail refuse les identifiants.

## Solution: Utiliser un Mot de Passe d'Application Gmail

### Étape 1: Activer la Validation en 2 Étapes
1. Allez sur https://myaccount.google.com/security
2. Cliquez sur "Validation en 2 étapes"
3. Suivez les instructions pour l'activer (si ce n'est pas déjà fait)

### Étape 2: Générer un Mot de Passe d'Application
1. Allez sur https://myaccount.google.com/apppasswords
2. Connectez-vous si nécessaire
3. Dans "Sélectionner l'application", choisissez "Autre (nom personnalisé)"
4. Entrez "Système Gestion Personnel" comme nom
5. Cliquez sur "Générer"
6. **Copiez le mot de passe de 16 caractères** (format: xxxx xxxx xxxx xxxx)

### Étape 3: Mettre à Jour le Fichier .env
Ouvrez `backend/.env` et remplacez:

```env
SMTP_PASSWORD=lulafswexoxflts
```

Par:

```env
SMTP_PASSWORD=votre_mot_de_passe_application_16_caracteres
```

**Important:** Utilisez le mot de passe SANS espaces (exemple: `abcdabcdabcdabcd`)

### Étape 4: Redémarrer le Backend
Après avoir mis à jour le `.env`:
1. Arrêtez le backend (Ctrl+C)
2. Redémarrez-le: `python main.py`
3. Testez à nouveau: `python test_email.py dmsmariko@gmail.com`

## Alternative: Utiliser un Autre Service SMTP

Si vous ne pouvez pas utiliser Gmail, vous pouvez utiliser:

### Option 1: Mailtrap (Pour Tests)
```env
SMTP_SERVER=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=votre_username_mailtrap
SMTP_PASSWORD=votre_password_mailtrap
SMTP_FROM_EMAIL=noreply@personnel.com
```

### Option 2: SendGrid
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=votre_api_key_sendgrid
SMTP_FROM_EMAIL=dmsmariko@gmail.com
```

### Option 3: Mailgun
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=votre_username_mailgun
SMTP_PASSWORD=votre_password_mailgun
SMTP_FROM_EMAIL=dmsmariko@gmail.com
```

## Vérification
Une fois configuré correctement, vous devriez voir:
```
✅ Email envoyé avec succès!
   ID de notification: X
   Statut: envoye
```

## Notes Importantes
- Gmail limite l'envoi à 500 emails/jour pour les comptes gratuits
- Pour la production, il est recommandé d'utiliser un service SMTP professionnel
- Le mot de passe d'application Gmail est différent de votre mot de passe Gmail normal
- Ne partagez JAMAIS votre mot de passe d'application publiquement
