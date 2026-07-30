from flask import Blueprint, render_template
from models import Product

# Création du Blueprint pour gérer toutes les routes liées à l'accueil
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Route principale : Affiche la magnifique page d'accueil Wa Ngoie."""
    # On récupère les 3 derniers produits ajoutés pour les mettre en avant
    produits_vedettes = Product.query.order_by(Product.id.desc()).limit(3).all()
    return render_template('home.html', produits=produits_vedettes)