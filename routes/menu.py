from flask import Blueprint, render_template
from models import Product

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu')
def menu():
    """Affiche le menu complet de Wa Ngoie."""
    # Correction : on récupère tous les produits sans le filtre is_available
    produits = Product.query.all()
    return render_template('menu.html', produits=produits)