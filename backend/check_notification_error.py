"""
Script pour vérifier l'erreur de la dernière notification
"""
from main import create_app
from app.models.notification import Notification

app = create_app()

with app.app_context():
    # Récupérer la dernière notification
    notification = Notification.query.order_by(Notification.id.desc()).first()
    
    if notification:
        print(f"📧 Dernière notification (ID: {notification.id})")
        print(f"   Destinataire: {notification.destinataire_email}")
        print(f"   Sujet: {notification.sujet}")
        print(f"   Statut: {notification.statut.value}")
        print(f"   Tentatives: {notification.tentatives}")
        
        if notification.erreur_message:
            print(f"\n❌ Erreur:")
            print(f"   {notification.erreur_message}")
        else:
            print(f"\n✅ Aucune erreur enregistrée")
    else:
        print("Aucune notification trouvée")
