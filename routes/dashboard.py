from flask import Blueprint, render_template, session, redirect, url_for
from security import login_required, get_current_user
from services import get_chantiers_utilisateur, get_dashboard_direction, get_saisies_en_attente
from algorithms import verifier_saisies_en_attente

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user = get_current_user()
    role = session.get('user_role')
    
    if role == 'super_admin':
        return redirect(url_for('superadmin.index'))
    
    if role == 'admin':
        return redirect(url_for('admin.index'))
    
    if role == 'direction':
        dashboard_data = get_dashboard_direction(user.entreprise_id)
        saisies = get_saisies_en_attente(user.entreprise_id)
        alerte_saisies = verifier_saisies_en_attente(user.entreprise_id)
        
        return render_template('dashboard/direction.html',
                             dashboard_data=dashboard_data,
                             saisies=saisies,
                             alerte_saisies=alerte_saisies,
                             user=user)
    else:
        chantiers = get_chantiers_utilisateur(user.id, role)
        return render_template('dashboard/chef.html',
                             chantiers=chantiers,
                             user=user)
