#!/usr/bin/env python3
"""
Script de lancement du serveur Flask
"""
from main import create_app
from flask_migrate import upgrade
import os

def deploy():
    """Déploiement de l'application"""
    app = create_app()
    
    with app.app_context():
        # Créer les tables de base de données
        from app.extensions import db
        db.create_all()
        
        # Appliquer les migrations
        try:
            upgrade()
        except Exception as e:
            print(f"Erreur lors des migrations: {e}")

if __name__ == '__main__':
    # Déploiement initial si nécessaire
    if os.environ.get('FLASK_ENV') == 'development':
        deploy()
    
    # Lancement de l'application
    app = create_app()
    app.run(
        debug=os.environ.get('FLASK_ENV') == 'development',
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )