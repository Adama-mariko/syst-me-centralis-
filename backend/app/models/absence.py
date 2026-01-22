from datetime import datetime, date
from enum import Enum
from app.extensions import db

class TypeAbsence(Enum):
    CONGE_PAYE = "conge_paye"
    CONGE_SANS_SOLDE = "conge_sans_solde"
    MALADIE = "maladie"
    FORMATION = "formation"
    MATERNITE = "maternite"
    PATERNITE = "paternite"
    AUTRE = "autre"

class StatutAbsence(Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"
    ANNULE = "annule"

class Absence(db.Model):
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    type_absence = db.Column(db.Enum(TypeAbsence), nullable=False)
    motif = db.Column(db.Text)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    nombre_jours = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.Enum(StatutAbsence), default=StatutAbsence.EN_ATTENTE)
    commentaires = db.Column(db.Text)
    document_justificatif = db.Column(db.String(255))
    demande_par_collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'), nullable=False)
    approuve_par_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_approbation = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    collaborateur = db.relationship('Collaborateur', foreign_keys=[collaborateur_id], backref='absences')
    demandeur = db.relationship('Collaborateur', foreign_keys=[demande_par_collaborateur_id])
    approbateur = db.relationship('User', backref='absences_approuvees')
    
    def to_dict(self):
        return {
            'id': self.id,
            'collaborateur_id': self.collaborateur_id,
            'collaborateur': {
                'id': self.collaborateur.id,
                'nom': self.collaborateur.nom,
                'prenom': self.collaborateur.prenom,
                'email': self.collaborateur.email
            } if self.collaborateur else None,
            'type_absence': self.type_absence.value,
            'motif': self.motif,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'nombre_jours': self.nombre_jours,
            'statut': self.statut.value,
            'commentaires': self.commentaires,
            'document_justificatif': self.document_justificatif,
            'demande_par_collaborateur_id': self.demande_par_collaborateur_id,
            'demandeur': {
                'id': self.demandeur.id,
                'nom': self.demandeur.nom,
                'prenom': self.demandeur.prenom
            } if self.demandeur else None,
            'approuve_par_user_id': self.approuve_par_user_id,
            'approbateur': {
                'id': self.approbateur.id,
                'nom': self.approbateur.nom,
                'prenom': self.approbateur.prenom
            } if self.approbateur else None,
            'date_approbation': self.date_approbation.isoformat() if self.date_approbation else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Absence {self.id}: {self.collaborateur.nom if self.collaborateur else "N/A"} - {self.type_absence.value}>'