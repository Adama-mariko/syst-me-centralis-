from app.extensions import db
from datetime import datetime
from enum import Enum

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
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'remplace_id': self.remplace_id,
            'remplacant_id': self.remplacant_id,
            'type_remplacement': self.type_remplacement.value,
            'motif': self.motif,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'statut': self.statut.value,
            'commentaires': self.commentaires,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }