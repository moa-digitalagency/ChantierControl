from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import db, User, Chantier, ChantierAssignment, Entreprise, Ouvrier, Pointage, Achat, Heure, Avance
from security import admin_required, get_current_user, hash_pin, get_manageable_roles
from datetime import datetime, date
import json
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_admin_entreprise():
    user = get_current_user()
    if user and user.role == 'admin':
        return user.entreprise
    return None

@admin_bp.route('/')
@admin_required
def index():
    user = get_current_user()
    
    if user.role == 'super_admin':
        return redirect(url_for('superadmin.index'))
    
    entreprise = user.entreprise
    if not entreprise:
        flash('Aucune entreprise associée à votre compte', 'danger')
        return redirect(url_for('dashboard.index'))
    
    users = User.query.filter(
        User.entreprise_id == entreprise.id,
        User.role.in_(['direction', 'chef_chantier', 'responsable_achats'])
    ).order_by(User.role, User.nom).all()
    
    chantiers = Chantier.query.filter_by(entreprise_id=entreprise.id).order_by(Chantier.nom).all()
    
    return render_template('admin/index.html',
                         entreprise=entreprise,
                         users=users,
                         chantiers=chantiers)

@admin_bp.route('/user/new', methods=['GET', 'POST'])
@admin_required
def nouvel_utilisateur():
    user = get_current_user()
    
    if user.role == 'super_admin':
        return redirect(url_for('superadmin.nouvel_admin'))
    
    entreprise = user.entreprise
    roles = get_manageable_roles(user.role)
    
    role_labels = {
        'direction': 'Direction',
        'chef_chantier': 'Chef de Chantier',
        'responsable_achats': 'Responsable Achats'
    }
    
    if request.method == 'POST':
        telephone = request.form.get('telephone', '').strip()
        pin = request.form.get('pin', '').strip()
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        role = request.form.get('role')
        role_label = request.form.get('role_label', '').strip()
        
        if not all([telephone, pin, nom, prenom, role]):
            flash('Tous les champs sont requis', 'danger')
            return render_template('admin/user_form.html', 
                                 roles=roles, role_labels=role_labels, entreprise=entreprise)
        
        if role not in roles:
            flash('Rôle non autorisé', 'danger')
            return redirect(url_for('admin.index'))
        
        if len(pin) != 4 or not pin.isdigit():
            flash('Le PIN doit être composé de 4 chiffres', 'danger')
            return render_template('admin/user_form.html', 
                                 roles=roles, role_labels=role_labels, entreprise=entreprise)
        
        existing = User.query.filter_by(telephone=telephone).first()
        if existing:
            flash('Ce numéro de téléphone est déjà utilisé', 'danger')
            return render_template('admin/user_form.html', 
                                 roles=roles, role_labels=role_labels, entreprise=entreprise)
        
        new_user = User(
            telephone=telephone,
            pin_hash=hash_pin(pin),
            nom=nom,
            prenom=prenom,
            role=role,
            role_label=role_label,
            entreprise_id=entreprise.id,
            created_by_id=user.id
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Utilisateur {prenom} {nom} créé avec succès', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/user_form.html', 
                         roles=roles, role_labels=role_labels, entreprise=entreprise)

@admin_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def modifier_utilisateur(id):
    current_user = get_current_user()
    
    if current_user.role == 'super_admin':
        return redirect(url_for('superadmin.modifier_admin', id=id))
    
    entreprise = current_user.entreprise
    target_user = db.session.get(User, id)
    
    if not target_user or target_user.entreprise_id != entreprise.id:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('admin.index'))
    
    if target_user.role not in get_manageable_roles(current_user.role):
        flash('Vous ne pouvez pas modifier cet utilisateur', 'danger')
        return redirect(url_for('admin.index'))
    
    roles = get_manageable_roles(current_user.role)
    role_labels = {
        'direction': 'Direction',
        'chef_chantier': 'Chef de Chantier',
        'responsable_achats': 'Responsable Achats'
    }
    
    if request.method == 'POST':
        target_user.nom = request.form.get('nom', '').strip()
        target_user.prenom = request.form.get('prenom', '').strip()
        target_user.role = request.form.get('role')
        target_user.role_label = request.form.get('role_label', '').strip()
        target_user.actif = 'actif' in request.form
        
        if target_user.role not in roles:
            flash('Rôle non autorisé', 'danger')
            return render_template('admin/user_form.html', 
                                 user=target_user, roles=roles, role_labels=role_labels, entreprise=entreprise)
        
        new_pin = request.form.get('pin', '').strip()
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                flash('Le PIN doit être composé de 4 chiffres', 'danger')
                return render_template('admin/user_form.html', 
                                     user=target_user, roles=roles, role_labels=role_labels, entreprise=entreprise)
            target_user.pin_hash = hash_pin(new_pin)
        
        db.session.commit()
        flash('Utilisateur mis à jour', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/user_form.html', 
                         user=target_user, roles=roles, role_labels=role_labels, entreprise=entreprise)

