from flask import Blueprint, render_template, flash, redirect, url_for
from security import direction_required, get_current_user
from models import Chantier, Achat, Heure, Avance, Pointage, db
from sqlalchemy import func
from utils.export import export_to_excel
from datetime import date

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
    total_pointages = 0
    total_avances = 0

    for chantier in chantiers:
        # Calculate totals per chantier

        # Achats (Expenses) - optimize with scalar query if needed, but keeping consistent style for now
        # Using db.session.query for performance
        depenses = db.session.query(func.sum(Achat.montant)).filter_by(chantier_id=chantier.id).scalar() or 0

        # Heures (Legacy Labor Cost)
        cout_heures = db.session.query(func.sum(Heure.cout_total)).filter_by(chantier_id=chantier.id).scalar() or 0

        # Pointages (New Labor Cost)
        cout_pointages = db.session.query(func.sum(Pointage.montant)).filter_by(chantier_id=chantier.id).scalar() or 0

        # Avances (Advances)
        avances = db.session.query(func.sum(Avance.montant)).filter_by(chantier_id=chantier.id).scalar() or 0

        budget = chantier.budget_previsionnel or 0

        # Total Spent = Expenses + Labor (Legacy + New)
        total_spent = depenses + cout_heures + cout_pointages

        reste = budget - total_spent

        financial_data.append({
            'chantier': chantier,
            'budget': budget,
            'depenses': depenses,
            'heures': cout_heures + cout_pointages, # Combine for display
            'avances': avances,
            'total_spent': total_spent,
            'reste': reste,
            'consommation_pct': (total_spent / budget * 100) if budget > 0 else 0
        })

        total_budget += budget
        total_depenses += depenses
        total_heures += (cout_heures + cout_pointages)
        total_avances += avances

    global_stats = {
        'budget': total_budget,
        'spent': total_depenses + total_heures, # total_heures already includes pointages
        'avances': total_avances,
        'reste': total_budget - (total_depenses + total_heures)
    }

    return render_template('finance/index.html', data=financial_data, global_stats=global_stats)

@finance_bp.route('/details/<int:chantier_id>')
@direction_required
def details(chantier_id):
    current_user = get_current_user()
    chantier = Chantier.query.get_or_404(chantier_id)

    if chantier.entreprise_id != current_user.entreprise_id:
        flash("Accès non autorisé", "danger")
        return redirect(url_for('finance.index'))

    # Achats (Expenses)
    achats = chantier.achats.order_by(Achat.date_achat.desc()).all()

    # Group by category
    achats_by_category = {}
    total_depenses = 0
    for a in achats:
        cat = a.categorie or 'Autre'
        if cat not in achats_by_category:
            achats_by_category[cat] = 0
        achats_by_category[cat] += a.montant
        total_depenses += a.montant

    # Pointages (Labor)
    pointages = chantier.pointages.order_by(Pointage.date_pointage.desc()).all()
    cout_pointages = sum(p.montant for p in pointages)

    # Legacy Heures
    heures = chantier.heures.all()
    cout_heures = sum(h.cout_total for h in heures)

    total_main_oeuvre = cout_pointages + cout_heures
    total_general = total_depenses + total_main_oeuvre

    budget = chantier.budget_previsionnel or 0
    reste = budget - total_general
    consommation_pct = (total_general / budget * 100) if budget > 0 else 0

    return render_template('finance/details.html',
                           chantier=chantier,
                           achats=achats,
                           pointages=pointages,
                           achats_by_category=achats_by_category,
                           total_depenses=total_depenses,
                           total_main_oeuvre=total_main_oeuvre,
                           total_general=total_general,
                           budget=budget,
                           reste=reste,
                           consommation_pct=consommation_pct)

@finance_bp.route('/details/<int:chantier_id>/export_achats')
@direction_required
def export_achats(chantier_id):
    current_user = get_current_user()
    chantier = Chantier.query.get_or_404(chantier_id)
    if chantier.entreprise_id != current_user.entreprise_id:
        return redirect(url_for('finance.index'))

    achats = chantier.achats.order_by(Achat.date_achat.desc()).all()
    data = []
    for a in achats:
        data.append({
            'Date': a.date_achat,
            'Fournisseur': a.fournisseur,
            'Catégorie': a.categorie,
            'Description': a.description,
            'Montant': a.montant,
            'Validé par': a.valide_par.nom if a.valide_par else ''
        })

    return export_to_excel(data, filename=f"achats_{chantier.nom}_{date.today()}.xlsx")
