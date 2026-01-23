from app.extensions import db
from datetime import datetime
from enum import Enum
from sqlalchemy.types import DECIMAL

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
    competences = db.Column(db.Text)  # JSON string
    salaire = db.Column(DECIMAL(10, 2))
    statut = db.Column(db.Enum(StatutCollaborateur), default=StatutCollaborateur.ACTIF)
    entreprise_actuelle_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'))
    photo_url = db.Column(db.String(255))  # URL de la photo de profil
    is_validated_by_rh = db.Column(db.Boolean, default=False)
    validated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validation_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    validated_by = db.relationship('User', foreign_keys=[validated_by_user_id])
    placements = db.relationship('Placement', backref='collaborateur', lazy=True)
    remplacements_effectues = db.relationship('Remplacement', 
                                            foreign_keys='Remplacement.remplacant_id',
                                            backref='remplacant', lazy=True)
    remplacements_remplaces = db.relationship('Remplacement',
                                            foreign_keys='Remplacement.remplace_id', 
                                            backref='remplace', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_employe': self.numero_employe,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'ville': self.ville,
            'code_postal': self.code_postal,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'date_embauche': self.date_embauche.isoformat(),
            'poste': self.poste,
            'competences': self.competences,
            'salaire': float(self.salaire) if self.salaire else None,
            'statut': self.statut.value,
            'entreprise_actuelle_id': self.entreprise_actuelle_id,
            'photo_url': self.photo_url,
            'is_validated_by_rh': self.is_validated_by_rh,
            'validation_date': self.validation_date.isoformat() if self.validation_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }