from app.extensions import db, bcrypt
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
    avatar_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    entreprise = db.relationship('Entreprise', backref='users')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nom': self.nom,
            'prenom': self.prenom,
            'role': self.role.value,
            'entreprise_id': self.entreprise_id,
            'avatar_url': self.get_avatar_url(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_avatar_url(self):
        """Retourne l'URL complète de l'avatar"""
        if self.avatar_url:
            if self.avatar_url.startswith('http'):
                return self.avatar_url
            else:
                return f"http://localhost:5000{self.avatar_url}"
        return None