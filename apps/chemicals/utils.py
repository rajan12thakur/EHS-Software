import datetime
import os
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle
)

from django.utils.timezone import localtime


# ================= PAGE NUMBER =================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(page_count)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.darkgrey)
        self.drawRightString(200 * mm, 15 * mm, f"Page {self._pageNumber} of {page_count}")


# ================= HELPERS =================
def _safe_text(value, fallback="N/A"):
    return str(value) if value else fallback


def _format_dt(value, fallback="N/A"):
    if not value:
        return fallback
    try:
        return localtime(value).strftime("%d-%b-%Y, %I:%M %p")
    except Exception:
        return str(value)


# ================= MAIN PDF =================
def generate_chemical_pdf(chemical):
    buffer = BytesIO()

    header_height = 1.6 * inch
    left_margin = 15 * mm
    right_margin = 15 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=right_margin,
        leftMargin=left_margin,
        topMargin=header_height + 22 * mm,
        bottomMargin=25 * mm,
    )

    story = []
    drawable_width = A4[0] - left_margin - right_margin

    # COLORS (same as permit)
    primary_text_color = colors.HexColor('#212529')
    secondary_text_color = colors.HexColor('#495057')
    header_bg_color = colors.HexColor('#F8F9FA')
    border_color = colors.HexColor('#DEE2E6')

    # STYLES (same as permit)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='HeaderTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=primary_text_color))
    styles.add(ParagraphStyle(name='HeaderInfo', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=secondary_text_color, leading=12))
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=11, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=primary_text_color, spaceBefore=6))
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=10, fontName='Helvetica-Bold', textColor=primary_text_color, spaceBefore=8, spaceAfter=4, alignment=TA_LEFT, backColor=header_bg_color, borderPadding=(6, 4)))
    styles.add(ParagraphStyle(name='Label', fontSize=9, fontName='Helvetica-Bold', textColor=primary_text_color))
    styles.add(ParagraphStyle(name='Value', fontSize=9, fontName='Helvetica', textColor=secondary_text_color, leading=12))
    styles.add(ParagraphStyle(name='FooterText', fontSize=8, fontName='Helvetica', textColor=colors.darkgrey, alignment=TA_CENTER))

    # ================= HEADER =================
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
    logo_img = Image(logo_path, width=2.2 * inch, height=header_height) if os.path.exists(logo_path) else Paragraph("<b>Your Company</b>", styles['HeaderTitle'])

    header_data = [
        [logo_img, Paragraph("<b>INTEGRATED MANAGEMENT SYSTEM [EHS]</b>", styles['HeaderTitle']), Paragraph("DOC NO: EHS/PTW/F-01", styles['HeaderInfo'])],
        ['', Paragraph("<b>CHEMICAL REPORT</b>", styles['HeaderTitle']), Paragraph("REV NO: 00<br/>DATE: 01-01-2024", styles['HeaderInfo'])],
    ]

    header_table = Table(
        header_data,
        colWidths=[drawable_width * 0.2875, drawable_width * 0.4875, drawable_width * 0.225],
        rowHeights=[0.8 * inch, 0.8 * inch],
    )

    header_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('SPAN', (0, 0), (0, 1)),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    def draw_header(pdf_canvas, pdf_doc):
        pdf_canvas.saveState()
        width, height = header_table.wrap(pdf_doc.width, pdf_doc.topMargin)
        header_table.drawOn(
            pdf_canvas,
            pdf_doc.leftMargin,
            pdf_doc.height + pdf_doc.topMargin - height + 5 * mm
        )
        pdf_canvas.restoreState()

    # ================= TITLE =================
    story.append(Spacer(1, 4 * mm))

    title_table = Table([
        [
            Paragraph("<b>Chemical Report</b>", styles['ReportTitle']),
            Paragraph(f"<b>Chemical Name:</b><br/>{_safe_text(chemical.chemical_name)}", styles['HeaderInfo'])
        ]
    ], colWidths=[drawable_width * 0.7, drawable_width * 0.3])

    title_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(title_table)
    story.append(Spacer(1, 6 * mm))

    # ================= IDENTIFICATION =================
    story.append(Paragraph("<b>1. CHEMICAL IDENTIFICATION</b>", styles['SectionHeader']))

    ident_table = Table([
        [Paragraph("<b>Name:</b>", styles['Label']), Paragraph(_safe_text(chemical.chemical_name), styles['Value']),
         Paragraph("<b>CAS:</b>", styles['Label']), Paragraph(_safe_text(chemical.cas_number), styles['Value'])],

        [Paragraph("<b>Trade:</b>", styles['Label']), Paragraph(_safe_text(chemical.trade_name), styles['Value']),
         Paragraph("<b>UN No:</b>", styles['Label']), Paragraph(_safe_text(chemical.un_number), styles['Value'])],

        [Paragraph("<b>Owner:</b>", styles['Label']), Paragraph(_safe_text(chemical.owner), styles['Value']),
         Paragraph("<b>Status:</b>", styles['Label']), Paragraph(_safe_text(chemical.get_status_display()), styles['Value'])],
    ], colWidths=[drawable_width / 4] * 4)

    ident_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(ident_table)
    story.append(Spacer(1, 6 * mm))

    # ================= INVENTORY =================
    story.append(Paragraph("<b>2. INVENTORY DETAILS</b>", styles['SectionHeader']))

    inv_table = Table([
        [Paragraph("<b>Supplier:</b>", styles['Label']), Paragraph(_safe_text(chemical.supplier), styles['Value'])],
        [Paragraph("<b>Quantity:</b>", styles['Label']), Paragraph(f"{chemical.quantity} {chemical.quantity_unit}", styles['Value'])],
        [Paragraph("<b>Storage:</b>", styles['Label']), Paragraph(_safe_text(chemical.storage_location), styles['Value'])],
        [Paragraph("<b>Receipt:</b>", styles['Label']), Paragraph(_format_dt(chemical.receipt_date), styles['Value'])],
        [Paragraph("<b>Expiry:</b>", styles['Label']), Paragraph(_format_dt(chemical.expiration_date), styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])

    inv_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(inv_table)
    story.append(Spacer(1, 6 * mm))

    # LOCATION 
    story.append(Paragraph("<b>3. LOCATION DETAILS</b>", styles['SectionHeader']))

    loc_table = Table([
        [Paragraph("<b>Plant:</b>", styles['Label']), Paragraph(_safe_text(chemical.plant), styles['Value'])],
        [Paragraph("<b>Zone:</b>", styles['Label']), Paragraph(_safe_text(chemical.zone), styles['Value'])],
        [Paragraph("<b>Location:</b>", styles['Label']), Paragraph(_safe_text(chemical.location), styles['Value'])],
        [Paragraph("<b>Sub Location:</b>", styles['Label']), Paragraph(_safe_text(chemical.sublocation), styles['Value'])],
        [Paragraph("<b>Department:</b>", styles['Label']), Paragraph(_safe_text(chemical.department), styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])

    loc_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(loc_table)
    story.append(Spacer(1, 6 * mm))

    # EHS Compliance
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<b>4. EHS COMPLIANCE</b>", styles['SectionHeader']))

    ehs = chemical.ehs_compliance or {}
    ghs = ", ".join(ehs.get("ghs", [])) or "N/A"
    ppe = ", ".join(ehs.get("ppe", [])) or "N/A"

    ehs_table = Table([
        [Paragraph("<b>GHS Symbols:</b>", styles['Label']), Paragraph(ghs, styles['Value'])],
        [Paragraph("<b>PPE Required:</b>", styles['Label']), Paragraph(ppe, styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])

    ehs_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(ehs_table)

    #Additional Details
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<b>5. ADDITIONAL DETAILS</b>", styles['SectionHeader']))

    additional_table = Table([
        [Paragraph("<b>Lot Number:</b>", styles['Label']), Paragraph(_safe_text(chemical.lot_number), styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])

    additional_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(additional_table)

    # system information
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<b>6. SYSTEM INFORMATION</b>", styles['SectionHeader']))

    system_table = Table([
        [Paragraph("<b>Created By:</b>", styles['Label']), Paragraph(_safe_text(chemical.created_by), styles['Value'])],
        [Paragraph("<b>Created At:</b>", styles['Label']), Paragraph(_format_dt(chemical.created_at), styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])

    system_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(system_table)

    # FOOTER 
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        f"This is a system-generated chemical report from EHS-360 on {datetime.datetime.now().strftime('%d-%b-%Y at %I:%M %p')}",
        styles['FooterText'],
    ))

    doc.build(
        story,
        onFirstPage=draw_header,
        onLaterPages=draw_header,
        canvasmaker=NumberedCanvas
    )

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Chemical_{chemical.id}.pdf"'
    response.write(pdf)

    return response