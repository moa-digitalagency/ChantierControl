from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from security import direction_required, hash_pin, get_current_user

users_bp = Blueprint('users', __name__, url_prefix='/utilisateurs')

@users_bp.route('/')
@direction_required
def liste():
    current_user = get_current_user()
    users = User.query.filter_by(
        entreprise_id=current_user.entreprise_id
    ).filter(User.role != 'admin').order_by(User.nom).all()
    return render_template('users/liste.html', users=users)

@users_bp.route('/nouveau', methods=['GET', 'POST'])
@direction_required
def nouveau():
    current_user = get_current_user()

    if request.method == 'POST':
        telephone = request.form.get('telephone')
        pin = request.form.get('pin')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role = request.form.get('role')
        role_label = request.form.get('role_label')
        
        if len(pin) != 4 or not pin.isdigit():
            flash('Le PIN doit contenir exactement 4 chiffres', 'danger')
            return render_template('users/nouveau.html')
        
        existing = User.query.filter_by(telephone=telephone).first()
        if existing:
            flash('Ce numéro de téléphone est déjà utilisé', 'danger')
            return render_template('users/nouveau.html')
        
        user = User(
            telephone=telephone,
            pin_hash=hash_pin(pin),
            nom=nom,
            prenom=prenom,
            role=role,
            role_label=role_label,
            entreprise_id=current_user.entreprise_id,
            created_by_id=current_user.id
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Utilisateur créé avec succès', 'success')
        return redirect(url_for('users.liste'))
    
    return render_template('users/nouveau.html')

@users_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@direction_required
def modifier(id):
    current_user = get_current_user()
    user = db.session.get(User, id)

    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('users.liste'))
    
    if user.entreprise_id != current_user.entreprise_id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('users.liste'))

    if request.method == 'POST':
        user.telephone = request.form.get('telephone')
        user.nom = request.form.get('nom')
        user.prenom = request.form.get('prenom')
        user.role = request.form.get('role')
        user.role_label = request.form.get('role_label')
        user.actif = 'actif' in request.form
        
        new_pin = request.form.get('pin')
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                flash('Le PIN doit contenir exactement 4 chiffres', 'danger')
                return render_template('users/modifier.html', user=user)
            user.pin_hash = hash_pin(new_pin)
        
        db.session.commit()
        flash('Utilisateur modifié avec succès', 'success')
        return redirect(url_for('users.liste'))
    
    return render_template('users/modifier.html', user=user)

@users_bp.route('/<int:id>/desactiver', methods=['POST'])
@direction_required
def desactiver(id):
    user = db.session.get(User, id)
    if user:
        user.actif = not user.actif
        db.session.commit()
        status = 'activé' if user.actif else 'désactivé'
        flash(f'Utilisateur {status}', 'success')
    return redirect(url_for('users.liste'))
