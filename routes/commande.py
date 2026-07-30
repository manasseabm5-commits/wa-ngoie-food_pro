from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from models import Order, Product, OrderItem
from extensions import db
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

commande_bp = Blueprint('commande', __name__, url_prefix='/commande')


# 1. ROUTE POUR PASSER UNE COMMANDE DEPUIS LE MENU
@commande_bp.route('/commander/<int:product_id>', methods=['GET', 'POST'])
@login_required
def commander(product_id):
    produit = db.session.get(Product, product_id)
    if not produit:
        flash("Ce produit n'existe pas.", "danger")
        return redirect(url_for('menu.menu'))

    if request.method == 'POST':
        try:
            quantite = int(request.form.get('quantite', 1))
            telephone = request.form.get('telephone', '')
            adresse = request.form.get('adresse', 'Kintambo, Kinshasa')

            # Création de la commande
            nouvelle_commande = Order(
                user_id=current_user.id,
                total_price=produit.prix * quantite,
                telephone=telephone,
                adresse_livraison=adresse,
                status='En attente'
            )
            db.session.add(nouvelle_commande)
            db.session.commit()

            # Ajout du produit dans les détails de la commande
            item = OrderItem(
                order_id=nouvelle_commande.id,
                product_id=produit.id,
                quantity=quantite,
                price=produit.prix
            )
            db.session.add(item)
            db.session.commit()

            flash(f"Commande passée avec succès ! Code : {nouvelle_commande.code_recu}. Attendez la validation de l'administrateur.", "success")
            return redirect(url_for('commande.mes_commandes'))

        except Exception as e:
            db.session.rollback()
            print(f"[ERREUR COMMANDER] : {e}")
            flash("Une erreur s'est produite lors de la commande.", "danger")
            return redirect(url_for('menu.menu'))

    return render_template('commande/commander.html', produit=produit)


# 2. HISTORIQUE DES COMMANDES CLIENT
@commande_bp.route('/mes-commandes')
@login_required
def mes_commandes():
    commandes = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template('commande/mes_commandes.html', commandes=commandes)


# 3. GÉNÉRATION ET TÉLÉCHARGEMENT DU REÇU PDF
@commande_bp.route('/<int:order_id>/recu-pdf')
@login_required
def telecharger_recu(order_id):
    commande = db.session.get(Order, order_id)
    
    if not commande or commande.user_id != current_user.id:
        flash("Commande introuvable ou accès non autorisé.", "danger")
        return redirect(url_for('commande.mes_commandes'))
    
    # RÈGLE MÉTIER STRICTE : Génération autorisée uniquement si la commande est Validée ou Livrée
    if commande.status not in ['Validée', 'Livrée']:
        flash("Votre reçu sera disponible dès que l'administrateur aura validé votre commande.", "warning")
        return redirect(url_for('commande.mes_commandes'))

    # Génération du document PDF en mémoire
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    # En-tête du Reçu
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#d97706'), spaceAfter=4)
    elements.append(Paragraph("<b>WA NGOIE FAST-FOOD</b>", title_style))
    elements.append(Paragraph("Kintambo, Kinshasa • Service de Livraison & Sur Place", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Détails du Client et de la Commande
    elements.append(Paragraph("<b>REÇU DE COMMANDE OFFICIEL</b>", styles['Heading2']))
    elements.append(Paragraph(f"<b>Code Unique :</b> <font color='#d97706'>{commande.code_recu}</font>", styles['Normal']))
    elements.append(Paragraph(f"<b>Date :</b> {commande.created_at.strftime('%d/%m/%Y à %H:%M') if commande.created_at else 'Récemment'}", styles['Normal']))
    elements.append(Paragraph(f"<b>Client :</b> {current_user.nom if hasattr(current_user, 'nom') else current_user.email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Téléphone :</b> {commande.telephone}", styles['Normal']))
    elements.append(Paragraph(f"<b>Adresse de livraison :</b> {commande.adresse_livraison}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Tableau Récapitulatif
    data = [
        ["Référence", "Statut", "Montant Total"],
        [commande.code_recu, commande.status, f"{commande.total_price:,.0f} FC".replace(',', ' ')]
    ]
    t = Table(data, colWidths=[200, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
    ]))
    elements.append(t)
    
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("<i>Remettez ce reçu ou présentez votre code unique au livreur à la réception.</i>", styles['Italic']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Merci pour votre confiance chez Wa Ngoie Fast-Food !</b>", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Recu_{commande.code_recu}.pdf'
    return response