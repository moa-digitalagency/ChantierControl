import io
import pandas as pd
from flask import send_file, flash
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_to_excel(data_list, filename="export.xlsx", sheet_name='Données'):
    """
    Exports a list of dictionaries to Excel.
    data_list: List of dicts.
    """
    try:
        if not data_list:
            # Create empty dataframe with message
            df = pd.DataFrame({'Info': ['Aucune donnée à exporter']})
        else:
            df = pd.DataFrame(data_list)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

        output.seek(0)
        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Export error: {e}")
        return None

def export_to_pdf(data_list, filename="export.pdf"):
    try:
        if not data_list:
            return None

        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []

        # Convert dict to list of lists
        headers = list(data_list[0].keys())
        data = [headers]
        for row in data_list:
            data.append([str(row.get(h, '')) for h in headers])

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        doc.build(elements)

        output.seek(0)
        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"PDF Export error: {e}")
        return None

def export_to_csv(data_list, filename="export.csv"):
    try:
        if not data_list:
            df = pd.DataFrame({'Info': ['Aucune donnée à exporter']})
        else:
            df = pd.DataFrame(data_list)

        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility
        output.seek(0)
        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype='text/csv'
        )
    except Exception as e:
        print(f"Export error: {e}")
        return None
