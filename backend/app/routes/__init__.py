from .auth import auth_bp
from .admin import admin_bp
from .rh import rh_bp
from .collaborateurs import collaborateurs_bp
from .entreprises import entreprises_bp
from .placements import placements_bp
from .remplacements import remplacements_bp
from .mouvements import mouvements_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(rh_bp, url_prefix='/api/rh')
    app.register_blueprint(collaborateurs_bp, url_prefix='/api/collaborateurs')
    app.register_blueprint(entreprises_bp, url_prefix='/api/entreprises')
    app.register_blueprint(placements_bp, url_prefix='/api/placements')
    app.register_blueprint(remplacements_bp, url_prefix='/api/remplacements')
    app.register_blueprint(mouvements_bp, url_prefix='/api/mouvements')