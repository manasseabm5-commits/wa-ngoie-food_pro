import os

# Pointe vers le dossier racine du projet (wa_ngoie/)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Clé de sécurité pour crypter les sessions et protéger contre les attaques CSRF
    SECRET_KEY = 'cle_secrete_wa_ngoie_abm_2026'
    
    # Chemin absolu vers la base de données pour garantir sa persistance
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'wa_ngoie.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dossier où seront stockées les photos des plats
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')