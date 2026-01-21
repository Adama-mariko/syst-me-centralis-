# Système de Gestion de Personnel - Backend

## Description
Solution informatique centralisée pour la gestion et le placement de personnel au sein d'entreprises partenaires.

## Fonctionnalités
- Gestion complète des collaborateurs
- Organisation des placements
- Gestion des remplacements en cas d'absence
- Validation des personnels par les RH des entreprises partenaires
- Traçabilité des mouvements
- Automatisation des tâches administratives

## Architecture
- **Backend**: Python Flask + MySQL
- **Portail Admin**: Gestion complète du système
- **Portail RH Entreprise**: Gestion locale du personnel placé

## Installation
```bash
pip install -r requirements.txt
python app.py
```

## Structure du projet
```
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── config/
├── migrations/
└── tests/
```