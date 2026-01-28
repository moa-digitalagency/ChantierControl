from models import db, Chantier, Achat, Avance, Heure, Alerte
from datetime import datetime, timedelta
from sqlalchemy import func

def calculer_kpi_chantier(chantier_id):
    chantier = db.session.get(Chantier, chantier_id)
    if not chantier:
        return None
    
    total_achats = db.session.query(func.sum(Achat.montant)).filter_by(
        chantier_id=chantier_id, 
        statut='valide'
    ).scalar() or 0
    
    total_salaires = db.session.query(func.sum(Heure.cout_total)).filter_by(
        chantier_id=chantier_id,
        statut='valide'
    ).scalar() or 0
    
    total_avances = db.session.query(func.sum(Avance.montant)).filter_by(
        chantier_id=chantier_id,
        statut='valide'
    ).scalar() or 0
    
    transport = db.session.query(func.sum(Achat.montant)).filter_by(
        chantier_id=chantier_id,
        statut='valide',
        categorie='transport'
    ).scalar() or 0
    
    cout_total = total_achats + total_salaires
    budget = chantier.budget_previsionnel or 1
    
    taux_consommation = (cout_total / budget) * 100 if budget > 0 else 0
    ecart_budgetaire = budget - cout_total
    ipc = budget / cout_total if cout_total > 0 else 1
    solde_avance = total_avances - cout_total
    
    return {
        'chantier': chantier,
        'total_achats': total_achats,
        'total_salaires': total_salaires,
        'total_transport': transport,
        'total_avances': total_avances,
        'cout_total': cout_total,
        'budget': budget,
        'taux_consommation': taux_consommation,
        'ecart_budgetaire': ecart_budgetaire,
        'ipc': ipc,
        'solde_avance': solde_avance,
        'cout_revient': cout_total
    }

def verifier_alertes(chantier_id, kpi=None):
    if kpi is None:
        kpi = calculer_kpi_chantier(chantier_id)
    if not kpi:
        return []
    
    alertes = []
    
    if kpi['solde_avance'] < 10000:
        alertes.append({
            'type': 'solde_bas',
            'message': f"Solde avance bas: {kpi['solde_avance']:.2f} MAD",
            'niveau': 'danger'
        })
    
    if kpi['ecart_budgetaire'] < 0 and abs(kpi['ecart_budgetaire']) > kpi['budget'] * 0.05:
        alertes.append({
            'type': 'depassement_budget',
            'message': f"Dépassement budget > 5%: {kpi['ecart_budgetaire']:.2f} MAD",
            'niveau': 'danger'
        })
    
    if kpi['taux_consommation'] > 80:
        alertes.append({
            'type': 'consommation_elevee',
            'message': f"Consommation budget > 80%: {kpi['taux_consommation']:.1f}%",
            'niveau': 'warning'
        })
    
    return alertes

def verifier_saisies_en_attente(entreprise_id=None):
    seuil = datetime.utcnow() - timedelta(hours=24)
    
    achats_query = Achat.query.filter(
        Achat.statut == 'en_attente',
        Achat.created_at < seuil
    )
    avances_query = Avance.query.filter(
        Avance.statut == 'en_attente',
        Avance.created_at < seuil
    )
    heures_query = Heure.query.filter(
        Heure.statut == 'en_attente',
        Heure.created_at < seuil
    )
    
    if entreprise_id:
        achats_query = achats_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
        avances_query = avances_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
        heures_query = heures_query.join(Chantier).filter(Chantier.entreprise_id == entreprise_id)
    
    achats_anciens = achats_query.count()
    avances_anciennes = avances_query.count()
    heures_anciennes = heures_query.count()
    
    total = achats_anciens + avances_anciennes + heures_anciennes
    
    if total > 0:
        return {
            'type': 'saisies_en_attente',
            'message': f"{total} saisies en attente depuis plus de 24h",
            'niveau': 'warning'
        }
    return None
