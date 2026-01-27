from main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.entreprise import Entreprise

app = create_app()

with app.app_context():
    print("🔄 Création des tables...")
    
    # Créer toutes les tables
    db.create_all()
    
    print("✓ Tables créées avec succès!")
    
    # Vérifier si l'admin existe
    admin = User.query.filter_by(email='admin@personnel.com').first()
    if not admin:
        print("\n🔄 Création de l'utilisateur admin...")
        admin = User(
            email='admin@personnel.com',
            nom='Admin',
            prenom='Système',
            role=UserRole.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin créé: admin@personnel.com / admin123")
    else:
        print("\n✓ Admin existe déjà")
    
    # Vérifier si une entreprise exemple existe
    entreprise = Entreprise.query.first()
    if not entreprise:
        print("\n🔄 Création d'une entreprise exemple...")
        entreprise = Entreprise(
            nom='Entreprise Exemple SARL',
            siret='12345678901234',
            adresse='123 Rue de la Paix',
            ville='Paris',
            code_postal='75001',
            telephone='0123456789',
            email='contact@exemple.com'
        )
        db.session.add(entreprise)
        db.session.commit()
        print("✓ Entreprise exemple créée")
    else:
        print("\n✓ Entreprise existe déjà")
    
    print("\n✅ Base de données initialisée avec succès!")
    print("🚀 Vous pouvez maintenant lancer le serveur avec: python run.py")
