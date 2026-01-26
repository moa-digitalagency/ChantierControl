from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Entreprise, Chantier, Achat, Avance, Heure, AppSettings
from security import super_admin_required, get_current_user, hash_pin
from datetime import datetime
from sqlalchemy import func

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

def get_setting(key, default=''):
    setting = AppSettings.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value, category='general'):
    setting = AppSettings.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        setting.category = category
    else:
        setting = AppSettings(key=key, value=value, category=category)
        db.session.add(setting)
    db.session.commit()

@superadmin_bp.route('/')
@super_admin_required
def index():
    nb_entreprises = Entreprise.query.count()
    nb_entreprises_actives = Entreprise.query.filter_by(actif=True).count()
    nb_admins = User.query.filter_by(role='admin').count()
    nb_users = User.query.filter(User.role != 'super_admin').count()
    nb_chantiers = Chantier.query.count()
    nb_chantiers_en_cours = Chantier.query.filter_by(statut='en_cours').count()
    
    total_achats = db.session.query(func.coalesce(func.sum(Achat.montant), 0)).scalar() or 0
    total_avances = db.session.query(func.coalesce(func.sum(Avance.montant), 0)).scalar() or 0
    total_heures = db.session.query(func.coalesce(func.sum(Heure.cout_total), 0)).scalar() or 0
    
    entreprises_recentes = Entreprise.query.order_by(Entreprise.created_at.desc()).limit(5).all()
    
    stats = {
        'nb_entreprises': nb_entreprises,
        'nb_entreprises_actives': nb_entreprises_actives,
        'nb_admins': nb_admins,
        'nb_users': nb_users,
        'nb_chantiers': nb_chantiers,
        'nb_chantiers_en_cours': nb_chantiers_en_cours,
        'total_depenses': total_achats + total_heures,
        'total_avances': total_avances
    }
    
    return render_template('superadmin/dashboard.html',
                         stats=stats,
                         entreprises_recentes=entreprises_recentes)

@superadmin_bp.route('/entreprises')
@super_admin_required
def liste_entreprises():
    entreprises = Entreprise.query.order_by(Entreprise.nom).all()
    return render_template('superadmin/entreprises.html', entreprises=entreprises)

@superadmin_bp.route('/admins')
@super_admin_required
def liste_admins():
    admins = User.query.filter_by(role='admin').order_by(User.nom).all()
    return render_template('superadmin/admins.html', admins=admins)

