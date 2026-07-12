"""
PDF Report Generator for Eye Disease Detection Application
Uses ReportLab to create a professional, structured medical report.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
INDIGO      = colors.HexColor('#4f46e5')
INDIGO_DARK = colors.HexColor('#3730a3')
INDIGO_LIGHT= colors.HexColor('#e0e7ff')
RED         = colors.HexColor('#dc2626')
RED_LIGHT   = colors.HexColor('#fee2e2')
GREEN       = colors.HexColor('#16a34a')
GREEN_LIGHT = colors.HexColor('#dcfce7')
AMBER       = colors.HexColor('#d97706')
AMBER_LIGHT = colors.HexColor('#fef3c7')
TEAL        = colors.HexColor('#0d9488')
TEAL_LIGHT  = colors.HexColor('#ccfbf1')
GRAY_DARK   = colors.HexColor('#1f2937')
GRAY_MID    = colors.HexColor('#6b7280')
GRAY_LIGHT  = colors.HexColor('#f3f4f6')
WHITE       = colors.white

# Healthy prediction labels
HEALTHY_LABELS = {"No_DR", "normal", "Glaucoma_Negative"}

DISEASE_TYPE_LABELS = {
    'diabetic_retinopathy': 'Diabetic Retinopathy',
    'cataract':             'Cataract',
    'glaucoma':             'Glaucoma',
}


# ---------------------------------------------------------------------------
# Style Helpers
# ---------------------------------------------------------------------------

def get_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles['title'] = ParagraphStyle(
        'ReportTitle', fontSize=22, textColor=WHITE,
        alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28
    )
    styles['subtitle'] = ParagraphStyle(
        'ReportSubtitle', fontSize=11, textColor=colors.HexColor('#c7d2fe'),
        alignment=TA_CENTER, fontName='Helvetica', leading=16
    )
    styles['section_header'] = ParagraphStyle(
        'SectionHeader', fontSize=13, textColor=INDIGO_DARK,
        fontName='Helvetica-Bold', leading=18, spaceAfter=4
    )
    styles['label'] = ParagraphStyle(
        'Label', fontSize=9, textColor=GRAY_MID,
        fontName='Helvetica', leading=13
    )
    styles['value'] = ParagraphStyle(
        'Value', fontSize=11, textColor=GRAY_DARK,
        fontName='Helvetica-Bold', leading=15
    )
    styles['body'] = ParagraphStyle(
        'Body', fontSize=10, textColor=GRAY_DARK,
        fontName='Helvetica', leading=15
    )
    styles['body_bold'] = ParagraphStyle(
        'BodyBold', fontSize=10, textColor=GRAY_DARK,
        fontName='Helvetica-Bold', leading=15
    )
    styles['disclaimer'] = ParagraphStyle(
        'Disclaimer', fontSize=8, textColor=GRAY_MID,
        fontName='Helvetica-Oblique', alignment=TA_CENTER, leading=12
    )
    styles['result_healthy'] = ParagraphStyle(
        'ResultHealthy', fontSize=20, textColor=GREEN,
        fontName='Helvetica-Bold', alignment=TA_CENTER, leading=26
    )
    styles['result_disease'] = ParagraphStyle(
        'ResultDisease', fontSize=20, textColor=RED,
        fontName='Helvetica-Bold', alignment=TA_CENTER, leading=26
    )
    styles['center'] = ParagraphStyle(
        'Center', fontSize=10, textColor=GRAY_DARK,
        fontName='Helvetica', alignment=TA_CENTER, leading=14
    )
    styles['footer'] = ParagraphStyle(
        'Footer', fontSize=8, textColor=GRAY_MID,
        fontName='Helvetica', alignment=TA_CENTER
    )
    return styles


def section_table(title_text, rows, styles, bg_color=GRAY_LIGHT):
    """Helper: renders a titled info table block."""
    elements = []
    elements.append(Paragraph(title_text, styles['section_header']))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceAfter=6))
    tdata = []
    for label, value in rows:
        tdata.append([
            Paragraph(label, styles['label']),
            Paragraph(str(value), styles['body'])
        ])
    t = Table(tdata, colWidths=[4.5*cm, 13*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, bg_color]),
        ('GRID',      (0, 0), (-1, -1), 0.3, colors.HexColor('#e5e7eb')),
        ('VALIGN',    (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('FONTNAME',  (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 0), (0, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY_MID),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 14))
    return elements


def treatment_card(label, text, bg, text_color, styles):
    """Renders a single treatment card row."""
    data = [[
        Paragraph(f"<b>{label}</b>", ParagraphStyle(
            'TCard', fontSize=10, textColor=text_color,
            fontName='Helvetica-Bold', leading=14
        )),
        Paragraph(text, styles['body'])
    ]]
    t = Table(data, colWidths=[3.5*cm, 14*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('GRID',  (0, 0), (-1, -1), 0, WHITE),
        ('VALIGN',(0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return t


# ---------------------------------------------------------------------------
# Main PDF Generator
# ---------------------------------------------------------------------------

def generate_report_pdf(patient: dict, pred: dict, image_path: str, output_path: str) -> str:
    """
    Generate a professional eye disease diagnostic report PDF.

    Args:
        patient     : dict from Patient.to_dict()
        pred        : dict from Prediction.to_dict()
        image_path  : path to the preprocessed output image
        output_path : where to save the PDF

    Returns:
        output_path (str)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm,  bottomMargin=2*cm
    )

    styles  = get_styles()
    story   = []
    W       = A4[0] - 3.6*cm   # usable width

    raw_pred   = pred.get('prediction', '')
    is_healthy = raw_pred in HEALTHY_LABELS
    disease_label = DISEASE_TYPE_LABELS.get(pred.get('disease_type', ''), pred.get('disease_type', ''))
    report_date   = pred.get('diagnosed_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # -------------------------------------------------------------------------
    # HEADER BANNER
    # -------------------------------------------------------------------------
    header_data = [[
        Paragraph("EyeCare AI", styles['title']),
        Paragraph(f"Medical Diagnostic Report<br/>{disease_label}", styles['subtitle']),
        Paragraph(f"Date: {report_date[:10]}<br/>Report #{pred.get('id','')}", ParagraphStyle(
            'HRight', fontSize=9, textColor=colors.HexColor('#c7d2fe'),
            fontName='Helvetica', alignment=TA_RIGHT, leading=14
        ))
    ]]
    header_table = Table(header_data, colWidths=[5*cm, 9*cm, 4.5*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), INDIGO),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING',   (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 18),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # RESULT BANNER
    # -------------------------------------------------------------------------
    result_bg    = GREEN_LIGHT if is_healthy else RED_LIGHT
    result_color = GREEN       if is_healthy else RED
    result_text  = pred.get('prediction', '').replace('_', ' ').title()
    result_icon  = "HEALTHY - No Disease Detected" if is_healthy else f"CONDITION DETECTED"
    conf_text    = pred.get('confidence', '')

    result_data = [[
        Paragraph(result_text, ParagraphStyle(
            'RB', fontSize=22, textColor=result_color,
            fontName='Helvetica-Bold', alignment=TA_CENTER, leading=28
        )),
        Paragraph(f"{result_icon}<br/><font size=10 color='#{('16a34a' if is_healthy else 'dc2626')}'>Confidence: {conf_text}</font>",
                  ParagraphStyle('RS', fontSize=12, textColor=result_color,
                                 fontName='Helvetica', alignment=TA_CENTER, leading=18))
    ]]
    result_table = Table(result_data, colWidths=[W/2, W/2])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), result_bg),
        ('GRID',       (0, 0), (-1, -1), 0.5, result_color),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING',   (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 16),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 16))

    # -------------------------------------------------------------------------
    # PATIENT INFORMATION
    # -------------------------------------------------------------------------
    story += section_table(
        "Patient Information",
        [
            ("Name",      patient.get('name', 'N/A')),
            ("Age",       f"{patient.get('age', 'N/A')} years"),
            ("Gender",    patient.get('gender', 'N/A')),
            ("Contact",   patient.get('contact', 'N/A')),
            ("Patient ID",str(patient.get('id', 'N/A'))),
        ],
        styles,
        bg_color=INDIGO_LIGHT
    )

    # -------------------------------------------------------------------------
    # ANALYZED IMAGE
    # -------------------------------------------------------------------------
    story.append(Paragraph("Analyzed Eye Image", styles['section_header']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceAfter=8))

    if image_path and os.path.exists(image_path):
        try:
            img = RLImage(image_path, width=7*cm, height=7*cm, kind='proportional')
            img_table = Table([[img]], colWidths=[W])
            img_table.setStyle(TableStyle([
                ('ALIGN',  (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, -1), GRAY_LIGHT),
                ('TOPPADDING',   (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
            ]))
            story.append(img_table)
        except Exception as e:
            story.append(Paragraph(f"[Image could not be loaded: {e}]", styles['body']))
    else:
        story.append(Paragraph("[No image available]", styles['body']))

    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # DIAGNOSIS DETAILS
    # -------------------------------------------------------------------------
    if not is_healthy:
        story += section_table(
            "Diagnosis Details",
            [
                ("Disease Type",  disease_label),
                ("Condition",     pred.get('prediction','').replace('_',' ').title()),
                ("Confidence",    pred.get('confidence', 'N/A')),
                ("Possible Cause",pred.get('cause', 'N/A')),
                ("Treatment",     pred.get('treatment', 'N/A')),
            ],
            styles
        )

        # Treatment Approaches
        story.append(Paragraph("Treatment Approaches", styles['section_header']))
        story.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceAfter=8))

        story.append(treatment_card(
            "Homeopathy", pred.get('homeopathy', 'N/A'),
            colors.HexColor('#fff1f2'), RED, styles
        ))
        story.append(Spacer(1, 4))
        story.append(treatment_card(
            "Allopathy", pred.get('allopathy', 'N/A'),
            colors.HexColor('#eff6ff'), colors.HexColor('#1d4ed8'), styles
        ))
        story.append(Spacer(1, 4))
        story.append(treatment_card(
            "Ayurveda", pred.get('ayurveda', 'N/A'),
            colors.HexColor('#f0fdf4'), GREEN, styles
        ))
        story.append(Spacer(1, 14))

        # Hospitals & Cost
        story.append(Paragraph("Hospitals & Cost Estimates", styles['section_header']))
        story.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceAfter=8))

        hosp_data = [
            [
                Paragraph("<b>India</b>", ParagraphStyle(
                    'HI', fontSize=11, textColor=colors.HexColor('#b45309'),
                    fontName='Helvetica-Bold', leading=15
                )),
                Paragraph("<b>USA</b>", ParagraphStyle(
                    'HU', fontSize=11, textColor=colors.HexColor('#1d4ed8'),
                    fontName='Helvetica-Bold', leading=15
                ))
            ],
            [
                Paragraph(pred.get('india_hospitals', 'N/A'), styles['body']),
                Paragraph(pred.get('usa_hospitals',   'N/A'), styles['body'])
            ],
            [
                Paragraph(f"<b>Est. Cost:</b> {pred.get('cost_india','N/A')}", styles['body']),
                Paragraph(f"<b>Est. Cost:</b> {pred.get('cost_usa',  'N/A')}", styles['body'])
            ]
        ]
        hosp_table = Table(hosp_data, colWidths=[W/2, W/2])
        hosp_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (0, -1), AMBER_LIGHT),
            ('BACKGROUND',   (1, 0), (1, -1), colors.HexColor('#dbeafe')),
            ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ]))
        story.append(hosp_table)
        story.append(Spacer(1, 10))

        # Success Rate
        sr_data = [[
            Paragraph("Treatment Success Rate", ParagraphStyle(
                'SR', fontSize=11, textColor=AMBER, fontName='Helvetica-Bold',
                alignment=TA_CENTER, leading=16
            )),
            Paragraph(pred.get('success_rate', 'N/A'), ParagraphStyle(
                'SRV', fontSize=16, textColor=AMBER, fontName='Helvetica-Bold',
                alignment=TA_CENTER, leading=22
            ))
        ]]
        sr_table = Table(sr_data, colWidths=[W/2, W/2])
        sr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), AMBER_LIGHT),
            ('GRID',       (0, 0), (-1, -1), 0.5, AMBER),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',   (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 12),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(sr_table)
        story.append(Spacer(1, 14))

    else:
        # Healthy message
        healthy_data = [[
            Paragraph(
                "Great News! No disease detected in the analyzed image.<br/>"
                "<font size=10>Continue regular eye checkups for preventive care.</font>",
                ParagraphStyle('HM', fontSize=13, textColor=GREEN,
                               fontName='Helvetica-Bold', alignment=TA_CENTER, leading=20)
            )
        ]]
        h_table = Table(healthy_data, colWidths=[W])
        h_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), GREEN_LIGHT),
            ('GRID',       (0, 0), (-1, -1), 0.5, GREEN),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING',   (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 18),
        ]))
        story.append(h_table)
        story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # DISCLAIMER
    # -------------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_MID, spaceAfter=8))
    story.append(Paragraph(
        "IMPORTANT DISCLAIMER: This report is generated by an AI-based screening tool for "
        "informational and educational purposes only. It does not constitute a medical diagnosis. "
        "Please consult a qualified ophthalmologist or healthcare professional for proper evaluation, "
        "diagnosis, and treatment. Early professional consultation is critical for eye diseases.",
        styles['disclaimer']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by EyeCare AI | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        "Powered by EfficientNetB0 Deep Learning",
        styles['footer']
    ))

    doc.build(story)
    print(f"PDF report saved: {output_path}")
    return output_path