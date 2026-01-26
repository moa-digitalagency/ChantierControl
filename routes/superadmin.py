from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Entreprise
from security import super_admin_required, get_current_user, hash_pin
from datetime import datetime

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

@superadmin_bp.route('/')
@super_admin_required
def index():
    entreprises = Entreprise.query.order_by(Entreprise.nom).all()
    admins = User.query.filter_by(role='admin').order_by(User.nom).all()
    
    return render_template('superadmin/index.html',
                         entreprises=entreprises,
                         admins=admins)

@superadmin_bp.route('/entreprise/new', methods=['GET', 'POST'])
@super_admin_required
def nouvelle_entreprise():
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        adresse = request.form.get('adresse', '').strip()
        telephone = request.form.get('telephone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not nom:
            flash('Le nom de l\'entreprise est requis', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        existing = Entreprise.query.filter_by(nom=nom).first()
        if existing:
            flash('Une entreprise avec ce nom existe déjà', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        entreprise = Entreprise(
            nom=nom,
            adresse=adresse,
            telephone=telephone,
            email=email
        )
        db.session.add(entreprise)
        db.session.commit()
        
        flash(f'Entreprise "{nom}" créée avec succès', 'success')
        return redirect(url_for('superadmin.index'))
    
    return render_template('superadmin/entreprise_form.html')

@superadmin_bp.route('/entreprise/<int:id>/edit', methods=['GET', 'POST'])
@super_admin_required
def modifier_entreprise(id):
    entreprise = db.session.get(Entreprise, id)
    if not entreprise:
        flash('Entreprise non trouvée', 'danger')
        return redirect(url_for('superadmin.index'))
    
    if request.method == 'POST':
        entreprise.nom = request.form.get('nom', '').strip()
        entreprise.adresse = request.form.get('adresse', '').strip()
        entreprise.telephone = request.form.get('telephone', '').strip()
        entreprise.email = request.form.get('email', '').strip()
        entreprise.actif = 'actif' in request.form
        
        db.session.commit()
        flash('Entreprise mise à jour', 'success')
        return redirect(url_for('superadmin.index'))
    
    return render_template('superadmin/entreprise_form.html', entreprise=entreprise)

@superadmin_bp.route('/admin/new', methods=['GET', 'POST'])
@super_admin_required
def nouvel_admin():
    entreprises = Entreprise.query.filter_by(actif=True).order_by(Entreprise.nom).all()
    
    if request.method == 'POST':
        telephone = request.form.get('telephone', '').strip()
        pin = request.form.get('pin', '').strip()
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        entreprise_id = request.form.get('entreprise_id')
        
        if not all([telephone, pin, nom, prenom, entreprise_id]):
            flash('Tous les champs sont requis', 'danger')
            return render_template('superadmin/admin_form.html', entreprises=entreprises)
        
        if len(pin) != 4 or not pin.isdigit():
            flash('Le PIN doit être composé de 4 chiffres', 'danger')
            return render_template('superadmin/admin_form.html', entreprises=entreprises)
        
        existing = User.query.filter_by(telephone=telephone).first()
        if existing:
            flash('Ce numéro de téléphone est déjà utilisé', 'danger')
            return render_template('superadmin/admin_form.html', entreprises=entreprises)
        
        current_user = get_current_user()
        
        admin = User(
            telephone=telephone,
            pin_hash=hash_pin(pin),
            nom=nom,
            prenom=prenom,
            role='admin',
            entreprise_id=int(entreprise_id),
            created_by_id=current_user.id
        )
        db.session.add(admin)
        db.session.commit()
        
        flash(f'Administrateur {prenom} {nom} créé avec succès', 'success')
        return redirect(url_for('superadmin.index'))
    
    return render_template('superadmin/admin_form.html', entreprises=entreprises)

@superadmin_bp.route('/admin/<int:id>/edit', methods=['GET', 'POST'])
@super_admin_required
def modifier_admin(id):
    admin = db.session.get(User, id)
    if not admin or admin.role != 'admin':
        flash('Administrateur non trouvé', 'danger')
        return redirect(url_for('superadmin.index'))
    
    entreprises = Entreprise.query.filter_by(actif=True).order_by(Entreprise.nom).all()
    
    if request.method == 'POST':
        admin.nom = request.form.get('nom', '').strip()
        admin.prenom = request.form.get('prenom', '').strip()
        admin.entreprise_id = int(request.form.get('entreprise_id'))
        admin.actif = 'actif' in request.form
        
        new_pin = request.form.get('pin', '').strip()
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                flash('Le PIN doit être composé de 4 chiffres', 'danger')
                return render_template('superadmin/admin_form.html', 
                                     admin=admin, entreprises=entreprises)
            admin.pin_hash = hash_pin(new_pin)
        
        db.session.commit()
        flash('Administrateur mis à jour', 'success')
        return redirect(url_for('superadmin.index'))
    
    return render_template('superadmin/admin_form.html', admin=admin, entreprises=entreprises)

@superadmin_bp.route('/admin/<int:id>/toggle', methods=['POST'])
@super_admin_required
def toggle_admin(id):
    admin = db.session.get(User, id)
    if admin and admin.role == 'admin':
        admin.actif = not admin.actif
        db.session.commit()
        status = "activé" if admin.actif else "désactivé"
        flash(f'Administrateur {status}', 'success')
    return redirect(url_for('superadmin.index'))
