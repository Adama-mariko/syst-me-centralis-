from datetime import datetime, date
from enum import Enum
from app.extensions import db

class TypeRapport(Enum):
    MENSUEL_PLACEMENTS = "mensuel_placements"
    MENSUEL_ABSENCES = "mensuel_absences"
    MENSUEL_REMPLACEMENTS = "mensuel_remplacements"
    ANNUEL_GLOBAL = "annuel_global"
    PERSONNALISE = "personnalise"

class StatutRapport(Enum):
    EN_COURS = "en_cours"
    GENERE = "genere"
    ERREUR = "erreur"

class Rapport(db.Model):
    __tablename__ = 'rapports'
    
    id = db.Column(db.Integer, primary_key=True)
    type_rapport = db.Column(db.Enum(TypeRapport), nullable=False)
    titre = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    periode_debut = db.Column(db.Date, nullable=False)
    periode_fin = db.Column(db.Date, nullable=False)
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprises.id'))
    ville = db.Column(db.String(100))
    statut = db.Column(db.Enum(StatutRapport), default=StatutRapport.EN_COURS)
    fichier_path = db.Column(db.String(500))
    donnees_json = db.Column(db.Text)
    genere_par_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    entreprise = db.relationship('Entreprise', backref='rapports')
    generateur = db.relationship('User', backref='rapports_generes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_rapport': self.type_rapport.value,
            'titre': self.titre,
            'description': self.description,
            'periode_debut': self.periode_debut.isoformat() if self.periode_debut else None,
            'periode_fin': self.periode_fin.isoformat() if self.periode_fin else None,
            'entreprise_id': self.entreprise_id,
            'entreprise': {
                'id': self.entreprise.id,
                'nom': self.entreprise.nom
            } if self.entreprise else None,
            'ville': self.ville,
            'statut': self.statut.value,
            'fichier_path': self.fichier_path,
            'donnees_json': self.donnees_json,
            'genere_par_user_id': self.genere_par_user_id,
            'generateur': {
                'id': self.generateur.id,
                'nom': self.generateur.nom,
                'prenom': self.generateur.prenom
            } if self.generateur else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Rapport {self.id}: {self.titre} - {self.statut.value}>'