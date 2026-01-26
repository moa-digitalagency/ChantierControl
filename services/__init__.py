from models import db, Chantier, ChantierAssignment, Achat, Avance, Heure
from algorithms import calculer_kpi_chantier, verifier_alertes

def get_chantiers_utilisateur(user_id, role):
    if role == 'direction':
        return Chantier.query.filter_by(statut='en_cours').all()
    
    assignments = ChantierAssignment.query.filter_by(
        user_id=user_id,
        actif=True
    ).all()
    
    chantier_ids = [a.chantier_id for a in assignments]
    return Chantier.query.filter(
        Chantier.id.in_(chantier_ids),
        Chantier.statut == 'en_cours'
    ).all()

def get_dashboard_direction():
    chantiers = Chantier.query.filter_by(statut='en_cours').all()
    
    dashboard_data = []
    for chantier in chantiers:
        kpi = calculer_kpi_chantier(chantier.id)
        alertes = verifier_alertes(chantier.id)
        
        dashboard_data.append({
            'chantier': chantier,
            'kpi': kpi,
            'alertes': alertes,
            'nb_alertes': len(alertes)
        })
    
    return dashboard_data

def get_saisies_en_attente():
    achats = Achat.query.filter_by(statut='en_attente').order_by(Achat.created_at.desc()).all()
    avances = Avance.query.filter_by(statut='en_attente').order_by(Avance.created_at.desc()).all()
    heures = Heure.query.filter_by(statut='en_attente').order_by(Heure.created_at.desc()).all()
    
    return {
        'achats': achats,
        'avances': avances,
        'heures': heures,
        'total': len(achats) + len(avances) + len(heures)
    }

def get_derniers_achats(chantier_id, limit=5):
    return Achat.query.filter_by(
        chantier_id=chantier_id,
        statut='valide'
    ).order_by(Achat.date_achat.desc()).limit(limit).all()

def get_tresorerie_par_chef():
    from sqlalchemy import func
    
    result = db.session.query(
        ChantierAssignment.user_id,
        func.sum(Avance.montant).label('total_avances'),
        func.sum(Achat.montant).label('total_depenses')
    ).outerjoin(
        Avance, Avance.chantier_id == ChantierAssignment.chantier_id
    ).outerjoin(
        Achat, Achat.chantier_id == ChantierAssignment.chantier_id
    ).filter(
        Avance.statut == 'valide',
        Achat.statut == 'valide'
    ).group_by(ChantierAssignment.user_id).all()
    
    return result
