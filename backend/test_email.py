"""
Script pour tester l'envoi d'emails
"""
from main import create_app
from app.services.notification_service import NotificationService
from app.models.notification import TypeNotification
import sys

app = create_app()

def test_email(email_destinataire):
    """Tester l'envoi d'un email"""
    with app.app_context():
        try:
            print(f"📧 Envoi d'un email de test à {email_destinataire}...")
            
            # Créer et envoyer la notification
            notification = NotificationService.creer_notification(
                TypeNotification.AUTRE,
                None,
                email_destinataire,
                "Test Email SMTP - Système de Gestion Personnel",
                "Bonjour,\n\n"
                "Si vous recevez cet email, cela signifie que la configuration SMTP fonctionne correctement!\n\n"
                "Le système de gestion de personnel peut maintenant envoyer des emails automatiques aux collaborateurs.\n\n"
                "Cordialement,\n"
                "L'équipe de développement"
            )
            
            print(f"✅ Email envoyé avec succès!")
            print(f"   ID de notification: {notification.id}")
            print(f"   Statut: {notification.statut.value}")
            print(f"\n📬 Vérifiez votre boîte de réception (et le dossier spam)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_email.py votre-email@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    test_email(email)
