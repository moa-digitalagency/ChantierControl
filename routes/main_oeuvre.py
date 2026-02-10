from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Ouvrier, Pointage, Chantier, User
from security import login_required, get_current_user, direction_required
from datetime import datetime, date
from utils.export import export_to_excel
from utils import save_photo
import pandas as pd

main_oeuvre_bp = Blueprint('main_oeuvre', __name__, url_prefix='/main_oeuvre')

@main_oeuvre_bp.route('/')
@login_required
def index():
    user = get_current_user()
    if not user.entreprise_id:
        flash("Erreur: Utilisateur sans entreprise.", "danger")
        return redirect(url_for('dashboard.index'))

    # Filter by chantier if requested
    chantier_id = request.args.get('chantier_id', type=int)

    query = Ouvrier.query.filter_by(entreprise_id=user.entreprise_id, actif=True)

    if chantier_id:
        query = query.filter_by(chantier_id=chantier_id)

    ouvriers = query.all()

    # Get chantiers list for filter
    if user.role in ['admin', 'direction']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id, statut='en_cours').all()
    else:
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments if a.chantier.statut == 'en_cours']

    return render_template('main_oeuvre/index.html', ouvriers=ouvriers, chantiers=chantiers, selected_chantier_id=chantier_id)

@main_oeuvre_bp.route('/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau():
    # Changed from @direction_required to @login_required to allow chefs chantier (per user request context)
    # But stricter check inside:
    user = get_current_user()
    if user.role not in ['admin', 'direction', 'chef_chantier', 'super_admin']:
         flash("Accès non autorisé", "danger")
         return redirect(url_for('main_oeuvre.index'))

    # Get chantiers list
    if user.role in ['admin', 'direction', 'super_admin']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id, statut='en_cours').all()
    else:
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments if a.chantier.statut == 'en_cours']

    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        telephone = request.form.get('telephone')
        poste = request.form.get('poste')
        chantier_id = request.form.get('chantier_id')
        cni = request.form.get('cni')

        try:
            taux_horaire = float(request.form.get('taux_horaire', 0))
        except ValueError:
            taux_horaire = 0.0

        if not nom or not prenom:
            flash('Nom et Prénom sont obligatoires', 'danger')
            return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)

        # Handle Photo Upload
        photo = request.files.get('photo_cni')
        photo_filename = None
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if not photo_filename:
                flash('Format de fichier non autorisé. Utilisez JPG, PNG ou GIF', 'warning')

        # Validate chantier access
        if chantier_id:
            chantier_id = int(chantier_id)
            # Check if user has access to this chantier
            allowed_ids = [c.id for c in chantiers]
            if chantier_id not in allowed_ids:
                 flash('Accès non autorisé à ce chantier', 'danger')
                 return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)
        else:
            chantier_id = None

        ouvrier = Ouvrier(
            entreprise_id=user.entreprise_id,
            chantier_id=chantier_id,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            poste=poste,
            taux_horaire=taux_horaire,
            cni=cni,
            photo_cni=photo_filename
        )
        db.session.add(ouvrier)
        db.session.commit()

        flash('Ouvrier ajouté avec succès', 'success')
        return redirect(url_for('main_oeuvre.index'))

    return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)

