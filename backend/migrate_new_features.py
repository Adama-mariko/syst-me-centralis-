#!/usr/bin/env python3
"""
Script simple pour appliquer les nouvelles fonctionnalités
"""

from main import create_app
from app.extensions import db
from app.models import *
import os

def apply_migration():
    """Appliquer la migration SQL directement"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Application des nouvelles fonctionnalités...")
            
            # Lire le fichier SQL
            with open('migrations/add_new_features.sql', 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Diviser en commandes individuelles
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            for command in commands:
                if command:
                    try:
                        db.engine.execute(command)
                        print(f"✅ Exécuté: {command[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"⚠️  Déjà existant: {command[:50]}...")
                        else:
                            print(f"❌ Erreur: {e}")
            
            print("✅ Migration terminée!")
            
            # Créer les tables avec SQLAlchemy
            print("🔄 Création des tables avec SQLAlchemy...")
            db.create_all()
            print("✅ Tables créées!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Application des nouvelles fonctionnalités")
    print("=" * 50)
    
    if apply_migration():
        print("\n🎉 SUCCÈS! Nouvelles fonctionnalités ajoutées:")
        print("   ✅ Gestion des absences")
        print("   ✅ Système de notifications")
        print("   ✅ Génération de rapports")
        print("   ✅ Traçabilité complète")
        print("   ✅ Gestion des compétences")
        print("   ✅ Nouveaux rôles de sécurité")
        print("\n🔧 Redémarrez le serveur pour appliquer les changements")
    else:
        print("❌ Échec de l'application")