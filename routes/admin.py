from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from models import Order, Product
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
    commandes = Order.query.order_by(Order.id.desc()).all()
    
    # CALCULS DES STATISTIQUES POUR L'ADMINISTRATEUR
    aujourdhui = datetime.now().date()
    commandes_validees = [c for c in commandes if c.status in ['Validée', 'Livrée']]
    
    ventes_jour = sum(c.total_price for c in commandes_validees if c.created_at and c.created_at.date() == aujourdhui)
    ventes_mois = sum(c.total_price for c in commandes_validees if c.created_at and c.created_at.month == aujourdhui.month and c.created_at.year == aujourdhui.year)
    total_validees = len(commandes_validees)

    return render_template(
        'admin/dashboard.html', 
        commandes=commandes, 
        ventes_jour=ventes_jour, 
        ventes_mois=ventes_mois, 
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


@admin_bp.route('/rapport-pdf')
@login_required
@admin_required
def exporter_rapport():
    type_rapport = request.args.get('type', 'jour')
    aujourdhui = datetime.now()
    commandes_validees = Order.query.filter(Order.status.in_(['Validée', 'Livrée'])).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    # En-tête Rapport Admin
    elements.append(Paragraph("<b>WA NGOIE FAST-FOOD - ESPACE DIRECTION</b>", ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1a1a1a'))))
    
    if type_rapport == 'jour':
        titre = f"Rapport Journalier des Ventes par Tranche Horaire ({aujourdhui.strftime('%d/%m/%Y')})"
    elif type_rapport == 'mois':
        titre = f"Rapport Mensuel des Ventes ({aujourdhui.strftime('%m/%Y')})"
    else:
        titre = f"Rapport Annuel des Ventes ({aujourdhui.strftime('%Y')})"

    elements.append(Paragraph(f"<b>{titre}</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    if type_rapport == 'jour':
        # DÉCOUPAGE PAR HEURE (00h00 à 23h00)
        ventes_par_heure = {h: 0 for h in range(24)}
        nb_cmd_par_heure = {h: 0 for h in range(24)}

        for c in commandes_validees:
            if c.created_at and c.created_at.date() == aujourdhui.date():
                h = c.created_at.hour
                ventes_par_heure[h] += c.total_price
                nb_cmd_par_heure[h] += 1

        table_data = [["Créneau Horaire", "Commandes Validées", "Chiffre d'Affaires (FC)"]]
        total_ca = 0
        total_cmd = 0

        for h in range(24):
            if nb_cmd_par_heure[h] > 0 or h in [10, 11, 12, 13, 14, 18, 19, 20, 21]: # Affiche les heures clés
                ca = ventes_par_heure[h]
                cmd = nb_cmd_par_heure[h]
                total_ca += ca
                total_cmd += cmd
                table_data.append([f"{h:02d}h00 - {h+1:02d}h00", str(cmd), f"{ca:,.0f} FC".replace(',', ' ')])

        table_data.append(["TOTAL DU JOUR", str(total_cmd), f"{total_ca:,.0f} FC".replace(',', ' ')])

    else:
        # RAPPORT SIMPLIFIÉ
        total_ca = sum(c.total_price for c in commandes_validees)
        table_data = [
            ["Indicateur", "Valeur"],
            ["Total Commandes Validées", str(len(commandes_validees))],
            ["Chiffre d'Affaires Cumulé", f"{total_ca:,.0f} FC".replace(',', ' ')]
        ]

    t = Table(table_data, colWidths=[200, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d97706')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f3f4f6')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<i>Rapport extrait le {aujourdhui.strftime('%d/%m/%Y à %H:%M')} par l'administrateur.</i>", styles['Italic']))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Rapport_Ventes_{type_rapport}.pdf'
    return response