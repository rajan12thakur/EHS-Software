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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


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


def _safe_text(value, fallback='N/A'):
    if value is None or value == '':
        return fallback
    return str(value)


def _format_dt(value, fallback='N/A'):
    if not value:
        return fallback
    return value.strftime('%d-%b-%Y, %I:%M %p')


def generate_permit_pdf(permit):
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

    try:
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    except Exception:
        pass

    primary_text_color = colors.HexColor('#212529')
    secondary_text_color = colors.HexColor('#495057')
    header_bg_color = colors.HexColor('#F8F9FA')
    border_color = colors.HexColor('#DEE2E6')

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='HeaderTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=primary_text_color))
    styles.add(ParagraphStyle(name='HeaderInfo', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=secondary_text_color, leading=12))
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=11, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=primary_text_color, spaceBefore=6))
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=10, fontName='Helvetica-Bold', textColor=primary_text_color, spaceBefore=8, spaceAfter=4, alignment=TA_LEFT, backColor=header_bg_color, borderPadding=(6, 4)))
    styles.add(ParagraphStyle(name='Label', fontSize=9, fontName='Helvetica-Bold', textColor=primary_text_color, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Value', fontSize=9, fontName='Helvetica', textColor=secondary_text_color, alignment=TA_LEFT, leading=12))
    styles.add(ParagraphStyle(name='FooterText', fontSize=8, fontName='Helvetica', textColor=colors.darkgrey, alignment=TA_CENTER))

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
    logo_img = Image(logo_path, width=2.2 * inch, height=header_height) if os.path.exists(logo_path) else Paragraph("<b>Your Company</b>", styles['HeaderTitle'])

    header_data = [
        [logo_img, Paragraph("<b>INTEGRATED MANAGEMENT SYSTEM [EHS]</b>", styles['HeaderTitle']), Paragraph("DOC NO: EHS/PTW/F-01", styles['HeaderInfo'])],
        ['', Paragraph("<b>PERMIT TO WORK</b>", styles['HeaderTitle']), Paragraph("REV NO: 00 &<br/>DATE: 01-01-2024", styles['HeaderInfo'])],
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
        header_table.drawOn(pdf_canvas, pdf_doc.leftMargin, pdf_doc.height + pdf_doc.topMargin - height + 5 * mm)
        pdf_canvas.restoreState()

    story.append(Spacer(1, 4 * mm))
    ref_table = Table([
        [
            Paragraph("<b>Permit Work Report</b>", styles['ReportTitle']),
            Paragraph(f"<b>Reference number:</b><br/>{_safe_text(permit.permit_number, f'PTW-{permit.pk}')}", styles['HeaderInfo']),
        ]
    ], colWidths=[drawable_width * 0.7, drawable_width * 0.3])
    ref_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("<b>1. PERMIT OVERVIEW</b>", styles['SectionHeader']))
    overview_table = Table([
        [Paragraph("<b>Permit Number:</b>", styles['Label']), Paragraph(_safe_text(permit.permit_number, f'PTW-{permit.pk}'), styles['Value']), Paragraph("<b>Status:</b>", styles['Label']), Paragraph(permit.get_status_display(), styles['Value'])],
        [Paragraph("<b>Permit Type:</b>", styles['Label']), Paragraph(_safe_text(getattr(permit.permit_type, 'name', None)), styles['Value']), Paragraph("<b>Priority:</b>", styles['Label']), Paragraph(permit.get_priority_display(), styles['Value'])],
        [Paragraph("<b>Start Date:</b>", styles['Label']), Paragraph(_format_dt(permit.start_date), styles['Value']), Paragraph("<b>End Date:</b>", styles['Label']), Paragraph(_format_dt(permit.end_date), styles['Value'])],
    ], colWidths=[drawable_width / 4] * 4)
    overview_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("<b>2. REQUESTER & LOCATION DETAILS</b>", styles['SectionHeader']))
    detail_rows = [
        [Paragraph("<b>Requester:</b>", styles['Label']), Paragraph(_safe_text(permit.requester_name), styles['Value'])],
        [Paragraph("<b>Plant:</b>", styles['Label']), Paragraph(_safe_text(permit.plant), styles['Value'])],
        [Paragraph("<b>Zone:</b>", styles['Label']), Paragraph(_safe_text(permit.zone), styles['Value'])],
        [Paragraph("<b>Location:</b>", styles['Label']), Paragraph(_safe_text(permit.location), styles['Value'])],
        [Paragraph("<b>Sub Location:</b>", styles['Label']), Paragraph(_safe_text(permit.sublocation), styles['Value'])],
        [Paragraph("<b>Department:</b>", styles['Label']), Paragraph(_safe_text(permit.department), styles['Value'])],
        [Paragraph("<b>Supervisor:</b>", styles['Label']), Paragraph(_safe_text(permit.supervisor_name), styles['Value'])],
        [Paragraph("<b>Reporting Engineer:</b>", styles['Label']), Paragraph(_safe_text(permit.reporting_engineer), styles['Value'])],
        [Paragraph("<b>Contractor Company:</b>", styles['Label']), Paragraph(_safe_text(permit.contractor_company), styles['Value'])],
        [Paragraph("<b>Contact Number:</b>", styles['Label']), Paragraph(_safe_text(permit.contact_number), styles['Value'])],
    ]
    detail_table = Table(detail_rows, colWidths=[drawable_width * 0.25, drawable_width * 0.75])
    detail_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("<b>3. WORK DESCRIPTION & SAFETY</b>", styles['SectionHeader']))
    hazards_text = ', '.join(permit.hazards) if permit.hazards else 'N/A'
    work_table = Table([
        [Paragraph("<b>Job Description:</b>", styles['Label']), Paragraph(_safe_text(permit.job_description).replace('\n', '<br/>'), styles['Value'])],
        [Paragraph("<b>Hazard Risk Level:</b>", styles['Label']), Paragraph(_safe_text(permit.get_hazard_risk_level_display() if permit.hazard_risk_level else None), styles['Value'])],
        [Paragraph("<b>Hazards:</b>", styles['Label']), Paragraph(_safe_text(hazards_text), styles['Value'])],
        [Paragraph("<b>Safety Measures:</b>", styles['Label']), Paragraph(_safe_text(permit.safety_measures).replace('\n', '<br/>'), styles['Value'])],
    ], colWidths=[drawable_width * 0.25, drawable_width * 0.75])
    work_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(work_table)

    contractors = permit.contractors.all()
    if contractors.exists():
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("<b>4. CONTRACTORS</b>", styles['SectionHeader']))
        contractor_data = [[
            Paragraph("<b>Name</b>", styles['Label']),
            Paragraph("<b>Trade</b>", styles['Label']),
            Paragraph("<b>ID Number</b>", styles['Label']),
            Paragraph("<b>Contact</b>", styles['Label']),
        ]]
        for contractor in contractors:
            contractor_data.append([
                Paragraph(_safe_text(contractor.name), styles['Value']),
                Paragraph(_safe_text(contractor.trade), styles['Value']),
                Paragraph(_safe_text(contractor.id_number), styles['Value']),
                Paragraph(_safe_text(contractor.contact_number), styles['Value']),
            ])
        contractor_table = Table(contractor_data, colWidths=[drawable_width * 0.3, drawable_width * 0.2, drawable_width * 0.25, drawable_width * 0.25])
        contractor_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, border_color),
            ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(contractor_table)

    approval_rows = [
        [Paragraph("<b>Approver:</b>", styles['Label']), Paragraph(_safe_text(permit.approver), styles['Value'])],
        [Paragraph("<b>Rejection Reason:</b>", styles['Label']), Paragraph(_safe_text(permit.rejection_reason), styles['Value'])],
        [Paragraph("<b>Close Out Notes:</b>", styles['Label']), Paragraph(_safe_text(permit.close_out_notes).replace('\n', '<br/>'), styles['Value'])],
        [Paragraph("<b>Created At:</b>", styles['Label']), Paragraph(_format_dt(permit.created_at), styles['Value'])],
        [Paragraph("<b>Updated At:</b>", styles['Label']), Paragraph(_format_dt(permit.updated_at), styles['Value'])],
    ]
    if hasattr(permit, 'closure'):
        approval_rows.extend([
            [Paragraph("<b>Closure Status:</b>", styles['Label']), Paragraph(_safe_text(permit.closure.get_work_status_display()), styles['Value'])],
            [Paragraph("<b>Closed At:</b>", styles['Label']), Paragraph(_format_dt(permit.closure.closed_at), styles['Value'])],
            [Paragraph("<b>Closure Summary:</b>", styles['Label']), Paragraph(_safe_text(permit.closure.work_summary).replace('\n', '<br/>'), styles['Value'])],
        ])

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<b>5. APPROVAL & CLOSURE</b>", styles['SectionHeader']))
    approval_table = Table(approval_rows, colWidths=[drawable_width * 0.25, drawable_width * 0.75])
    approval_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(approval_table)

    attachments = permit.attachments.all()
    if attachments.exists():
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("<b>6. ATTACHMENTS</b>", styles['SectionHeader']))
        attachment_data = [[
            Paragraph("<b>Description</b>", styles['Label']),
            Paragraph("<b>Filename</b>", styles['Label']),
            Paragraph("<b>Uploaded At</b>", styles['Label']),
        ]]
        for attachment in attachments:
            attachment_data.append([
                Paragraph(_safe_text(attachment.description), styles['Value']),
                Paragraph(_safe_text(attachment.original_filename), styles['Value']),
                Paragraph(_format_dt(attachment.uploaded_at), styles['Value']),
            ])
        attachment_table = Table(attachment_data, colWidths=[drawable_width * 0.35, drawable_width * 0.35, drawable_width * 0.30])
        attachment_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, border_color),
            ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(attachment_table)

    if hasattr(permit, 'closure') and permit.closure.photos.exists():
        photo_flowables = [Spacer(1, 6 * mm), Paragraph("<b>7. CLOSURE PHOTOS</b>", styles['SectionHeader'])]
        photo_table_data = []
        photo_row = []
        for photo in permit.closure.photos.all():
            if photo.photo and hasattr(photo.photo, 'path') and os.path.exists(photo.photo.path):
                try:
                    image = Image(photo.photo.path, width=3 * inch, height=3 * inch, kind='proportional')
                    image.hAlign = 'CENTER'
                    photo_row.append(image)
                except Exception:
                    photo_row.append(Paragraph("<i>Error reading image</i>", styles['Value']))
            else:
                photo_row.append(Paragraph("<i>Image not found</i>", styles['Value']))
            if len(photo_row) == 2:
                photo_table_data.append(photo_row)
                photo_row = []
        if photo_row:
            photo_table_data.append(photo_row)
        if photo_table_data:
            photo_table = Table(photo_table_data, colWidths=[drawable_width / 2] * 2, rowHeights=3.2 * inch)
            photo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, border_color),
            ]))
            photo_flowables.append(photo_table)
            story.append(KeepTogether(photo_flowables))

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        f"This is a system-generated permit report from EHS-360 on {datetime.datetime.now().strftime('%d-%b-%Y at %I:%M %p')}",
        styles['FooterText'],
    ))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header, canvasmaker=NumberedCanvas)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    filename = _safe_text(permit.permit_number, f'PTW-{permit.pk}')
    response['Content-Disposition'] = f'attachment; filename="Permit_Report_{filename}.pdf"'
    response.write(pdf)
    return response
