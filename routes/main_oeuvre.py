from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Ouvrier, Pointage, Chantier, User
from security import login_required, get_current_user, direction_required
from datetime import datetime, date, timedelta, time
from utils.export import export_to_excel
from utils import save_photo, get_date_range
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

    # Get chantiers list for filter
    if user.role in ['admin', 'direction', 'super_admin']:
        chantiers = Chantier.query.filter_by(entreprise_id=user.entreprise_id, statut='en_cours').all()
        if chantier_id:
            query = query.filter_by(chantier_id=chantier_id)
    else:
        assignments = user.assignments.filter_by(actif=True).all()
        chantiers = [a.chantier for a in assignments if a.chantier.statut == 'en_cours']
        allowed_ids = [c.id for c in chantiers]

        if chantier_id:
            if chantier_id not in allowed_ids:
                flash("Accès non autorisé à ce chantier", "danger")
                return redirect(url_for('dashboard.index'))
            query = query.filter_by(chantier_id=chantier_id)
        else:
            if allowed_ids:
                query = query.filter(Ouvrier.chantier_id.in_(allowed_ids))
            else:
                query = query.filter(db.false()) # No assignments, no workers

    ouvriers = query.all()

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
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        nationalite = request.form.get('nationalite')

        try:
            taux_horaire = float(request.form.get('taux_horaire', 0))
        except ValueError:
            taux_horaire = 0.0

        if not nom or not prenom:
            flash('Nom et Prénom sont obligatoires', 'danger')
            return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)

        # Handle CNI Photo Upload
        photo = request.files.get('photo_cni')
        photo_filename = None
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if not photo_filename:
                flash('Format de fichier CNI non autorisé', 'warning')

        # Handle Profile Photo Upload
        photo_profil = request.files.get('photo_profil')
        photo_profil_filename = None
        if photo_profil and photo_profil.filename:
            photo_profil_filename = save_photo(photo_profil)
            if not photo_profil_filename:
                flash('Format de photo de profil non autorisé', 'warning')

        # Validate chantier access
        if chantier_id:
            chantier_id = int(chantier_id)
            # Check if user has access to this chantier
            allowed_ids = [c.id for c in chantiers]
            if chantier_id not in allowed_ids:
                 flash('Accès non autorisé à ce chantier', 'danger')
                 return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)
        else:
            # Enforce chantier selection for Chef de Chantier
            if user.role not in ['admin', 'direction', 'super_admin']:
                flash('Vous devez assigner un chantier à l\'ouvrier', 'danger')
                return render_template('main_oeuvre/nouveau.html', chantiers=chantiers)
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
            photo_cni=photo_filename,
            adresse=adresse,
            ville=ville,
            nationalite=nationalite,
            photo_profil=photo_profil_filename
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
        ouvrier.adresse = request.form.get('adresse')
        ouvrier.ville = request.form.get('ville')
        ouvrier.nationalite = request.form.get('nationalite')
        chantier_id = request.form.get('chantier_id')

        # Handle CNI Photo Upload
        photo = request.files.get('photo_cni')
        if photo and photo.filename:
            photo_filename = save_photo(photo)
            if photo_filename:
                ouvrier.photo_cni = photo_filename
            else:
                flash('Format de fichier CNI non autorisé', 'warning')

        # Handle Profile Photo Upload
        photo_p = request.files.get('photo_profil')
        if photo_p and photo_p.filename:
            photo_p_filename = save_photo(photo_p)
            if photo_p_filename:
                ouvrier.photo_profil = photo_p_filename
            else:
                flash('Format de photo de profil non autorisé', 'warning')

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

        # Security: Chef de Chantier check
        if user.role not in ['admin', 'direction', 'super_admin']:
             assignment = user.assignments.filter_by(chantier_id=selected_chantier_id, actif=True).first()
             if not assignment:
                 flash("Accès non autorisé", "danger")
                 return redirect(url_for('dashboard.index'))

        # 1. Get workers whose PRIMARY assignment is this chantier
        assigned_workers = Ouvrier.query.filter_by(
            entreprise_id=user.entreprise_id,
            chantier_id=selected_chantier_id,
            actif=True
        ).all()

        # 2. Get workers who are NOT assigned here but have a Pointage here today (visiting workers)
        # This allows the Chef to manage them once they've been added (even if added by a higher up or previous logic)
        visiting_workers = db.session.query(Ouvrier).join(Pointage).filter(
            Pointage.chantier_id == selected_chantier_id,
            Pointage.date_pointage == selected_date,
            Ouvrier.chantier_id != selected_chantier_id, # Avoid duplicates
            Ouvrier.entreprise_id == user.entreprise_id
        ).all()

        ouvriers = assigned_workers + visiting_workers

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

        def parse_time(t_str):
            if not t_str: return None
            try:
                return datetime.strptime(t_str, '%H:%M').time()
            except ValueError:
                return None

        for ouvrier in ouvriers:
            check_in_str = request.form.get(f'check_in_{ouvrier.id}')
            check_out_str = request.form.get(f'check_out_{ouvrier.id}')
            break_start_str = request.form.get(f'break_start_{ouvrier.id}')
            break_end_str = request.form.get(f'break_end_{ouvrier.id}')

            check_in = parse_time(check_in_str)
            check_out = parse_time(check_out_str)
            break_start = parse_time(break_start_str)
            break_end = parse_time(break_end_str)

            hours = 0.0
            if check_in and check_out:
                dt_in = datetime.combine(date.min, check_in)
                dt_out = datetime.combine(date.min, check_out)

                if dt_out < dt_in:
                    dt_out += timedelta(days=1)

                duration = dt_out - dt_in

                if break_start and break_end:
                    dt_break_start = datetime.combine(date.min, break_start)
                    dt_break_end = datetime.combine(date.min, break_end)
                    if dt_break_end < dt_break_start:
                         dt_break_end += timedelta(days=1)

                    break_duration = dt_break_end - dt_break_start
                    duration -= break_duration

                hours = duration.total_seconds() / 3600.0
                if hours < 0: hours = 0

            # Only create/update if there is data or existing pointage
            if hours > 0 or existing_pointages.get(ouvrier.id):
                p = existing_pointages.get(ouvrier.id)
                if not p:
                    p = Pointage(
                        ouvrier_id=ouvrier.id,
                        chantier_id=selected_chantier_id,
                        user_id=user.id,
                        date_pointage=selected_date,
                        valide=False
                    )
                    db.session.add(p)

                p.check_in = check_in
                p.check_out = check_out
                p.break_start = break_start
                p.break_end = break_end
                p.update_hours_and_amount()
                p.user_id = user.id

        db.session.commit()
        flash("Pointage enregistré", "success")
        return redirect(url_for('main_oeuvre.pointage', chantier_id=selected_chantier_id, date=selected_date_str))

    return render_template('main_oeuvre/pointage.html',
                           chantiers=chantiers,
                           ouvriers=ouvriers,
                           selected_chantier_id=selected_chantier_id,
                           selected_date=selected_date_str,
                           existing_pointages=existing_pointages)

