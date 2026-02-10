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

from models import Chantier, ChantierAssignment

@users_bp.route('/nouveau', methods=['GET', 'POST'])
@direction_required
def nouveau():
    current_user = get_current_user()
    chantiers = Chantier.query.filter_by(entreprise_id=current_user.entreprise_id).all()

    if request.method == 'POST':
        telephone = request.form.get('telephone')
        pin = request.form.get('pin')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role = request.form.get('role')
        role_label = request.form.get('role_label')
        selected_chantiers = request.form.getlist('chantiers')
        
        if len(pin) != 4 or not pin.isdigit():
            flash('Le PIN doit contenir exactement 4 chiffres', 'danger')
            return render_template('users/nouveau.html', chantiers=chantiers)
        
        existing = User.query.filter_by(telephone=telephone).first()
        if existing:
            flash('Ce numéro de téléphone est déjà utilisé', 'danger')
            return render_template('users/nouveau.html', chantiers=chantiers)
        
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
        db.session.flush() # Get ID before commit

        # Add assignments
        for chantier_id in selected_chantiers:
            assignment = ChantierAssignment(
                user_id=user.id,
                chantier_id=int(chantier_id),
                actif=True
            )
            db.session.add(assignment)

        db.session.commit()
        
        flash('Utilisateur créé avec succès', 'success')
        return redirect(url_for('users.liste'))
    
    return render_template('users/nouveau.html', chantiers=chantiers)

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

    chantiers = Chantier.query.filter_by(entreprise_id=current_user.entreprise_id).all()
    current_assignments = [a.chantier_id for a in user.assignments.filter_by(actif=True).all()]

    if request.method == 'POST':
        user.telephone = request.form.get('telephone')
        user.nom = request.form.get('nom')
        user.prenom = request.form.get('prenom')
        user.role = request.form.get('role')
        user.role_label = request.form.get('role_label')
        user.actif = 'actif' in request.form
        
        # Update Assignments
        selected_chantiers = list(map(int, request.form.getlist('chantiers')))

        # Deactivate removed assignments
        for assignment in user.assignments:
            if assignment.chantier_id not in selected_chantiers:
                assignment.actif = False
            elif not assignment.actif:
                assignment.actif = True # Reactivate if re-selected but was inactive

        # Add new assignments
        existing_ids = [a.chantier_id for a in user.assignments]
        for chantier_id in selected_chantiers:
            if chantier_id not in existing_ids:
                new_assignment = ChantierAssignment(
                    user_id=user.id,
                    chantier_id=chantier_id,
                    actif=True
                )
                db.session.add(new_assignment)

        new_pin = request.form.get('pin')
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                flash('Le PIN doit contenir exactement 4 chiffres', 'danger')
                return render_template('users/modifier.html', user=user, chantiers=chantiers, current_assignments=current_assignments)
            user.pin_hash = hash_pin(new_pin)
        
        db.session.commit()
        flash('Utilisateur modifié avec succès', 'success')
        return redirect(url_for('users.liste'))
    
    return render_template('users/modifier.html', user=user, chantiers=chantiers, current_assignments=current_assignments)

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
