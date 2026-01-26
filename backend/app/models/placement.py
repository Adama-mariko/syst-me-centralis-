from app.extensions import db
from datetime import datetime
from enum import Enum
from sqlalchemy.types import DECIMAL

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
    document_url = db.Column(db.String(255))  # URL du document (contrat, lettre de mission, etc.)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    validated_by_rh_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validation_rh_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])
    validated_by_rh = db.relationship('User', foreign_keys=[validated_by_rh_user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'collaborateur_id': self.collaborateur_id,
            'entreprise_id': self.entreprise_id,
            'poste_demande': self.poste_demande,
            'description': self.description,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'salaire_propose': float(self.salaire_propose) if self.salaire_propose else None,
            'statut': self.statut.value,
            'commentaires': self.commentaires,
            'document_url': self.document_url,
            'validation_rh_date': self.validation_rh_date.isoformat() if self.validation_rh_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }