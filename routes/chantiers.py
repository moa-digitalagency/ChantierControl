from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import db, Chantier, ChantierAssignment, User
from security import login_required, direction_required, get_current_user
from algorithms import calculer_kpi_chantier, verifier_alertes
from services import get_derniers_achats, generate_chantier_report

chantiers_bp = Blueprint('chantiers', __name__, url_prefix='/chantiers')

@chantiers_bp.route('/')
@login_required
def liste():
    user = get_current_user()
    role = session.get('user_role')
    
    if role == 'direction':
        chantiers = Chantier.query.all()
    else:
        assignments = ChantierAssignment.query.filter_by(
            user_id=user.id, actif=True
        ).all()
        chantier_ids = [a.chantier_id for a in assignments]
        chantiers = Chantier.query.filter(Chantier.id.in_(chantier_ids)).all()
    
    return render_template('chantiers/liste.html', chantiers=chantiers, user=user)

@chantiers_bp.route('/nouveau', methods=['GET', 'POST'])
@direction_required
def nouveau():
    if request.method == 'POST':
        nom = request.form.get('nom')
        adresse = request.form.get('adresse')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        budget = request.form.get('budget_previsionnel', 0)
        
        chantier = Chantier(
            nom=nom,
            adresse=adresse,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            budget_previsionnel=float(budget) if budget else 0
        )
        
        db.session.add(chantier)
        db.session.commit()
        
        flash('Chantier créé avec succès', 'success')
        return redirect(url_for('chantiers.detail', id=chantier.id))
    
    return render_template('chantiers/nouveau.html')

@chantiers_bp.route('/<int:id>')
@login_required
def detail(id):
    user = get_current_user()
    role = session.get('user_role')
    
    chantier = db.session.get(Chantier, id)
    if not chantier:
        flash('Chantier non trouvé', 'danger')
        return redirect(url_for('chantiers.liste'))
    
    if role != 'direction':
        assignment = ChantierAssignment.query.filter_by(
            user_id=user.id, chantier_id=id, actif=True
        ).first()
        if not assignment:
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('dashboard.index'))
    
    kpi = calculer_kpi_chantier(id)
    alertes = verifier_alertes(id)
    derniers_achats = get_derniers_achats(id)
    
    users_assignes = ChantierAssignment.query.filter_by(
        chantier_id=id, actif=True
    ).all()
    
    return render_template('chantiers/detail.html',
                         chantier=chantier,
                         kpi=kpi,
                         alertes=alertes,
                         derniers_achats=derniers_achats,
                         users_assignes=users_assignes,
                         user=user,
                         role=role)

@chantiers_bp.route('/<int:id>/assigner', methods=['GET', 'POST'])
@direction_required
def assigner(id):
    chantier = db.session.get(Chantier, id)
    if not chantier:
        flash('Chantier non trouvé', 'danger')
        return redirect(url_for('chantiers.liste'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        existing = ChantierAssignment.query.filter_by(
            user_id=user_id, chantier_id=id
        ).first()
        
        if existing:
            existing.actif = True
        else:
            assignment = ChantierAssignment(
                user_id=user_id,
                chantier_id=id
            )
            db.session.add(assignment)
        
        db.session.commit()
        flash('Utilisateur assigné avec succès', 'success')
        return redirect(url_for('chantiers.detail', id=id))
    
    users = User.query.filter(User.role != 'direction', User.actif == True).all()
    
    current_assignments = ChantierAssignment.query.filter_by(
        chantier_id=id, actif=True
    ).all()
    assigned_ids = [a.user_id for a in current_assignments]
    
    return render_template('chantiers/assigner.html',
                         chantier=chantier,
                         users=users,
                         assigned_ids=assigned_ids)

@chantiers_bp.route('/<int:id>/desassigner/<int:user_id>', methods=['POST'])
@direction_required
def desassigner(id, user_id):
    assignment = ChantierAssignment.query.filter_by(
        user_id=user_id, chantier_id=id
    ).first()
    
    if assignment:
        assignment.actif = False
        db.session.commit()
        flash('Utilisateur retiré du chantier', 'success')
    
    return redirect(url_for('chantiers.detail', id=id))

@chantiers_bp.route('/<int:id>/rapport')
@login_required
def rapport(id):
    user = get_current_user()
    role = session.get('user_role')

    chantier = db.session.get(Chantier, id)
    if not chantier:
        flash('Chantier non trouvé', 'danger')
        return redirect(url_for('chantiers.liste'))

    # Check access
    if role != 'direction':
        assignment = ChantierAssignment.query.filter_by(
            user_id=user.id, chantier_id=id, actif=True
        ).first()
        if not assignment:
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('dashboard.index'))

    output_path = generate_chantier_report(id)
    if not output_path:
        flash('Erreur lors de la génération du rapport', 'danger')
        return redirect(url_for('chantiers.detail', id=id))

    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"rapport_chantier_{chantier.nom}_{id}.pdf",
        mimetype='application/pdf'
    )
