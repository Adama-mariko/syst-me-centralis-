from datetime import datetime, date
from enum import Enum
from app.extensions import db

class NiveauCompetence(Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"
    EXPERT = "expert"

class Competence(db.Model):
    __tablename__ = 'competences'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50))
    niveau_requis = db.Column(db.Enum(NiveauCompetence), default=NiveauCompetence.DEBUTANT)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'categorie': self.categorie,
            'niveau_requis': self.niveau_requis.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Competence {self.id}: {self.nom}>'

class CollaborateurCompetence(db.Model):
    __tablename__ = 'collaborateur_competences'
    
    id = db.Column(db.Integer, primary_key=True)
    collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'), nullable=False)
    niveau = db.Column(db.Enum(NiveauCompetence), nullable=False)
    certifie = db.Column(db.Boolean, default=False)
    date_acquisition = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    collaborateur = db.relationship('Collaborateur', backref='competences_rel')
    competence = db.relationship('Competence', backref='collaborateurs_rel')
    
    # Contrainte unique
    __table_args__ = (db.UniqueConstraint('collaborateur_id', 'competence_id', name='unique_collaborateur_competence'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'collaborateur_id': self.collaborateur_id,
            'competence_id': self.competence_id,
            'competence': self.competence.to_dict() if self.competence else None,
            'niveau': self.niveau.value,
            'certifie': self.certifie,
            'date_acquisition': self.date_acquisition.isoformat() if self.date_acquisition else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CollaborateurCompetence {self.id}: {self.collaborateur_id} - {self.competence_id}>'