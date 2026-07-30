import os
from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à l'espace Wa Ngoie."
    login_message_category = "warning"

    from models import User, Product, Order, OrderItem
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    
    # Importation des routes
    from routes.home import home_bp
    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.commande import commande_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(menu_bp)
    app.register_blueprint(commande_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        
        # 1. Initialisation automatique de l'administrateur
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            hashed_admin_pw = bcrypt.generate_password_hash("wangoie2026").decode('utf-8')
            admin = User(
                nom="Administrateur Wa Ngoie",
                email="admin@wangoie.com",
                password=hashed_admin_pw,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("[INFO] Compte Administrateur crée avec succès (Identifiant: wangoie / Passe: wangoie2026).")

        # 2. Injection des plats
        if Product.query.count() == 0:
            plats_initiaux = [
                Product(nom="Shawarma", description="Délicieux shawarma bien garni.", prix=14000, image="uploads/plats/chawarma.jpg"),
                Product(nom="Hamburger", description="Burger juteux avec steak et cheddar fondant.", prix=14000, image="uploads/plats/hamburger.jpg"),
                Product(nom="Tacos", description="Tacos croustillant garni de viande.", prix=14000, image="uploads/plats/tacos.jpg"),
                Product(nom="Saucisse (2 pièces)", description="Saucisses grillées savoureuses.", prix=14000, image="uploads/plats/saucisse.jpg"),
                Product(nom="Cuisse de poulet", description="Cuisses de poulet dorées.", prix=14000, image="uploads/plats/cuisse_de_poulet.png"),
                Product(nom="Poulet Mayo", description="Le fameux poulet mayo traditionnel.", prix=28000, image="uploads/plats/poulet_mayo.jpg"),
                Product(nom="Samoussa (3 pièces)", description="Samoussas croustillants.", prix=14000, image="uploads/plats/samoussa.jpg"),
                Product(nom="Boulettes (3 pièces)", description="Boulettes de viande.", prix=14000, image="uploads/plats/boulette.jpg"),
                Product(nom="Chikwangue", description="Chikwangue fraîche et traditionnelle.", prix=3500, image="uploads/plats/chikwangue.jpg"),
                Product(nom="Frites", description="Portion de frites de pommes de terre.", prix=7000, image="uploads/plats/frites.jpg"),
                Product(nom="Eau", description="Bouteille d'eau minérale fraîche 50cl.", prix=2500, image="uploads/plats/eau.jpg"),
                Product(nom="Canette sucrée", description="Boisson gazeuse en canette.", prix=5500, image="uploads/plats/sucre.jpg"),
                Product(nom="Savana / Bavaria", description="Boisson rafraîchissante.", prix=8000, image="uploads/plats/savanna.jpg"),
                Product(nom="Bière", description="Bière locale bien fraîche.", prix=8000, image="uploads/plats/biere.jpg"),
                Product(nom="Brochette", description="Brochettes tendres et savoureuses.", prix=10000, image="uploads/plats/brochette.jpg"),
                Product(nom="Pizza", description="Délicieuse pizza maison.", prix=20000, image="uploads/plats/pizza.jpg"),
                Product(nom="Gaufre", description="Gaufre sucrée et croustillante.", prix=5000, image="uploads/plats/gaufre.jpg")
            ]
            db.session.bulk_save_objects(plats_initiaux)
            db.session.commit()
            print("[INFO] Les articles Wa Ngoie ont été injectés.")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)