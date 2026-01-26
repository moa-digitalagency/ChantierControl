from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Achat, Avance, Heure
from security import direction_required, get_current_user
from datetime import datetime

validation_bp = Blueprint('validation', __name__, url_prefix='/validation')

@validation_bp.route('/')
@direction_required
def liste():
    achats = Achat.query.filter_by(statut='en_attente').order_by(Achat.created_at.desc()).all()
    avances = Avance.query.filter_by(statut='en_attente').order_by(Avance.created_at.desc()).all()
    heures = Heure.query.filter_by(statut='en_attente').order_by(Heure.created_at.desc()).all()
    
    return render_template('validation/liste.html',
                         achats=achats,
                         avances=avances,
                         heures=heures)

@validation_bp.route('/achat/<int:id>/<action>', methods=['POST'])
@direction_required
def valider_achat(id, action):
    user = get_current_user()
    achat = db.session.get(Achat, id)
    
    if not achat:
        flash('Achat non trouvé', 'danger')
        return redirect(url_for('validation.liste'))
    
    commentaire = request.form.get('commentaire', '')
    
    if action == 'valider':
        achat.statut = 'valide'
        flash('Achat validé', 'success')
    elif action == 'refuser':
        achat.statut = 'refuse'
        flash('Achat refusé', 'warning')
    
    achat.commentaire_validation = commentaire
    achat.valide_par_id = user.id
    achat.date_validation = datetime.utcnow()
    
    db.session.commit()
    return redirect(url_for('validation.liste'))

@validation_bp.route('/avance/<int:id>/<action>', methods=['POST'])
@direction_required
def valider_avance(id, action):
    user = get_current_user()
    avance = db.session.get(Avance, id)
    
    if not avance:
        flash('Avance non trouvée', 'danger')
        return redirect(url_for('validation.liste'))
    
    commentaire = request.form.get('commentaire', '')
    
    if action == 'valider':
        avance.statut = 'valide'
        flash('Avance validée', 'success')
    elif action == 'refuser':
        avance.statut = 'refuse'
        flash('Avance refusée', 'warning')
    
    avance.commentaire_validation = commentaire
    avance.valide_par_id = user.id
    avance.date_validation = datetime.utcnow()
    
    db.session.commit()
    return redirect(url_for('validation.liste'))

@validation_bp.route('/heure/<int:id>/<action>', methods=['POST'])
@direction_required
def valider_heure(id, action):
    user = get_current_user()
    heure = db.session.get(Heure, id)
    
    if not heure:
        flash('Heures non trouvées', 'danger')
        return redirect(url_for('validation.liste'))
    
    commentaire = request.form.get('commentaire', '')
    
    if action == 'valider':
        heure.statut = 'valide'
        flash('Heures validées', 'success')
    elif action == 'refuser':
        heure.statut = 'refuse'
        flash('Heures refusées', 'warning')
    
    heure.commentaire_validation = commentaire
    heure.valide_par_id = user.id
    heure.date_validation = datetime.utcnow()
    
    db.session.commit()
    return redirect(url_for('validation.liste'))
