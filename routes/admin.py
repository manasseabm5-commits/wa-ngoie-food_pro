from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from models import Order, Product, OrderItem
from extensions import db
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    toutes_commandes = Order.query.order_by(Order.id.desc()).all()
    commandes_visibles = Order.query.filter_by(is_archived=False).order_by(Order.id.desc()).all()
    produits = Product.query.order_by(Product.id.desc()).all()
    
    aujourdhui = datetime.now().date()
    commandes_validees = [c for c in toutes_commandes if c.status in ['Validée', 'Livrée']]
    
    ventes_jour = sum(c.total_price for c in commandes_validees if c.created_at and c.created_at.date() == aujourdhui)
    ventes_mois = sum(c.total_price for c in commandes_validees if c.created_at and c.created_at.month == aujourdhui.month and c.created_at.year == aujourdhui.year)
    
    ventes_sur_place = sum(c.total_price for c in commandes_validees if getattr(c, 'type_commande', 'Livraison') == 'Sur place' and c.created_at and c.created_at.date() == aujourdhui)
    total_sur_place = sum(1 for c in toutes_commandes if getattr(c, 'type_commande', 'Livraison') == 'Sur place' and c.created_at and c.created_at.date() == aujourdhui)
    
    total_validees = len(commandes_validees)

    return render_template(
        'admin/dashboard.html', 
        commandes=commandes_visibles,
        produits=produits,
        ventes_jour=ventes_jour, 
        ventes_mois=ventes_mois, 
        ventes_sur_place=ventes_sur_place,
        total_sur_place=total_sur_place,
        total_validees=total_validees
    )