@main_oeuvre_bp.route('/pointage/action/<int:ouvrier_id>/<action>', methods=['POST'])
@login_required
def pointage_action(ouvrier_id, action):
    user = get_current_user()
    if not user.entreprise_id:
        return jsonify({'success': False, 'message': 'Utilisateur sans entreprise'}), 403

    ouvrier = Ouvrier.query.filter_by(id=ouvrier_id, entreprise_id=user.entreprise_id).first_or_404()

    chantier_id = request.args.get('chantier_id', type=int) or ouvrier.chantier_id

    if not chantier_id:
        return jsonify({'success': False, 'message': 'Chantier non spécifié'}), 400

    # Check access to chantier
    if user.role not in ['admin', 'direction', 'super_admin']:
         assignments = user.assignments.filter_by(actif=True).all()
         allowed_ids = [a.chantier_id for a in assignments]
         if chantier_id not in allowed_ids:
             return jsonify({'success': False, 'message': 'Accès non autorisé à ce chantier'}), 403

    # Get or Create Pointage for today
    today = date.today()
    pointage = Pointage.query.filter_by(
        ouvrier_id=ouvrier.id,
        date_pointage=today
    ).first()

    if not pointage:
        pointage = Pointage(
            ouvrier_id=ouvrier.id,
            chantier_id=chantier_id,
            user_id=user.id,
            date_pointage=today,
            valide=False
        )
        db.session.add(pointage)

    now_time = datetime.now().time()
    # Round to nearest minute for cleanliness? No, user said "temps exacts".

    if action == 'arrivee':
        pointage.check_in = now_time
    elif action == 'pause':
        pointage.break_start = now_time
    elif action == 'reprise':
        pointage.break_end = now_time
    elif action == 'depart':
        pointage.check_out = now_time
    else:
        return jsonify({'success': False, 'message': 'Action inconnue'}), 400

    pointage.user_id = user.id # Update last modified user
    pointage.update_hours_and_amount()
    db.session.commit()

    return jsonify({
        'success': True,
        'check_in': pointage.check_in.strftime('%H:%M') if pointage.check_in else None,
        'check_out': pointage.check_out.strftime('%H:%M') if pointage.check_out else None,
        'break_start': pointage.break_start.strftime('%H:%M') if pointage.break_start else None,
        'break_end': pointage.break_end.strftime('%H:%M') if pointage.break_end else None,
        'heures': f"{pointage.heures:.2f}",
        'montant': f"{pointage.montant:.2f}"
    })

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

    filter_type = request.args.get('filter', 'month')
    custom_start = request.args.get('start')
    custom_end = request.args.get('end')

    start_date, end_date = get_date_range(filter_type, custom_start, custom_end)

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
                           filter_type=filter_type,
                           custom_start=custom_start,
                           custom_end=custom_end)

