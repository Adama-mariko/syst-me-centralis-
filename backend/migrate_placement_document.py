#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    
    with app.app_context():
        try:
            print("Verification de la colonne document_url...")
            
            # Vérifier si la colonne existe
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'placements' 
                AND COLUMN_NAME = 'document_url'
            """))
            
            exists = result.scalar()
            
            if exists:
                print("OK - La colonne document_url existe deja")
                return True
            
            print("Ajout de la colonne document_url...")
            
            # Ajouter la colonne
            db.session.execute(text("""
                ALTER TABLE placements 
                ADD COLUMN document_url VARCHAR(255) DEFAULT NULL
            """))
            
            db.session.commit()
            print("OK - Colonne document_url ajoutee avec succes!")
            
            return True
            
        except Exception as e:
            print(f"ERREUR: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout document_url aux placements")
    print("=" * 60)
    
    if migrate():
        print("\nMigration terminee avec succes!")
    else:
        print("\nLa migration a echoue")
