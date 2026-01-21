#!/usr/bin/env python3
"""
Script pour créer la base de données et les tables
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer Flask et les extensions
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy.types import DECIMAL

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'personnel_management')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Créer l'application Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialiser les extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
CORS(app)

# Importer les modèles
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    RH_ENTREPRISE = "rh_entreprise"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class Entreprise(db.Model):
    __tablename__ = 'entreprises'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    siret = db.Column(db.String(14), unique=True, nullable=False)
    adresse = db.Column(db.Text, nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    code_postal = db.Column(db.String(10), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contact_rh_nom = db.Column(db.String(100))
    contact_rh_email = db.Column(db.String(120))
    contact_rh_telephone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StatutCollaborateur(Enum):
    ACTIF = "actif"
    INACTIF = "inactif"
    EN_CONGE = "en_conge"
    ARRET_MALADIE = "arret_maladie"

class Collaborateur(db.Model):
    __tablename__ = 'collaborateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_employe = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    code_postal = db.Column(db.String(10))
    date_naissance = db.Column(db.Date)
    date_embauche = db.Column(db.Date, nullable=False)
    poste = db.Column(db.String(100), nullable=False)
    competences = db.Column(db.Text)
    salaire = db.Column(DECIMAL(10, 2))
    statut = db.Column(db.Enum(StatutCollaborateur), default=StatutCollaborateur.ACTIF)
    entreprise_actuelle_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'))
    is_validated_by_rh = db.Column(db.Boolean, default=False)
    validated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validation_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StatutPlacement(Enum):
    EN_ATTENTE = "en_attente"
    CONFIRME = "confirme"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"

class Placement(db.Model):
    __tablename__ = 'placements'
    
    id = db.Column(db.Integer, primary_key=True)
    collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'), nullable=False)
    poste_demande = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    salaire_propose = db.Column(DECIMAL(10, 2))
    statut = db.Column(db.Enum(StatutPlacement), default=StatutPlacement.EN_ATTENTE)
    commentaires = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    validated_by_rh_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validation_rh_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TypeRemplacement(Enum):
    CONGE = "conge"
    MALADIE = "maladie"
    FORMATION = "formation"
    AUTRE = "autre"

class StatutRemplacement(Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"

class Remplacement(db.Model):
    __tablename__ = 'remplacements'
    
    id = db.Column(db.Integer, primary_key=True)
    remplace_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    remplacant_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    type_remplacement = db.Column(db.Enum(TypeRemplacement), nullable=False)
    motif = db.Column(db.Text)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.Enum(StatutRemplacement), default=StatutRemplacement.PLANIFIE)
    commentaires = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TypeMouvement(Enum):
    PLACEMENT = "placement"
    REMPLACEMENT = "remplacement"
    VALIDATION = "validation"
    MODIFICATION = "modification"
    SUPPRESSION = "suppression"

class Mouvement(db.Model):
    __tablename__ = 'mouvements'
    
    id = db.Column(db.Integer, primary_key=True)
    type_mouvement = db.Column(db.Enum(TypeMouvement), nullable=False)
    description = db.Column(db.Text, nullable=False)
    collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'))
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'))
    placement_id = db.Column(db.Integer, db.ForeignKey('placements.id'))
    remplacement_id = db.Column(db.Integer, db.ForeignKey('remplacements.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donnees_avant = db.Column(db.Text)
    donnees_apres = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_database():
    """Créer la base de données et les tables"""
    try:
        with app.app_context():
            print("Création des tables...")
            
            # Supprimer toutes les tables existantes
            db.drop_all()
            
            # Créer toutes les tables
            db.create_all()
            
            print("✅ Tables créées avec succès!")
            
            # Créer un utilisateur admin par défaut
            admin_user = User.query.filter_by(email='admin@personnel.com').first()
            if not admin_user:
                admin_user = User(
                    email='admin@personnel.com',
                    nom='Admin',
                    prenom='Système',
                    role=UserRole.ADMIN
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                
                print("✅ Utilisateur admin créé (email: admin@personnel.com, mot de passe: admin123)")
            
            # Créer une entreprise exemple
            entreprise_exemple = Entreprise.query.filter_by(siret='12345678901234').first()
            if not entreprise_exemple:
                entreprise_exemple = Entreprise(
                    nom='Entreprise Exemple SARL',
                    siret='12345678901234',
                    adresse='123 Rue de la Paix',
                    ville='Paris',
                    code_postal='75001',
                    telephone='01.23.45.67.89',
                    email='contact@exemple.com',
                    contact_rh_nom='Marie Dupont',
                    contact_rh_email='rh@exemple.com'
                )
                db.session.add(entreprise_exemple)
                
                print("✅ Entreprise exemple créée")
            
            db.session.commit()
            
            # Afficher les tables créées
            print("\n📋 Tables créées dans la base de données:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            
            print(f"\n🎉 Base de données '{os.getenv('DB_NAME', 'personnel_management')}' créée avec succès!")
            print("Vous pouvez maintenant lancer l'application avec: python app.py")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    create_database()