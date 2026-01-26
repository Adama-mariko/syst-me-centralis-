#!/usr/bin/env python3
"""
Script pour créer un utilisateur admin par défaut
"""

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        try:
            # Créer les tables si elles n'existent pas
            db.create_all()
            
            # Vérifier si un admin existe déjà
            admin_exists = User.query.filter_by(role=UserRole.ADMIN).first()
            
            if admin_exists:
                print(f"✅ Un utilisateur admin existe déjà: {admin_exists.email}")
                return
            
            # Créer l'utilisateur admin
            admin_user = User(
                email='admin@personnel.com',
                nom='Admin',
                prenom='Super',
                role=UserRole.ADMIN,
                is_active=True
            )
            
            # Définir le mot de passe
            admin_user.set_password('admin123')
            
            # Ajouter à la base de données
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Utilisateur admin créé avec succès!")
            print("📧 Email: admin@personnel.com")
            print("🔑 Mot de passe: admin123")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'admin: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user()