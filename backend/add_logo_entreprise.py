#!/usr/bin/env python3
"""
Script pour ajouter le champ logo_url à la table entreprises
"""

from main import create_app
from app.extensions import db

def add_logo_field():
    app = create_app()
    
    with app.app_context():
        try:
            # Ajouter la colonne logo_url à la table entreprises
            with db.engine.connect() as connection:
                connection.execute(db.text('ALTER TABLE entreprises ADD COLUMN logo_url VARCHAR(255)'))
                connection.commit()
            print("✅ Champ logo_url ajouté avec succès à la table entreprises!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du champ logo_url: {str(e)}")
            # Si la colonne existe déjà, ce n'est pas grave
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                print("ℹ️ Le champ logo_url existe déjà dans la table entreprises")

if __name__ == '__main__':
    add_logo_field()