@admin_bp.route('/user/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_utilisateur(id):
    current_user = get_current_user()
    
    if current_user.role == 'super_admin':
        return redirect(url_for('superadmin.toggle_admin', id=id))
    
    entreprise = current_user.entreprise
    target_user = db.session.get(User, id)
    
    if target_user and target_user.entreprise_id == entreprise.id:
        if target_user.role in get_manageable_roles(current_user.role):
            target_user.actif = not target_user.actif
            db.session.commit()
            status = "activé" if target_user.actif else "désactivé"
            flash(f'Utilisateur {status}', 'success')
    
    return redirect(url_for('admin.index'))

@admin_bp.route('/chantier/new', methods=['GET', 'POST'])
@admin_required
def nouveau_chantier():
    current_user = get_current_user()
    
    if current_user.role == 'super_admin':
        flash('Super Admin ne peut pas créer de chantiers directement', 'warning')
        return redirect(url_for('superadmin.index'))
    
    entreprise = current_user.entreprise
    
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        adresse = request.form.get('adresse', '').strip()
        budget = request.form.get('budget_previsionnel', '0')
        
        if not nom:
            flash('Le nom du chantier est requis', 'danger')
            return render_template('admin/chantier_form.html', entreprise=entreprise)
        
        try:
            budget_float = float(budget) if budget else 0
        except ValueError:
            budget_float = 0
        
        chantier = Chantier(
            nom=nom,
            adresse=adresse,
            budget_previsionnel=budget_float,
            entreprise_id=entreprise.id
        )
        db.session.add(chantier)
        db.session.commit()
        
        flash(f'Chantier "{nom}" créé avec succès', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/chantier_form.html', entreprise=entreprise)

@admin_bp.route('/parametres', methods=['GET', 'POST'])
@admin_required
def parametres():
    current_user = get_current_user()

    if current_user.role == 'super_admin':
        return redirect(url_for('superadmin.parametres'))

    entreprise = current_user.entreprise
    if not entreprise:
        flash('Aucune entreprise associée', 'danger')
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        entreprise.nom = request.form.get('nom', '').strip()
        entreprise.adresse = request.form.get('adresse', '').strip()
        entreprise.telephone = request.form.get('telephone', '').strip()
        entreprise.email = request.form.get('email', '').strip()

        if not entreprise.nom:
            flash('Le nom de l\'entreprise est requis', 'danger')
        else:
            db.session.commit()
            flash('Paramètres mis à jour avec succès', 'success')
            return redirect(url_for('admin.parametres'))

    return render_template('admin/settings.html', entreprise=entreprise)

@admin_bp.route('/sauvegarde', methods=['GET'])
@admin_required
def sauvegarde():
    current_user = get_current_user()
    if current_user.role == 'super_admin':
        return redirect(url_for('superadmin.index'))

    return render_template('admin/sauvegarde.html')

@admin_bp.route('/sauvegarde/download')
@admin_required
def download_backup():
    current_user = get_current_user()
    ent_id = current_user.entreprise_id
    if not ent_id:
        flash("Erreur", "danger")
        return redirect(url_for('admin.index'))

    # Helper to serialize list of objects
    def serialize(query):
        res = []
        for item in query:
            d = {}
            for col in item.__table__.columns:
                val = getattr(item, col.name)
                if isinstance(val, (datetime, date)):
                    val = val.isoformat()
                d[col.name] = val
            res.append(d)
        return res

    data = {}
    data['entreprise'] = serialize(Entreprise.query.filter_by(id=ent_id).all())
    data['users'] = serialize(User.query.filter_by(entreprise_id=ent_id).all())
    data['chantiers'] = serialize(Chantier.query.filter_by(entreprise_id=ent_id).all())
    data['ouvriers'] = serialize(Ouvrier.query.filter_by(entreprise_id=ent_id).all())

    # Related data
    data['pointages'] = serialize(Pointage.query.join(Ouvrier).filter(Ouvrier.entreprise_id == ent_id).all())
    data['achats'] = serialize(Achat.query.join(Chantier).filter(Chantier.entreprise_id == ent_id).all())
    data['heures'] = serialize(Heure.query.join(Chantier).filter(Chantier.entreprise_id == ent_id).all())
    data['avances'] = serialize(Avance.query.join(Chantier).filter(Chantier.entreprise_id == ent_id).all())
    data['assignments'] = serialize(ChantierAssignment.query.join(Chantier).filter(Chantier.entreprise_id == ent_id).all())

    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    output = io.BytesIO(json_str.encode('utf-8'))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        output,
        download_name=f"backup_{current_user.entreprise.nom}_{timestamp}.json",
        as_attachment=True,
        mimetype='application/json'
    )

@admin_bp.route('/sauvegarde/restore', methods=['POST'])
@admin_required
def restore_backup():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('admin.sauvegarde'))

    file = request.files['file']
    if not file.filename.endswith('.json'):
        flash('Format invalide. JSON requis.', 'danger')
        return redirect(url_for('admin.sauvegarde'))

    # Placeholder for restore logic
    flash("La restauration automatique est désactivée pour des raisons de sécurité. Veuillez contacter le support technique.", "warning")
    return redirect(url_for('admin.sauvegarde'))
