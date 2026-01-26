from flask import Blueprint, render_template, session
from security import login_required, get_current_user
from services import get_chantiers_utilisateur, get_dashboard_direction, get_saisies_en_attente
from algorithms import verifier_saisies_en_attente

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user = get_current_user()
    role = session.get('user_role')
    
    if role == 'direction':
        dashboard_data = get_dashboard_direction()
        saisies = get_saisies_en_attente()
        alerte_saisies = verifier_saisies_en_attente()
        
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
