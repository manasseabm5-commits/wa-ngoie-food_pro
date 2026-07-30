from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import User
from extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Cet email est déjà utilisé par un autre compte.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            nom=nom,
            email=email,
            password=hashed_pw,
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_user = request.form.get('email')
        password = request.form.get('password')

        # Permet de se connecter avec l'email ou directement avec le pseudonyme 'wangoie'
        if email_or_user == 'wangoie':
            user = User.query.filter_by(is_admin=True).first()
        else:
            user = User.query.filter_by(email=email_or_user).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('home.index'))
        else:
            flash('Adresse email ou mot de passe incorrect.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('home.index'))