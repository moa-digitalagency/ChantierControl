from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Achat, Avance, Heure, ChantierAssignment
from security import login_required, get_current_user
from utils import save_photo
from datetime import date

saisies_bp = Blueprint('saisies', __name__, url_prefix='/saisies')

def get_user_chantiers(user_id, role):
    if role == 'direction':
        from models import Chantier
        return Chantier.query.filter_by(statut='en_cours').all()
    
    assignments = ChantierAssignment.query.filter_by(
        user_id=user_id, actif=True
    ).all()
    return [a.chantier for a in assignments]

def user_has_access_to_chantier(user_id, role, chantier_id):
    if role == 'direction':
        return True
    
    assignment = ChantierAssignment.query.filter_by(
        user_id=user_id,
        chantier_id=chantier_id,
        actif=True
    ).first()
    return assignment is not None

@saisies_bp.route('/achat', methods=['GET', 'POST'])
@login_required
def nouvel_achat():
    user = get_current_user()
    role = session.get('user_role')
    chantiers = get_user_chantiers(user.id, role)
    
    if request.method == 'POST':
        chantier_id = request.form.get('chantier_id')
        
        if not user_has_access_to_chantier(user.id, role, chantier_id):
            flash('Accès non autorisé à ce chantier', 'danger')
            return redirect(url_for('dashboard.index'))
        
        try:
            montant = float(request.form.get('montant', 0))
        except ValueError:
            flash('Montant invalide', 'danger')
            return render_template('saisies/achat.html', chantiers=chantiers)
        
        date_achat = request.form.get('date_achat')
        fournisseur = request.form.get('fournisseur')
        description = request.form.get('description')
        categorie = request.form.get('categorie', 'achats')
        
        if not fournisseur or not date_achat:
            flash('Veuillez remplir tous les champs obligatoires', 'danger')
            return render_template('saisies/achat.html', chantiers=chantiers)
        
        photo = request.files.get('photo')
        photo_filename = None
        
        if montant > 500 and (not photo or not photo.filename):
            flash('Photo justificative obligatoire pour les montants > 500 MAD', 'danger')
            return render_template('saisies/achat.html', chantiers=chantiers)
        
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if not photo_filename:
                flash('Format de fichier non autorisé. Utilisez JPG, PNG ou GIF', 'danger')
                return render_template('saisies/achat.html', chantiers=chantiers)
        
        achat = Achat(
            chantier_id=chantier_id,
            user_id=user.id,
            montant=montant,
            date_achat=date.fromisoformat(date_achat),
            fournisseur=fournisseur,
            description=description,
            categorie=categorie,
            photo_justificatif=photo_filename,
            statut='en_attente'
        )
        
        db.session.add(achat)
        db.session.commit()
        
        flash('Achat enregistré - En attente de validation', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('saisies/achat.html', chantiers=chantiers)

@saisies_bp.route('/avance', methods=['GET', 'POST'])
@login_required
def nouvelle_avance():
    user = get_current_user()
    role = session.get('user_role')
    
    if role == 'responsable_achats':
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('dashboard.index'))
    
    chantiers = get_user_chantiers(user.id, role)
    
    if request.method == 'POST':
        chantier_id = request.form.get('chantier_id')
        
        if not user_has_access_to_chantier(user.id, role, chantier_id):
            flash('Accès non autorisé à ce chantier', 'danger')
            return redirect(url_for('dashboard.index'))
        
        try:
            montant = float(request.form.get('montant', 0))
        except ValueError:
            flash('Montant invalide', 'danger')
            return render_template('saisies/avance.html', chantiers=chantiers)
        
        date_avance = request.form.get('date_avance')
        description = request.form.get('description')
        
        if not date_avance:
            flash('Veuillez remplir tous les champs obligatoires', 'danger')
            return render_template('saisies/avance.html', chantiers=chantiers)
        
        photo = request.files.get('photo')
        photo_filename = None
        
        if montant > 500 and (not photo or not photo.filename):
            flash('Photo justificative obligatoire pour les montants > 500 MAD', 'danger')
            return render_template('saisies/avance.html', chantiers=chantiers)
        
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if not photo_filename:
                flash('Format de fichier non autorisé. Utilisez JPG, PNG ou GIF', 'danger')
                return render_template('saisies/avance.html', chantiers=chantiers)
        
        avance = Avance(
            chantier_id=chantier_id,
            user_id=user.id,
            montant=montant,
            date_avance=date.fromisoformat(date_avance),
            description=description,
            photo_justificatif=photo_filename,
            statut='en_attente'
        )
        
        db.session.add(avance)
        db.session.commit()
        
        flash('Avance enregistrée - En attente de validation', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('saisies/avance.html', chantiers=chantiers)

@saisies_bp.route('/heure', methods=['GET', 'POST'])
@login_required
def nouvelle_heure():
    user = get_current_user()
    role = session.get('user_role')
    chantiers = get_user_chantiers(user.id, role)
    
    if request.method == 'POST':
        chantier_id = request.form.get('chantier_id')
        
        if not user_has_access_to_chantier(user.id, role, chantier_id):
            flash('Accès non autorisé à ce chantier', 'danger')
            return redirect(url_for('dashboard.index'))
        
        try:
            quantite = float(request.form.get('quantite', 0))
            tarif_unitaire = float(request.form.get('tarif_unitaire', 0))
        except ValueError:
            flash('Valeurs numériques invalides', 'danger')
            return render_template('saisies/heure.html', chantiers=chantiers)
        
        date_travail = request.form.get('date_travail')
        description = request.form.get('description')
        type_travail = request.form.get('type_travail', 'main_oeuvre')
        
        if not date_travail or quantite <= 0 or tarif_unitaire <= 0:
            flash('Veuillez remplir tous les champs obligatoires avec des valeurs valides', 'danger')
            return render_template('saisies/heure.html', chantiers=chantiers)
        
        cout_total = quantite * tarif_unitaire
        
        heure = Heure(
            chantier_id=chantier_id,
            user_id=user.id,
            quantite=quantite,
            tarif_unitaire=tarif_unitaire,
            cout_total=cout_total,
            date_travail=date.fromisoformat(date_travail),
            description=description,
            type_travail=type_travail,
            statut='en_attente'
        )
        
        db.session.add(heure)
        db.session.commit()
        
        flash('Heures enregistrées - En attente de validation', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('saisies/heure.html', chantiers=chantiers)
