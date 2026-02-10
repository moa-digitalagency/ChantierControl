from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Ouvrier, Pointage, Chantier, User
from security import login_required, get_current_user, direction_required
from datetime import datetime, date
from utils.export import export_to_excel
import pandas as pd

main_oeuvre_bp = Blueprint('main_oeuvre', __name__, url_prefix='/main_oeuvre')

@main_oeuvre_bp.route('/')
@login_required
def index():
    user = get_current_user()
    if not user.entreprise_id:
        flash("Erreur: Utilisateur sans entreprise.", "danger")
        return redirect(url_for('dashboard.index'))

    ouvriers = Ouvrier.query.filter_by(entreprise_id=user.entreprise_id, actif=True).all()
    return render_template('main_oeuvre/index.html', ouvriers=ouvriers)

@main_oeuvre_bp.route('/nouveau', methods=['GET', 'POST'])
@direction_required
def nouveau():
    user = get_current_user()

    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        telephone = request.form.get('telephone')
        poste = request.form.get('poste')
        try:
            taux_horaire = float(request.form.get('taux_horaire', 0))
        except ValueError:
            taux_horaire = 0.0

        if not nom or not prenom:
            flash('Nom et Prénom sont obligatoires', 'danger')
            return render_template('main_oeuvre/nouveau.html')

        ouvrier = Ouvrier(
            entreprise_id=user.entreprise_id,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            poste=poste,
            taux_horaire=taux_horaire
        )
        db.session.add(ouvrier)
        db.session.commit()

        flash('Ouvrier ajouté avec succès', 'success')
        return redirect(url_for('main_oeuvre.index'))

    return render_template('main_oeuvre/nouveau.html')

@main_oeuvre_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@direction_required
def modifier(id):
    user = get_current_user()
    ouvrier = Ouvrier.query.filter_by(id=id, entreprise_id=user.entreprise_id).first_or_404()

    if request.method == 'POST':
        ouvrier.nom = request.form.get('nom')
        ouvrier.prenom = request.form.get('prenom')
        ouvrier.telephone = request.form.get('telephone')
        ouvrier.poste = request.form.get('poste')
        try:
            ouvrier.taux_horaire = float(request.form.get('taux_horaire', 0))
        except ValueError:
            pass # Keep old value or handle error

        db.session.commit()
        flash('Ouvrier modifié avec succès', 'success')
        return redirect(url_for('main_oeuvre.index'))

    return render_template('main_oeuvre/modifier.html', ouvrier=ouvrier)

@main_oeuvre_bp.route('/<int:id>/supprimer', methods=['POST'])
@direction_required
def supprimer(id):
    user = get_current_user()
    ouvrier = Ouvrier.query.filter_by(id=id, entreprise_id=user.entreprise_id).first_or_404()

    ouvrier.actif = False
    db.session.commit()
    flash('Ouvrier supprimé', 'success')
    return redirect(url_for('main_oeuvre.index'))

