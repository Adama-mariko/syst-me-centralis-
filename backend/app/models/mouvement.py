from app.extensions import db
from datetime import datetime
from enum import Enum

class TypeMouvement(Enum):
    # Placements
    PLACEMENT_CREE = "placement_cree"
    PLACEMENT_MODIFIE = "placement_modifie"
    PLACEMENT_VALIDE = "placement_valide"
    PLACEMENT_SUPPRIME = "placement_supprime"
    
    # Remplacements
    REMPLACEMENT_CREE = "remplacement_cree"
    REMPLACEMENT_MODIFIE = "remplacement_modifie"
    REMPLACEMENT_SUPPRIME = "remplacement_supprime"
    
    # Absences
    ABSENCE_DEMANDE = "absence_demande"
    ABSENCE_APPROUVE = "absence_approuve"
    ABSENCE_REFUSE = "absence_refuse"
    
    # Collaborateurs
    COLLABORATEUR_CREE = "collaborateur_cree"
    COLLABORATEUR_MODIFIE = "collaborateur_modifie"
    COLLABORATEUR_STATUT_CHANGE = "collaborateur_statut_change"
    
    # Entreprises
    ENTREPRISE_CREE = "entreprise_cree"
    ENTREPRISE_MODIFIE = "entreprise_modifie"
    
    # Utilisateurs
    UTILISATEUR_CREE = "utilisateur_cree"
    UTILISATEUR_MODIFIE = "utilisateur_modifie"
    UTILISATEUR_ROLE_CHANGE = "utilisateur_role_change"
    
    # Compétences
    COMPETENCE_AJOUT = "competence_ajout"
    COMPETENCE_MODIFICATION = "competence_modification"

class Mouvement(db.Model):
    __tablename__ = 'mouvements'
    
    id = db.Column(db.Integer, primary_key=True)
    type_mouvement = db.Column(db.Enum(TypeMouvement), nullable=False)
    description = db.Column(db.Text, nullable=False)
    collaborateur_id = db.Column(db.Integer, db.ForeignKey('collaborateurs.id'))
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'))
    placement_id = db.Column(db.Integer, db.ForeignKey('placements.id'))
    remplacement_id = db.Column(db.Integer, db.ForeignKey('remplacements.id'))
    absence_id = db.Column(db.Integer, db.ForeignKey('absences.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donnees_avant = db.Column(db.Text)  # JSON string
    donnees_apres = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    collaborateur = db.relationship('Collaborateur', backref='mouvements')
    entreprise = db.relationship('Entreprise', backref='mouvements')
    placement = db.relationship('Placement', backref='mouvements')
    remplacement = db.relationship('Remplacement', backref='mouvements')
    absence = db.relationship('Absence', backref='mouvements')
    user = db.relationship('User', backref='mouvements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_mouvement': self.type_mouvement.value,
            'description': self.description,
            'collaborateur_id': self.collaborateur_id,
            'entreprise_id': self.entreprise_id,
            'placement_id': self.placement_id,
            'remplacement_id': self.remplacement_id,
            'absence_id': self.absence_id,
            'user_id': self.user_id,
            'donnees_avant': self.donnees_avant,
            'donnees_apres': self.donnees_apres,
            'created_at': self.created_at.isoformat()
        }