@main_oeuvre_bp.route('/details/<int:id>', methods=['GET'])
@login_required
def details(id):
    user = get_current_user()
    ouvrier = Ouvrier.query.filter_by(id=id, entreprise_id=user.entreprise_id).first_or_404()

    # Check access
    if user.role not in ['admin', 'direction', 'super_admin']:
         assignments = user.assignments.filter_by(actif=True).all()
         allowed_ids = [a.chantier_id for a in assignments]
         if not ouvrier.chantier_id or ouvrier.chantier_id not in allowed_ids:
             flash("Accès non autorisé", "danger")
             return redirect(url_for('main_oeuvre.index'))

    # Filter pointages history
    filter_type = request.args.get('filter', 'month')
    custom_start = request.args.get('start')
    custom_end = request.args.get('end')

    start_date, end_date = get_date_range(filter_type, custom_start, custom_end)

    pointages = ouvrier.pointages.filter(Pointage.date_pointage >= start_date, Pointage.date_pointage < end_date).order_by(Pointage.date_pointage.desc()).all()

    total_heures = sum(p.heures for p in pointages)
    total_montant = sum(p.montant for p in pointages)

    return render_template('main_oeuvre/details.html', ouvrier=ouvrier, pointages=pointages,
                           total_heures=total_heures, total_montant=total_montant,
                           filter_type=filter_type, custom_start=custom_start, custom_end=custom_end)

@main_oeuvre_bp.route('/export_fiche/<int:id>')
@login_required
def export_fiche(id):
    user = get_current_user()
    ouvrier = Ouvrier.query.filter_by(id=id, entreprise_id=user.entreprise_id).first_or_404()

    export_type = request.args.get('type', 'identity')

    # Common Identity Section
    identity_data = [
        ['Nom', ouvrier.nom],
        ['Prénom', ouvrier.prenom],
        ['Poste', ouvrier.poste or '-'],
        ['Téléphone', ouvrier.telephone or '-'],
        ['Taux Horaire', f"{ouvrier.taux_horaire} MAD"],
        ['Nationalité', ouvrier.nationalite or '-'],
        ['Adresse', ouvrier.adresse or '-'],
        ['Ville', ouvrier.ville or '-'],
        ['CNI', ouvrier.cni or '-'],
        ['Chantier Actuel', ouvrier.chantier.nom if ouvrier.chantier else 'Non assigné']
    ]

    sections = [
        {
            'title': 'Informations Personnelles',
            'type': 'kv_list',
            'data': identity_data
        }
    ]

    filename_prefix = "Fiche_Identite"

    if export_type == 'complete':
        filename_prefix = "Dossier_Complet"
        # Filter pointages history
        filter_type = request.args.get('filter', 'month')
        custom_start = request.args.get('start')
        custom_end = request.args.get('end')

        start_date, end_date = get_date_range(filter_type, custom_start, custom_end)

        pointages = ouvrier.pointages.filter(Pointage.date_pointage >= start_date, Pointage.date_pointage < end_date).order_by(Pointage.date_pointage.asc()).all()

        total_heures = sum(p.heures for p in pointages)
        total_montant = sum(p.montant for p in pointages)

        # Pointage Table
        pointage_rows = []
        for p in pointages:
            pointage_rows.append([
                str(p.date_pointage),
                p.check_in.strftime('%H:%M') if p.check_in else '-',
                p.check_out.strftime('%H:%M') if p.check_out else '-',
                f"{p.heures:.2f} h",
                f"{p.montant:.2f} MAD"
            ])

        # Add Summary
        pointage_rows.append(['TOTAL', '', '', f"{total_heures:.2f} h", f"{total_montant:.2f} MAD"])

        sections.append({
            'title': f'Historique & Salaires (Période: {start_date} - {end_date})',
            'type': 'table',
            'headers': ['Date', 'Arrivée', 'Départ', 'Heures', 'Montant'],
            'data': pointage_rows
        })

    from utils.export import export_complex_pdf
    filename = f"{filename_prefix}_{ouvrier.nom}_{ouvrier.prenom}_{date.today()}.pdf"

    return export_complex_pdf(sections, filename, title=f"Dossier: {ouvrier.nom} {ouvrier.prenom}")
