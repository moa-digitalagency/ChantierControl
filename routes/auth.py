import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from security import hash_pin, verify_pin

auth_bp = Blueprint('auth', __name__)

# Simple in-memory rate limiting: IP -> [timestamp1, timestamp2, ...]
login_attempts = {}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Rate Limiting Logic
        ip = request.remote_addr
        now = time.time()

        # Clean up old attempts (older than 15 minutes)
        if ip in login_attempts:
            login_attempts[ip] = [t for t in login_attempts[ip] if now - t < 900]

        attempts = login_attempts.get(ip, [])
        if len(attempts) >= 5:
            flash('Trop de tentatives échouées. Veuillez réessayer dans 15 minutes.', 'danger')
            return render_template('auth/login.html')

        telephone = request.form.get('telephone', '').strip()
        pin = request.form.get('pin', '').strip()
        
        if not telephone or not pin:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(telephone=telephone, actif=True).first()
        
        if user and verify_pin(user.pin_hash, pin):
            # Reset attempts on success
            if ip in login_attempts:
                del login_attempts[ip]

            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_nom'] = f"{user.prenom} {user.nom}"
            flash(f'Bienvenue {user.prenom}!', 'success')
            return redirect(url_for('dashboard.index'))
        
        # Record failed attempt
        login_attempts.setdefault(ip, []).append(now)

        flash('Numéro de téléphone ou PIN incorrect', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('auth.login'))
