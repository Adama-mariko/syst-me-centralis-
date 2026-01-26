import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def add_document_field():
    """Ajouter le champ document_url à la table placements"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'personnel_management'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔍 Vérification de la colonne document_url...")
            
            # Vérifier si la colonne existe déjà
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'placements' 
                AND COLUMN_NAME = 'document_url'
            """, (os.getenv('DB_NAME', 'personnel_management'),))
            
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✅ La colonne document_url existe déjà")
                return True
            
            print("📝 Ajout de la colonne document_url...")
            
            # Ajouter la colonne
            cursor.execute("""
                ALTER TABLE placements 
                ADD COLUMN document_url VARCHAR(255) DEFAULT NULL
                COMMENT 'URL du document associé au placement (contrat, lettre de mission, etc.)'
            """)
            
            connection.commit()
            print("✅ Colonne document_url ajoutée avec succès!")
            
            return True
            
    except Error as e:
        print(f"❌ Erreur: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Connexion fermée")

if __name__ == "__main__":
    print("🚀 Ajout du champ document_url aux placements")
    print("=" * 60)
    
    if add_document_field():
        print("\n✅ Migration terminée avec succès!")
    else:
        print("\n❌ La migration a échoué")
