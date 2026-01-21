from app.extensions import db
from datetime import datetime

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
    
    # Relations
    collaborateurs = db.relationship('Collaborateur', backref='entreprise_actuelle', lazy=True)
    placements = db.relationship('Placement', backref='entreprise', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'siret': self.siret,
            'adresse': self.adresse,
            'ville': self.ville,
            'code_postal': self.code_postal,
            'telephone': self.telephone,
            'email': self.email,
            'contact_rh_nom': self.contact_rh_nom,
            'contact_rh_email': self.contact_rh_email,
            'contact_rh_telephone': self.contact_rh_telephone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }