from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='client', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Integer, nullable=False)
    categorie = db.Column(db.String(50), nullable=False, default='Plat')
    image = db.Column(db.String(255), nullable=False, default='uploads/plats/default_food.jpg')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='En attente')
    type_commande = db.Column(db.String(50), default='Livraison')  # 'Sur place' ou 'Livraison'
    adresse_livraison = db.Column(db.String(255), nullable=True, default='Sur place')
    telephone = db.Column(db.String(50), nullable=True, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- LIGNE AJOUTÉE POUR GÉRER L'ARCHIVAGE (SOFT DELETE) ---
    is_archived = db.Column(db.Boolean, default=False)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

    @property
    def code_recu(self):
        annee = self.created_at.strftime('%Y') if self.created_at else '2026'
        return f"WN-{annee}-{self.id:04d}"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')