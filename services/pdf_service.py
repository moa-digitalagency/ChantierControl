import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from algorithms import calculer_kpi_chantier, verifier_alertes
from models import db, Chantier
from datetime import datetime

def generate_chantier_report(chantier_id, output_path=None):
    # Import inside function to avoid circular import
    from services import get_derniers_achats

    chantier = db.session.get(Chantier, chantier_id)
    if not chantier:
        return None

    kpi = calculer_kpi_chantier(chantier_id)
    alertes = verifier_alertes(chantier_id, kpi=kpi)
    derniers_achats = get_derniers_achats(chantier_id, limit=10)

    if output_path is None:
        # Create a temporary file or return bytes?
        # For simplicity, we'll assume the caller manages the file path or we return the path
        import tempfile
        fd, output_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    story.append(Paragraph(f"Rapport de Chantier: {chantier.nom}", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Info Chantier
    story.append(Paragraph("Informations Générales", styles['Heading2']))
    info_data = [
        ["Adresse", chantier.adresse or "N/A"],
        ["Budget Prévisionnel", f"{chantier.budget_previsionnel:,.2f} MAD"],
        ["Statut", chantier.statut],
    ]
    t = Table(info_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # KPI & Budget
    if kpi:
        story.append(Paragraph("État Budgétaire", styles['Heading2']))
        kpi_data = [
            ["Coût Total", f"{kpi['cout_total']:,.2f} MAD"],
            ["dont Achats", f"{kpi['total_achats']:,.2f} MAD"],
            ["dont Main d'oeuvre", f"{kpi['total_salaires']:,.2f} MAD"],
            ["Taux Consommation", f"{kpi['taux_consommation']:.1f}%"],
            ["Écart Budgétaire", f"{kpi['ecart_budgetaire']:,.2f} MAD"],
            ["Solde Avance", f"{kpi['solde_avance']:,.2f} MAD"],
        ]
        t = Table(kpi_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    # Alerts
    if alertes:
        story.append(Paragraph("Alertes", styles['Heading2']))
        for alerte in alertes:
            color = colors.red if alerte['niveau'] == 'danger' else colors.orange
            p = Paragraph(f"• {alerte['message']}", ParagraphStyle('Alert', parent=styles['Normal'], textColor=color))
            story.append(p)
        story.append(Spacer(1, 12))

    # Derniers Achats
    if derniers_achats:
        story.append(Paragraph("Derniers Achats (Top 10)", styles['Heading2']))
        achats_data = [["Date", "Fournisseur", "Montant", "Catégorie"]]
        for achat in derniers_achats:
            achats_data.append([
                achat.date_achat.strftime('%d/%m/%Y'),
                achat.fournisseur,
                f"{achat.montant:,.2f}",
                achat.categorie
            ])

        t = Table(achats_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
        ]))
        story.append(t)

    doc.build(story)
    return output_path
