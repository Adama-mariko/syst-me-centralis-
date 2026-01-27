import pymysql
from config.config import Config

# Connexion à MySQL sans spécifier de base de données
connection = pymysql.connect(
    host=Config.DB_HOST,
    port=int(Config.DB_PORT),
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)

try:
    with connection.cursor() as cursor:
        # Supprimer la base de données si elle existe
        print(f"🔄 Suppression de la base de données '{Config.DB_NAME}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {Config.DB_NAME}")
        
        # Créer la base de données
        print(f"🔄 Création de la base de données '{Config.DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"✓ Base de données '{Config.DB_NAME}' créée avec succès!")
            
    connection.commit()
finally:
    connection.close()

print(f"\n✓ Base de données réinitialisée!")
print(f"🚀 Lancez maintenant: python run.py")
