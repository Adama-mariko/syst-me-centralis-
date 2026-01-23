#!/usr/bin/env python3
"""
Script pour ajouter le champ photo_url à la table collaborateurs
"""

from main import create_app
from app.extensions import db

def add_photo_url_column():
    """Ajouter la colonne photo_url à la table collaborateurs"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'collaborateurs' 
                    AND column_name = 'photo_url'
                    AND table_schema = DATABASE()
                """))
                
                if result.fetchone()[0] == 0:
                    print("🔄 Ajout de la colonne photo_url...")
                    conn.execute(db.text("""
                        ALTER TABLE collaborateurs 
                        ADD COLUMN photo_url VARCHAR(255) NULL
                    """))
                    conn.commit()
                    print("✅ Colonne photo_url ajoutée avec succès!")
                else:
                    print("ℹ️ La colonne photo_url existe déjà")
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    print("🚀 Ajout du champ photo_url aux collaborateurs")
    print("=" * 50)
    add_photo_url_column()
    print("🎉 Migration terminée!")