@admin_bp.route('/commande/<int:order_id>/statut', methods=['POST'])
@login_required
@admin_required
def changer_statut(order_id):
    commande = db.session.get(Order, order_id)
    if commande:
        nouveau_statut = request.form.get('statut')
        if nouveau_statut:
            commande.status = nouveau_statut
            db.session.commit()
            flash(f"Statut de la commande #{order_id} mis à jour : {nouveau_statut}", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/commande/supprimer/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def supprimer_commande(order_id):
    commande = db.session.get(Order, order_id)
    if commande:
        action = request.form.get('action_suppression')
        if action == 'garder_ca':
            commande.is_archived = True
            db.session.commit()
            flash(f"Commande #{order_id} masquée. L'espace est libéré mais le CA est conservé.", "info")
        else:
            OrderItem.query.filter_by(order_id=commande.id).delete()
            db.session.delete(commande)
            db.session.commit()
            flash(f"Commande #{order_id} définitivement supprimée et annulée du CA.", "success")
    else:
        flash("Commande introuvable.", "danger")
        
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/produit/ajouter', methods=['GET', 'POST'])
@login_required
@admin_required
def ajouter_produit():
    if request.method == 'POST':
        nom = request.form.get('nom')
        description = request.form.get('description')
        try:
            prix = float(request.form.get('prix'))
        except ValueError:
            flash("Prix invalide.", "danger")
            return redirect(url_for('admin.ajouter_produit'))
            
        image = request.form.get('image')
        nouveau = Product(nom=nom, description=description, prix=prix, image=image)
        db.session.add(nouveau)
        db.session.commit()
        flash(f"Plat '{nom}' ajouté au menu avec succès !", "success")
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/ajouter_produit.html')


@admin_bp.route('/produit/modifier/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_produit(product_id):
    produit = db.session.get(Product, product_id)
    if not produit:
        flash("Plat introuvable.", "danger")
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        produit.nom = request.form.get('nom')
        produit.description = request.form.get('description')
        try:
            produit.prix = float(request.form.get('prix'))
        except ValueError:
            flash("Prix invalide.", "danger")
            return redirect(url_for('admin.modifier_produit', product_id=product_id))
            
        produit.image = request.form.get('image')
        db.session.commit()
        flash(f"Plat '{produit.nom}' mis à jour !", "success")
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/modifier_produit.html', produit=produit)


@admin_bp.route('/produit/supprimer/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def supprimer_produit(product_id):
    produit = db.session.get(Product, product_id)
    if produit:
        db.session.delete(produit)
        db.session.commit()
        flash("Plat supprimé du menu avec succès.", "success")
    return redirect(url_for('admin.dashboard'))


# --- EXPORTATION PDF COMPLÈTE & CORRIGÉE ---

@admin_bp.route('/rapport-pdf')
@login_required
@admin_required
def exporter_rapport():
    type_rapport = request.args.get('type', 'jour')
    aujourdhui = datetime.now()
    
    toutes_commandes_validees = Order.query.filter(Order.status.in_(['Validée', 'Livrée'])).all()

    commandes_filtrees = []
    for c in toutes_commandes_validees:
        if not c.created_at:
            continue
        if type_rapport == 'jour' and c.created_at.date() == aujourdhui.date():
            commandes_filtrees.append(c)
        elif type_rapport == 'mois' and c.created_at.month == aujourdhui.month and c.created_at.year == aujourdhui.year:
            commandes_filtrees.append(c)
        elif type_rapport == 'annee' and c.created_at.year == aujourdhui.year:
            commandes_filtrees.append(c)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    # Styles spécifiques pour les cellules du tableau (évite les bugs d'affichage HTML)
    cell_style = ParagraphStyle('CellText', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#111111'))
    cell_style_right = ParagraphStyle('CellTextRight', parent=cell_style, alignment=2)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.white, fontName='Helvetica-Bold')
    header_style_right = ParagraphStyle('HeaderStyleRight', parent=header_style, alignment=2)
    total_style = ParagraphStyle('TotalStyle', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor('#111111'), fontName='Helvetica-Bold')
    total_style_right = ParagraphStyle('TotalStyleRight', parent=total_style, alignment=2)

    elements = []

    elements.append(Paragraph("<b>WA NGOIE FAST-FOOD - ESPACE DIRECTION</b>", ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1a1a1a'))))
    
    if type_rapport == 'jour':
        titre = f"Rapport Détaillé des Ventes du Jour ({aujourdhui.strftime('%d/%m/%Y')})"
    elif type_rapport == 'mois':
        titre = f"Rapport Détaillé des Ventes du Mois ({aujourdhui.strftime('%m/%Y')})"
    else:
        titre = f"Rapport Détaillé des Ventes de l'Année ({aujourdhui.strftime('%Y')})"

    elements.append(Paragraph(f"<b>{titre}</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Construction des en-têtes avec Paragraph
    table_data = [[
        Paragraph("Code", header_style),
        Paragraph("Client & Tél", header_style),
        Paragraph("Plats Commandés", header_style),
        Paragraph("Type / Adresse", header_style),
        Paragraph("Date & Heure", header_style),
        Paragraph("Montant", header_style_right),
    ]]
    total_ca = 0

    for c in commandes_filtrees:
        nom_client = c.client.nom if c.client else 'Client Comptoir'
        telephone = c.telephone if c.telephone else 'N/A'
        client_info = f"<b>{nom_client}</b><br/>{telephone}"
        
        # Récupération des plats commandés
        items_db = OrderItem.query.filter_by(order_id=c.id).all()
        items_list = []
        for item in items_db:
            nom_plat = item.product.nom if item.product else "Plat"
            qty = getattr(item, 'quantity', 1)
            items_list.append(f"• {qty}x {nom_plat}")
        plats_str = "<br/>".join(items_list) if items_list else "Aucun plat spécifié"

        # Gestion du type de commande et adresse
        type_cmd = getattr(c, 'type_commande', 'En ligne')
        adresse = getattr(c, 'adresse_livraison', '')
        
        if type_cmd == 'Sur place':
            type_adresse = "<b>Sur place</b>"
        else:
            type_adresse = f"<b>En ligne</b><br/>{adresse if adresse else 'Aucune adresse'}"

        date_str = c.created_at.strftime('%d/%m/%Y<br/>%H:%M') if c.created_at else 'N/A'
        montant_str = f"{c.total_price:,.0f} FC".replace(',', ' ')
        
        total_ca += c.total_price
        
        # Ajout de chaque cellule enveloppée dans un Paragraph
        table_data.append([
            Paragraph(c.code_recu, cell_style),
            Paragraph(client_info, cell_style),
            Paragraph(plats_str, cell_style),
            Paragraph(type_adresse, cell_style),
            Paragraph(date_str, cell_style),
            Paragraph(montant_str, cell_style_right),
        ])

    if not commandes_filtrees:
        table_data.append([
            Paragraph("Aucune commande validée sur cette période", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("0 FC", cell_style_right),
        ])

    table_data.append([
        Paragraph("TOTAL GÉNÉRAL", total_style),
        Paragraph("", total_style),
        Paragraph("", total_style),
        Paragraph("", total_style),
        Paragraph("", total_style),
        Paragraph(f"{total_ca:,.0f} FC".replace(',', ' '), total_style_right),
    ])

    t = Table(table_data, colWidths=[70, 95, 130, 105, 75, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d97706')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f9fafb')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f3f4f6')),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"<i>Rapport extrait le {aujourdhui.strftime('%d/%m/%Y à %H:%M')} par l'administrateur. Nombre de commandes validées : {len(commandes_filtrees)}</i>", ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8)))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Rapport_Ventes_{type_rapport}.pdf'
    return response