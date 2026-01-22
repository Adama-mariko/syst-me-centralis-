from datetime import datetime
from enum import Enum
from app.extensions import db

class StatutSecurite(Enum):
    SUCCES = "succes"
    ECHEC = "echec"
    TENTATIVE_SUSPECTE = "tentative_suspecte"

class SecurityLog(db.Model):
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    resource_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    statut = db.Column(db.Enum(StatutSecurite), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='security_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {
                'id': self.user.id,
                'nom': self.user.nom,
                'prenom': self.user.prenom,
                'email': self.user.email
            } if self.user else None,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'statut': self.statut.value,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SecurityLog {self.id}: {self.action} - {self.statut.value}>'