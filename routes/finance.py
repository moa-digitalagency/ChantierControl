from flask import Blueprint, render_template
from security import direction_required, get_current_user
from models import Chantier, Achat, Heure, Avance
from sqlalchemy import func

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@direction_required
def index():
    current_user = get_current_user()

    # Fetch all chantiers for the enterprise
    chantiers = Chantier.query.filter_by(entreprise_id=current_user.entreprise_id).all()

    financial_data = []

    total_budget = 0
    total_depenses = 0
    total_heures = 0
    total_avances = 0

    for chantier in chantiers:
        # Calculate totals per chantier

        # Achats (Expenses)
        depenses = sum(a.montant for a in chantier.achats)

        # Heures (Labor Cost)
        cout_heures = sum(h.cout_total for h in chantier.heures)

        # Avances (Advances)
        avances = sum(a.montant for a in chantier.avances)

        budget = chantier.budget_previsionnel or 0
        total_spent = depenses + cout_heures # Avances might be considered cash flow, not expense, or included. Usually specific request. Assuming Expense + Labor = Cost.
        reste = budget - total_spent

        financial_data.append({
            'chantier': chantier,
            'budget': budget,
            'depenses': depenses,
            'heures': cout_heures,
            'avances': avances,
            'total_spent': total_spent,
            'reste': reste,
            'consommation_pct': (total_spent / budget * 100) if budget > 0 else 0
        })

        total_budget += budget
        total_depenses += depenses
        total_heures += cout_heures
        total_avances += avances

    global_stats = {
        'budget': total_budget,
        'spent': total_depenses + total_heures,
        'avances': total_avances,
        'reste': total_budget - (total_depenses + total_heures)
    }

    return render_template('finance/index.html', data=financial_data, global_stats=global_stats)
