from datetime import datetime
from enum import Enum
from app.extensions import db

class TypeNotification(Enum):
    # Placements
    PLACEMENT_CREE = "placement_cree"
    PLACEMENT_VALIDE = "placement_valide"
    PLACEMENT_REFUSE = "placement_refuse"
    PLACEMENT_MODIFIE = "placement_modifie"
    PLACEMENT_EXPIRE_BIENTOT = "placement_expire_bientot"
    PLACEMENT_EXPIRE = "placement_expire"
    
    # Absences
    ABSENCE_DEMANDEE = "absence_demandee"
    ABSENCE_APPROUVEE = "absence_approuvee"
    ABSENCE_REFUSEE = "absence_refusee"
    
    # Remplacements
    REMPLACEMENT_PROPOSE = "remplacement_propose"
    REMPLACEMENT_CREE = "remplacement_cree"
    REMPLACEMENT_MODIFIE = "remplacement_modifie"
    
    # Rappels
    RAPPEL_VALIDATION = "rappel_validation"
    RAPPEL_PLACEMENT = "rappel_placement"
    
    # Conflits
    CONFLIT_DETECTE = "conflit_detecte"
    
    # Système
    RAPPORT_GENERE = "rapport_genere"
    AUTRE = "autre"

class StatutNotification(Enum):
    EN_ATTENTE = "en_attente"
    ENVOYE = "envoye"
    ECHEC = "echec"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    type_notification = db.Column(db.Enum(TypeNotification), nullable=False)
    destinataire_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    destinataire_email = db.Column(db.String(120))
    sujet = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    statut = db.Column(db.Enum(StatutNotification), default=StatutNotification.EN_ATTENTE)
    lu = db.Column(db.Boolean, default=False)
    date_lecture = db.Column(db.DateTime)
    date_envoi = db.Column(db.DateTime)
    tentatives = db.Column(db.Integer, default=0)
    erreur_message = db.Column(db.Text)
    placement_id = db.Column(db.Integer, db.ForeignKey('placements.id'))
    absence_id = db.Column(db.Integer, db.ForeignKey('absences.id'))
    remplacement_id = db.Column(db.Integer, db.ForeignKey('remplacements.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    destinataire = db.relationship('User', backref='notifications_recues')
    placement = db.relationship('Placement', backref='notifications')
    absence = db.relationship('Absence', backref='notifications')
    remplacement = db.relationship('Remplacement', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_notification': self.type_notification.value,
            'destinataire_user_id': self.destinataire_user_id,
            'destinataire_email': self.destinataire_email,
            'destinataire': {
                'id': self.destinataire.id,
                'nom': self.destinataire.nom,
                'prenom': self.destinataire.prenom,
                'email': self.destinataire.email
            } if self.destinataire else None,
            'sujet': self.sujet,
            'message': self.message,
            'statut': self.statut.value,
            'lu': self.lu,
            'date_lecture': self.date_lecture.isoformat() if self.date_lecture else None,
            'date_envoi': self.date_envoi.isoformat() if self.date_envoi else None,
            'tentatives': self.tentatives,
            'erreur_message': self.erreur_message,
            'placement_id': self.placement_id,
            'absence_id': self.absence_id,
            'remplacement_id': self.remplacement_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type_notification.value} - {self.statut.value}>'