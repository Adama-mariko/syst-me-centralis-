# Système Centralisé de Gestion du Personnel

## 📋 Description

Système informatique centralisé pour la gestion et le placement de personnel au sein d'entreprises partenaires. L'application permet la gestion complète des collaborateurs, l'organisation des placements, la gestion des remplacements et la traçabilité des mouvements.

## 🏗️ Architecture

### Backend (Flask + MySQL)
- **Framework** : Flask (Python)
- **Base de données** : MySQL
- **Authentification** : JWT (JSON Web Tokens)
- **API** : RESTful API avec CORS

### Frontend (Angular + Material Design)
- **Framework** : Angular 18
- **UI Library** : Angular Material
- **Authentification** : JWT avec intercepteurs
- **Responsive** : Design adaptatif mobile/desktop

## 🚀 Fonctionnalités

### 👨‍💼 Portail Administrateur
- ✅ Gestion complète des utilisateurs
- ✅ Gestion des entreprises partenaires
- ✅ Gestion des collaborateurs
- ✅ Upload d'avatars utilisateur
- ✅ Dashboard avec statistiques
- ✅ Traçabilité des actions
- 🚧 Gestion des placements
- 🚧 Gestion des remplacements
- 🚧 Rapports et exports

### 🏢 Portail RH Entreprise
- ✅ Gestion locale du personnel
- ✅ Validation des collaborateurs
- ✅ Dashboard personnalisé
- 🚧 Gestion des validations
- 🚧 Suivi des placements

### 🔐 Sécurité
- ✅ Authentification JWT
- ✅ Contrôle d'accès basé sur les rôles
- ✅ Validation côté client et serveur
- ✅ Hashage sécurisé des mots de passe
- ✅ Protection CORS

## 📊 Base de Données

### Tables Principales
1. **users** - Utilisateurs du système (Admin/RH)
2. **entreprises** - Entreprises partenaires
3. **collaborateurs** - Personnel géré
4. **placements** - Affectations de personnel
5. **remplacements** - Gestion des remplacements
6. **mouvements** - Traçabilité des actions

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Node.js 18+
- MySQL 8.0+
- Git

### Backend (Flask)

```bash
# Cloner le projet
git clone https://github.com/Adama-mariko/syst-me-centralis-.git
cd syst-me-centralis-

# Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
cd backend
pip install -r requirements.txt

# Configuration de la base de données
# 1. Créer la base de données MySQL 'personnel_management'
# 2. Configurer le fichier .env avec vos paramètres

# Exécuter les migrations
python create_database.py

# Lancer le serveur
python run.py
```

### Frontend (Angular)

```bash
# Installer les dépendances
cd frontend/personnel-app
npm install

# Lancer le serveur de développement
ng serve --port 4201
```

## 🌐 Accès

- **Frontend** : http://localhost:4201
- **Backend API** : http://localhost:5000
- **Connexion par défaut** : admin@personnel.com / admin123

## 📁 Structure du Projet

```
personnel-management-system/
├── backend/                    # API Flask
│   ├── app/
│   │   ├── models/            # Modèles de données
│   │   ├── routes/            # Routes API
│   │   ├── services/          # Services métier
│   │   └── utils/             # Utilitaires
│   ├── config/                # Configuration
│   ├── migrations/            # Scripts de migration
│   ├── uploads/               # Fichiers uploadés
│   └── requirements.txt       # Dépendances Python
├── frontend/personnel-app/     # Application Angular
│   ├── src/app/
│   │   ├── admin/             # Modules admin
│   │   ├── auth/              # Authentification
│   │   ├── core/              # Services et modèles
│   │   └── shared/            # Composants partagés
│   └── package.json           # Dépendances Node.js
└── README.md                  # Documentation
```

## 🔧 Configuration

### Variables d'Environnement (.env)

```env
# Flask
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Base de données
DB_HOST=localhost
DB_PORT=3306
DB_NAME=personnel_management
DB_USER=root
DB_PASSWORD=your-password
```

## 🎨 Captures d'Écran

### Dashboard Administrateur
- Interface moderne avec Material Design
- Statistiques en temps réel
- Navigation intuitive

### Gestion des Utilisateurs
- CRUD complet avec validation
- Upload d'avatars
- Gestion des rôles

### Gestion des Collaborateurs
- Interface responsive
- Filtres avancés
- Validation RH

## 🚧 Roadmap

### Version 1.1 (En cours)
- [ ] Gestion complète des placements
- [ ] Interface de remplacements
- [ ] Traçabilité avancée
- [ ] Notifications temps réel

### Version 1.2 (Planifiée)
- [ ] Rapports et exports PDF/Excel
- [ ] API mobile
- [ ] Intégration email
- [ ] Sauvegarde automatique

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Adama Mariko**
- GitHub: [@Adama-mariko](https://github.com/Adama-mariko)

## 🙏 Remerciements

- Angular Team pour le framework
- Flask Team pour le micro-framework
- Material Design pour l'UI/UX
- Communauté open source

---

**Status du Projet** : 🟢 En développement actif

**Dernière mise à jour** : Janvier 2026