@main_oeuvre_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier(id):
    user = get_current_user()
    ouvrier = Ouvrier.query.filter_by(id=id, entreprise_id=user.entreprise_id).first_or_404()

    if user.role not in ['admin', 'direction', 'super_admin']:
        # Check if chef chantier has access to this worker's chantier
        assignments = user.assignments.filter_by(actif=True).all()
        allowed_ids = [a.chantier_id for a in assignments]
        if not ouvrier.chantier_id or ouvrier.chantier_id not in allowed_ids:
             flash("Accès non autorisé", "danger")
             return redirect(url_for('main_oeuvre.index'))

    # Get chantiers list for dropdown
    if user.role in ['admin', 'direction', 'super_admin']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id, statut='en_cours').all()
    else:
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments if a.chantier.statut == 'en_cours']

    if request.method == 'POST':
        ouvrier.nom = request.form.get('nom')
        ouvrier.prenom = request.form.get('prenom')
        ouvrier.telephone = request.form.get('telephone')
        ouvrier.poste = request.form.get('poste')
        ouvrier.cni = request.form.get('cni')
        chantier_id = request.form.get('chantier_id')

        # Handle Photo Upload
        photo = request.files.get('photo_cni')
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if photo_filename:
                ouvrier.photo_cni = photo_filename
            else:
                flash('Format de fichier non autorisé', 'warning')

        if chantier_id:
             chantier_id = int(chantier_id)
             allowed_ids_c = [c.id for c in chantiers]
             if chantier_id in allowed_ids_c:
                 ouvrier.chantier_id = chantier_id
             else:
                 flash('Chantier non autorisé', 'warning')
        else:
             ouvrier.chantier_id = None

        try:
            ouvrier.taux_horaire = float(request.form.get('taux_horaire', 0))
        except ValueError:
            pass

        db.session.commit()
        flash('Ouvrier modifié avec succès', 'success')
        return redirect(url_for('main_oeuvre.index'))

    return render_template('main_oeuvre/modifier.html', ouvrier=ouvrier, chantiers=chantiers)

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

        # Only show workers assigned to this chantier OR not assigned to any (if that logic is desired, but user said "par chantier")
        # Let's strictly filter by chantier_id for the list, but maybe allow listing all if we want to add them?
        # User request: "enregistre chaque ouvrier par chantier... utiliser partout... pointage"
        # So Pointage should list only workers of that chantier.
        ouvriers = Ouvrier.query.filter_by(
            entreprise_id=user.entreprise_id,
            chantier_id=selected_chantier_id,
            actif=True
        ).all()

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
@main_oeuvre_bp.route('/salaires', methods=['GET'])
@login_required
def salaires():
    user = get_current_user()
    if not user.entreprise_id:
        return redirect(url_for('dashboard.index'))

    # Filter params
    chantier_id = request.args.get('chantier_id', type=int)
    month = request.args.get('month', date.today().strftime('%Y-%m'))

    try:
        start_date = datetime.strptime(month, '%Y-%m').date()
        # End date is start of next month - 1 day
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1)
    except ValueError:
        start_date = date.today().replace(day=1)
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1)

    # Chantiers list
    if user.role in ['admin', 'direction']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id).all()
    else:
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments]

    # Query Pointages
    query = Pointage.query.join(Ouvrier).filter(Ouvrier.entreprise_id == user.entreprise_id)

    if chantier_id:
        query = query.filter(Pointage.chantier_id == chantier_id)
    elif user.role not in ['admin', 'direction']:
        # Filter by allowed chantiers
        allowed_ids = [c.id for c in chantiers]
        query = query.filter(Pointage.chantier_id.in_(allowed_ids))

    query = query.filter(Pointage.date_pointage >= start_date, Pointage.date_pointage < end_date)

    pointages = query.all()

    # Aggregate by Worker
    salary_data = {}
    for p in pointages:
        if p.ouvrier_id not in salary_data:
            salary_data[p.ouvrier_id] = {
                'ouvrier': p.ouvrier,
                'total_heures': 0,
                'total_montant': 0,
                'jours_travailles': set()
            }

        salary_data[p.ouvrier_id]['total_heures'] += p.heures
        salary_data[p.ouvrier_id]['total_montant'] += p.montant
        salary_data[p.ouvrier_id]['jours_travailles'].add(p.date_pointage)

    # Convert set length
    for k, v in salary_data.items():
        v['jours_count'] = len(v['jours_travailles'])

    return render_template('main_oeuvre/salaires.html',
                           salary_data=salary_data,
                           chantiers=chantiers,
                           selected_chantier_id=chantier_id,
                           selected_month=month)