@superadmin_bp.route('/entreprise/new', methods=['GET', 'POST'])
@super_admin_required
def nouvelle_entreprise():
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        adresse = request.form.get('adresse', '').strip()
        telephone = request.form.get('telephone', '').strip()
        email = request.form.get('email', '').strip()
        
        admin_telephone = request.form.get('admin_telephone', '').strip()
        admin_pin = request.form.get('admin_pin', '').strip()
        admin_nom = request.form.get('admin_nom', '').strip()
        admin_prenom = request.form.get('admin_prenom', '').strip()
        
        if not nom:
            flash('Le nom de l\'entreprise est requis', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        if not all([admin_telephone, admin_pin, admin_nom, admin_prenom]):
            flash('Les informations de l\'administrateur principal sont requises', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        if len(admin_pin) != 4 or not admin_pin.isdigit():
            flash('Le PIN doit être composé de 4 chiffres', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        existing = Entreprise.query.filter_by(nom=nom).first()
        if existing:
            flash('Une entreprise avec ce nom existe déjà', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        existing_user = User.query.filter_by(telephone=admin_telephone).first()
        if existing_user:
            flash('Ce numéro de téléphone est déjà utilisé', 'danger')
            return render_template('superadmin/entreprise_form.html')
        
        current_user = get_current_user()
        
        entreprise = Entreprise(
            nom=nom,
            adresse=adresse,
            telephone=telephone,
            email=email
        )
        db.session.add(entreprise)
        db.session.flush()
        
        admin = User(
            telephone=admin_telephone,
            pin_hash=hash_pin(admin_pin),
            nom=admin_nom,
            prenom=admin_prenom,
            role='admin',
            entreprise_id=entreprise.id,
            created_by_id=current_user.id
        )
        db.session.add(admin)
        db.session.flush()
        
        entreprise.admin_principal_id = admin.id
        db.session.commit()
        
        flash(f'Entreprise "{nom}" créée avec l\'admin {admin_prenom} {admin_nom}', 'success')
        return redirect(url_for('superadmin.liste_entreprises'))
    
    return render_template('superadmin/entreprise_form.html')

@superadmin_bp.route('/entreprise/<int:id>/edit', methods=['GET', 'POST'])
@super_admin_required
def modifier_entreprise(id):
    entreprise = db.session.get(Entreprise, id)
    if not entreprise:
        flash('Entreprise non trouvée', 'danger')
        return redirect(url_for('superadmin.liste_entreprises'))
    
    admins = User.query.filter_by(role='admin', entreprise_id=id).all()
    
    if request.method == 'POST':
        entreprise.nom = request.form.get('nom', '').strip()
        entreprise.adresse = request.form.get('adresse', '').strip()
        entreprise.telephone = request.form.get('telephone', '').strip()
        entreprise.email = request.form.get('email', '').strip()
        entreprise.actif = 'actif' in request.form
        
        admin_principal_id = request.form.get('admin_principal_id')
        if admin_principal_id:
            entreprise.admin_principal_id = int(admin_principal_id)
        
        db.session.commit()
        flash('Entreprise mise à jour', 'success')
        return redirect(url_for('superadmin.liste_entreprises'))
    
    return render_template('superadmin/entreprise_form.html', entreprise=entreprise, admins=admins)

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
        is_principal = 'is_principal' in request.form
        
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
        db.session.flush()
        
        if is_principal:
            entreprise = db.session.get(Entreprise, int(entreprise_id))
            if entreprise:
                entreprise.admin_principal_id = admin.id
        
        db.session.commit()
        
        flash(f'Administrateur {prenom} {nom} créé avec succès', 'success')
        return redirect(url_for('superadmin.liste_admins'))
    
    return render_template('superadmin/admin_form.html', entreprises=entreprises)

@superadmin_bp.route('/admin/<int:id>/edit', methods=['GET', 'POST'])
@super_admin_required
def modifier_admin(id):
    admin = db.session.get(User, id)
    if not admin or admin.role != 'admin':
        flash('Administrateur non trouvé', 'danger')
        return redirect(url_for('superadmin.liste_admins'))
    
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
        return redirect(url_for('superadmin.liste_admins'))
    
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
    return redirect(url_for('superadmin.liste_admins'))

@superadmin_bp.route('/parametres', methods=['GET', 'POST'])
@super_admin_required
def parametres():
    if request.method == 'POST':
        set_setting('app_name', request.form.get('app_name', 'Gestion Chantiers'), 'general')
        set_setting('app_description', request.form.get('app_description', ''), 'general')
        set_setting('contact_email', request.form.get('contact_email', ''), 'general')
        set_setting('contact_telephone', request.form.get('contact_telephone', ''), 'general')
        set_setting('currency', request.form.get('currency', 'MAD'), 'general')
        set_setting('seuil_alerte_avance', request.form.get('seuil_alerte_avance', '10000'), 'alertes')
        set_setting('seuil_alerte_budget', request.form.get('seuil_alerte_budget', '80'), 'alertes')
        set_setting('delai_validation_max', request.form.get('delai_validation_max', '24'), 'alertes')
        
        flash('Paramètres enregistrés', 'success')
        return redirect(url_for('superadmin.parametres'))
    
    settings = {
        'app_name': get_setting('app_name', 'Gestion Chantiers'),
        'app_description': get_setting('app_description', ''),
        'contact_email': get_setting('contact_email', ''),
        'contact_telephone': get_setting('contact_telephone', ''),
        'currency': get_setting('currency', 'MAD'),
        'seuil_alerte_avance': get_setting('seuil_alerte_avance', '10000'),
        'seuil_alerte_budget': get_setting('seuil_alerte_budget', '80'),
        'delai_validation_max': get_setting('delai_validation_max', '24')
    }
    
    return render_template('superadmin/parametres.html', settings=settings)

@superadmin_bp.route('/seo', methods=['GET', 'POST'])
@super_admin_required
def seo():
    if request.method == 'POST':
        set_setting('meta_title', request.form.get('meta_title', ''), 'seo')
        set_setting('meta_description', request.form.get('meta_description', ''), 'seo')
        set_setting('meta_keywords', request.form.get('meta_keywords', ''), 'seo')
        set_setting('og_title', request.form.get('og_title', ''), 'seo')
        set_setting('og_description', request.form.get('og_description', ''), 'seo')
        set_setting('og_image', request.form.get('og_image', ''), 'seo')
        set_setting('google_analytics', request.form.get('google_analytics', ''), 'seo')
        set_setting('robots_txt', request.form.get('robots_txt', ''), 'seo')
        
        flash('Paramètres SEO enregistrés', 'success')
        return redirect(url_for('superadmin.seo'))
    
    settings = {
        'meta_title': get_setting('meta_title', ''),
        'meta_description': get_setting('meta_description', ''),
        'meta_keywords': get_setting('meta_keywords', ''),
        'og_title': get_setting('og_title', ''),
        'og_description': get_setting('og_description', ''),
        'og_image': get_setting('og_image', ''),
        'google_analytics': get_setting('google_analytics', ''),
        'robots_txt': get_setting('robots_txt', '')
    }
    
    return render_template('superadmin/seo.html', settings=settings)