@main_oeuvre_bp.route('/pointage', methods=['GET', 'POST'])
@login_required
def pointage():
    user = get_current_user()

    # Get available chantiers
    if user.role in ['admin', 'direction']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id, statut='en_cours').all()
    else:
        # Chef chantier see their assignments
        # user.assignments is lazy='dynamic', so it's a query
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments if a.chantier.statut == 'en_cours']

    selected_chantier_id = request.args.get('chantier_id', type=int)
    selected_date_str = request.args.get('date', date.today().isoformat())
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = date.today()

    ouvriers = []
    existing_pointages = {}

    if selected_chantier_id:
        # Verify access
        chantier = Chantier.query.get(selected_chantier_id)
        if not chantier or (chantier.entreprise_id != user.entreprise_id):
            flash("Accès non autorisé", "danger")
            return redirect(url_for('dashboard.index'))

        ouvriers = Ouvrier.query.filter_by(entreprise_id=user.entreprise_id, actif=True).all()

        # Load existing pointages for this date/chantier
        pointages_query = Pointage.query.filter_by(
            chantier_id=selected_chantier_id,
            date_pointage=selected_date
        ).all()

        for p in pointages_query:
            existing_pointages[p.ouvrier_id] = p

    if request.method == 'POST':
        if not selected_chantier_id:
            flash("Veuillez sélectionner un chantier", "warning")
            return redirect(url_for('main_oeuvre.pointage'))

        # Process form data
        # Form data format: hours_{ouvrier_id}
        for ouvrier in ouvriers:
            hours_str = request.form.get(f'hours_{ouvrier.id}')
            try:
                hours = float(hours_str) if hours_str else 0.0
            except ValueError:
                hours = 0.0

            if hours > 0:
                # Calculate amount
                montant = hours * ouvrier.taux_horaire

                # Update or Create
                p = existing_pointages.get(ouvrier.id)
                if p:
                    p.heures = hours
                    p.montant = montant
                    p.user_id = user.id # Update who modified it
                else:
                    p = Pointage(
                        ouvrier_id=ouvrier.id,
                        chantier_id=selected_chantier_id,
                        user_id=user.id,
                        date_pointage=selected_date,
                        heures=hours,
                        montant=montant,
                        valide=False
                    )
                    db.session.add(p)
            else:
                # If hours 0 and pointage exists, maybe delete or set to 0?
                # Let's set to 0
                p = existing_pointages.get(ouvrier.id)
                if p:
                    p.heures = 0
                    p.montant = 0

        db.session.commit()
        flash("Pointage enregistré", "success")
        return redirect(url_for('main_oeuvre.pointage', chantier_id=selected_chantier_id, date=selected_date_str))

    return render_template('main_oeuvre/pointage.html',
                           chantiers=chantiers,
                           ouvriers=ouvriers,
                           selected_chantier_id=selected_chantier_id,
                           selected_date=selected_date_str,
                           existing_pointages=existing_pointages)

@main_oeuvre_bp.route('/export')
@login_required
def export():
    user = get_current_user()
    ouvriers = Ouvrier.query.filter_by(entreprise_id=user.entreprise_id, actif=True).all()

    data = []
    for o in ouvriers:
        data.append({
            'Nom': o.nom,
            'Prénom': o.prenom,
            'Téléphone': o.telephone,
            'Poste': o.poste,
            'Taux Horaire': o.taux_horaire
        })

    return export_to_excel(data, filename=f"ouvriers_{date.today()}.xlsx")

@main_oeuvre_bp.route('/import_template')
@login_required
def download_template():
    data = [{'Nom': '', 'Prénom': '', 'Téléphone': '', 'Poste': '', 'Taux Horaire': ''}]
    return export_to_excel(data, filename="modele_import_ouvriers.xlsx")

@main_oeuvre_bp.route('/import', methods=['POST'])
@direction_required
def import_ouvriers():
    user = get_current_user()
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('main_oeuvre.index'))

    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('main_oeuvre.index'))

    if file:
        try:
            df = pd.read_excel(file)
            count = 0
            for index, row in df.iterrows():
                nom = str(row.get('Nom', '')).strip()
                prenom = str(row.get('Prénom', '')).strip()

                # Basic validation
                if not nom or nom.lower() == 'nan': continue
                if not prenom or prenom.lower() == 'nan': continue

                # Check existence
                exists = Ouvrier.query.filter_by(entreprise_id=user.entreprise_id, nom=nom, prenom=prenom).first()
                if not exists:
                    try:
                        rate = float(row.get('Taux Horaire', 0))
                    except:
                        rate = 0.0

                    ouvrier = Ouvrier(
                        entreprise_id=user.entreprise_id,
                        nom=nom,
                        prenom=prenom,
                        telephone=str(row.get('Téléphone', '') if pd.notna(row.get('Téléphone')) else ''),
                        poste=str(row.get('Poste', '') if pd.notna(row.get('Poste')) else ''),
                        taux_horaire=rate
                    )
                    db.session.add(ouvrier)
                    count += 1

            db.session.commit()
            if count > 0:
                flash(f'{count} ouvriers importés avec succès', 'success')
            else:
                flash('Aucun nouvel ouvrier n\'a été importé (doublons ou données invalides)', 'warning')
        except Exception as e:
            flash(f'Erreur lors de l\'importation: {str(e)}', 'danger')
            print(e)

    return redirect(url_for('main_oeuvre.index'))
