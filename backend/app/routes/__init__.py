from .auth import auth_bp
from .admin import admin_bp
from .rh import rh_bp
from .collaborateurs import collaborateurs_bp
from .entreprises import entreprises_bp
from .placements import placements_bp
from .remplacements import remplacements_bp
from .mouvements import mouvements_bp
from .absences import absences_bp
from .notifications import notifications_bp
from .rapports import rapports_bp
from .competences import competences_bp
from .tracabilite import tracabilite_bp

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
    app.register_blueprint(absences_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api')
    app.register_blueprint(rapports_bp, url_prefix='/api')
    app.register_blueprint(competences_bp, url_prefix='/api')
    app.register_blueprint(tracabilite_bp, url_prefix='/api')