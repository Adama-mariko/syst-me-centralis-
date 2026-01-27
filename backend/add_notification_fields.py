"""
Script pour ajouter les champs lu et date_lecture à la table notifications
"""
from main import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        print("🔄 Ajout des champs lu et date_lecture à la table notifications...")
        
        # Vérifier si les colonnes existent déjà
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('notifications')]
        
        if 'lu' not in columns:
            db.session.execute(text('ALTER TABLE notifications ADD COLUMN lu BOOLEAN DEFAULT FALSE'))
            print("✓ Colonne 'lu' ajoutée")
        else:
            print("✓ Colonne 'lu' existe déjà")
        
        if 'date_lecture' not in columns:
            db.session.execute(text('ALTER TABLE notifications ADD COLUMN date_lecture DATETIME'))
            print("✓ Colonne 'date_lecture' ajoutée")
        else:
            print("✓ Colonne 'date_lecture' existe déjà")
        
        db.session.commit()
        print("\n✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        db.session.rollback()
