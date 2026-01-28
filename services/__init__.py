from models import db, Chantier, ChantierAssignment, Achat, Avance, Heure, Alerte
from algorithms import calculer_kpi_chantier, verifier_alertes
from services.pdf_service import generate_chantier_report
from services.notification_service import notify_direction

def process_alerts(chantier_id):
    """
    Checks for alerts, saves them to DB if new, and sends notifications.
    """
    # Import inside to avoid circular deps if any, though verify_alertes is in algorithms
    generated_alerts = verifier_alertes(chantier_id)
    chantier = db.session.get(Chantier, chantier_id)

    if not generated_alerts:
        return

    for alert_data in generated_alerts:
        # Check if active (unread) alert of same type exists for this chantier
        existing = Alerte.query.filter_by(
            chantier_id=chantier_id,
            type_alerte=alert_data['type'],
            lu=False
        ).first()

        if not existing:
            # Create new alert
            new_alert = Alerte(
                chantier_id=chantier_id,
                type_alerte=alert_data['type'],
                message=alert_data['message'],
                niveau=alert_data['niveau']
            )
            db.session.add(new_alert)

            # Send notification
            subject = f"Alerte Chantier: {chantier.nom}"
            notify_direction(subject, alert_data['message'])

    db.session.commit()

def get_chantiers_utilisateur(user_id, role, entreprise_id=None):
    if role == 'direction':
        query = Chantier.query.filter_by(statut='en_cours')
        if entreprise_id:
            query = query.filter_by(entreprise_id=entreprise_id)
        return query.all()
    
    assignments = ChantierAssignment.query.filter_by(
        user_id=user_id,
        actif=True
    ).all()
    
    chantier_ids = [a.chantier_id for a in assignments]
    return Chantier.query.filter(
        Chantier.id.in_(chantier_ids),
        Chantier.statut == 'en_cours'
    ).all()

def get_dashboard_direction(entreprise_id=None):
    query = Chantier.query.filter_by(statut='en_cours')
    if entreprise_id:
        query = query.filter_by(entreprise_id=entreprise_id)
    chantiers = query.all()
    
    dashboard_data = []
    for chantier in chantiers:
        kpi = calculer_kpi_chantier(chantier.id)
        alertes = verifier_alertes(chantier.id, kpi=kpi)
        
        dashboard_data.append({
            'chantier': chantier,
            'kpi': kpi,
            'alertes': alertes,
            'nb_alertes': len(alertes)
        })
    
    return dashboard_data

def get_saisies_en_attente(entreprise_id=None):
    achats_query = Achat.query.filter_by(statut='en_attente')
    avances_query = Avance.query.filter_by(statut='en_attente')
    heures_query = Heure.query.filter_by(statut='en_attente')
    
    if entreprise_id:
        achats_query = achats_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
        avances_query = avances_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
        heures_query = heures_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
    
    achats = achats_query.order_by(Achat.created_at.desc()).all()
    avances = avances_query.order_by(Avance.created_at.desc()).all()
    heures = heures_query.order_by(Heure.created_at.desc()).all()
    
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

def get_tresorerie_par_chef(entreprise_id=None):
    from sqlalchemy import func
    
    query = db.session.query(
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
    )
    
    if entreprise_id:
        query = query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
    
    result = query.group_by(ChantierAssignment.user_id).all()
    
    return result
