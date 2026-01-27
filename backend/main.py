from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.extensions import db, migrate, bcrypt, ma
from config.config import Config
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    # JWT
    jwt = JWTManager(app)
    
    # CORS
    CORS(app)
    
    # Route pour servir les fichiers uploadés
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory('uploads', filename)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import (
        User, Entreprise, Collaborateur, Placement, Remplacement, Mouvement,
        Absence, Notification, Rapport, SecurityLog, Competence, CollaborateurCompetence
    )
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Initialiser le scheduler pour les tâches automatiques
    from app.services.scheduler_service import SchedulerService
    SchedulerService.init_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)