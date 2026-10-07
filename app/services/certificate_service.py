from io import BytesIO
import re

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.config import CERTIFLOW_BASE_URL, GENERATED_CERTIFICATES_DIR
from app.models import Certificate, Job


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def sanitize_filename(value: str) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        value.strip(),
    )
    return value.strip("_") or "recipient"


def build_verification_url(certificate_id: str) -> str:
    return (
        f"{CERTIFLOW_BASE_URL}"
        f"/api/v1/certificates/{certificate_id}/verify"
    )


def fit_text(
    text: str,
    font_name: str,
    max_size: int,
    min_size: int,
    max_width: float,
) -> int:
    size = max_size

    while size > min_size:
        if stringWidth(
            text,
            font_name,
            size,
        ) <= max_width:
            return size

        size -= 1

    return min_size


# ---------------------------------------------------------
# Main certificate generator
# ---------------------------------------------------------

def generate_certificate_pdf(
    job: Job,
    certificate: Certificate,
) -> str:

    job_directory = (
        GENERATED_CERTIFICATES_DIR / job.id
    )

    job_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = sanitize_filename(
        certificate.recipient_name
    )

    filename = (
        f"{safe_name}_{certificate.certificate_id}.pdf"
    )

    output_path = job_directory / filename

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=(page_width, page_height),
    )

    # =====================================================
    # COLOR PALETTE
    # =====================================================

    navy = colors.HexColor("#102A43")
    deep_blue = colors.HexColor("#163A5F")
    blue = colors.HexColor("#2563A6")
    gold = colors.HexColor("#C49A52")
    light_gold = colors.HexColor("#E7D4A8")
    background = colors.HexColor("#F7F9FC")
    white = colors.white
    slate = colors.HexColor("#64748B")
    dark = colors.HexColor("#172033")
    light_border = colors.HexColor("#D7E0EA")

    # =====================================================
    # BACKGROUND
    # =====================================================

    pdf.setFillColor(background)

    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0,
    )

    # =====================================================
    # TOP BRAND BAND
    # =====================================================

    header_height = 31 * mm

    pdf.setFillColor(navy)

    pdf.rect(
        0,
        page_height - header_height,
        page_width,
        header_height,
        fill=1,
        stroke=0,
    )

    # Small gold accent line

    pdf.setFillColor(gold)

    pdf.rect(
        0,
        page_height - header_height,
        page_width,
        1.6 * mm,
        fill=1,
        stroke=0,
    )

    # Brand

    pdf.setFillColor(white)
    pdf.setFont(
        "Helvetica-Bold",
        18,
    )

    pdf.drawString(
        22 * mm,
        page_height - 17 * mm,
        "CERTIFLOW",
    )

    pdf.setFillColor(
        colors.HexColor("#C9D7E8")
    )

    pdf.setFont(
        "Helvetica",
        7,
    )

    pdf.drawString(
        22 * mm,
        page_height - 23 * mm,
        "CERTIFICATE MANAGEMENT PLATFORM",
    )

    # Enterprise label

    pdf.setFillColor(light_gold)
    pdf.setFont(
        "Helvetica-Bold",
        7,
    )

    pdf.drawRightString(
        page_width - 22 * mm,
        page_height - 18 * mm,
        "DIGITALLY VERIFIED",
    )

    pdf.setFillColor(
        colors.HexColor("#C9D7E8")
    )

    pdf.setFont(
        "Helvetica",
        6.5,
    )

    pdf.drawRightString(
        page_width - 22 * mm,
        page_height - 24 * mm,
        "SECURE CERTIFICATE RECORD",
    )

    # =====================================================
    # MAIN WHITE CARD
    # =====================================================

    card_x = 18 * mm
    card_y = 15 * mm

    card_width = page_width - 36 * mm
    card_height = page_height - 51 * mm

    pdf.setFillColor(white)

    pdf.roundRect(
        card_x,
        card_y,
        card_width,
        card_height,
        5 * mm,
        fill=1,
        stroke=0,
    )

    # Outer subtle border

    pdf.setStrokeColor(light_border)
    pdf.setLineWidth(0.7)

    pdf.roundRect(
        card_x,
        card_y,
        card_width,
        card_height,
        5 * mm,
        fill=0,
        stroke=1,
    )

    # Gold inner accent

    pdf.setStrokeColor(light_gold)
    pdf.setLineWidth(0.8)

    pdf.roundRect(
        card_x + 4 * mm,
        card_y + 4 * mm,
        card_width - 8 * mm,
        card_height - 8 * mm,
        3.5 * mm,
        fill=0,
        stroke=1,
    )

    # =====================================================
    # TITLE
    # =====================================================

    center_x = page_width / 2

    title_y = page_height - 67 * mm

    pdf.setFillColor(navy)

    pdf.setFont(
        "Helvetica-Bold",
        25,
    )

    pdf.drawCentredString(
        center_x,
        title_y,
        "CERTIFICATE OF COMPLETION",
    )

    # Gold divider

    divider_width = 42 * mm

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(1.2)

    pdf.line(
        center_x - divider_width / 2,
        title_y - 7 * mm,
        center_x + divider_width / 2,
        title_y - 7 * mm,
    )

    # =====================================================
    # PRESENTED TO
    # =====================================================

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica",
        8,
    )

    pdf.drawCentredString(
        center_x,
        title_y - 19 * mm,
        "THIS CERTIFICATE IS PROUDLY PRESENTED TO",
    )

    # =====================================================
    # RECIPIENT NAME
    # =====================================================

    recipient_name = (
        certificate.recipient_name.upper()
    )

    recipient_size = fit_text(
        recipient_name,
        "Helvetica-Bold",
        25,
        15,
        page_width - 105 * mm,
    )

    pdf.setFillColor(dark)

    pdf.setFont(
        "Helvetica-Bold",
        recipient_size,
    )

    pdf.drawCentredString(
        center_x,
        title_y - 33 * mm,
        recipient_name,
    )

    # =====================================================
    # DESCRIPTION
    # =====================================================

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica",
        9,
    )

    pdf.drawCentredString(
        center_x,
        title_y - 44 * mm,
        "for successfully completing",
    )

    # =====================================================
    # EVENT NAME
    # =====================================================

    event_name = job.event_name

    event_size = fit_text(
        event_name,
        "Helvetica-Bold",
        17,
        10,
        page_width - 105 * mm,
    )

    pdf.setFillColor(deep_blue)

    pdf.setFont(
        "Helvetica-Bold",
        event_size,
    )

    pdf.drawCentredString(
        center_x,
        title_y - 55 * mm,
        event_name,
    )

    # =====================================================
    # DATE
    # =====================================================

    issue_date = job.event_date.strftime(
        "%d %B %Y"
    ).upper()

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica",
        8,
    )

    pdf.drawCentredString(
        center_x,
        title_y - 67 * mm,
        f"ISSUED ON  |  {issue_date}",
    )

    # =====================================================
    # BOTTOM INFORMATION STRIP
    # =====================================================

    info_y = card_y + 13 * mm

    pdf.setFillColor(
        colors.HexColor("#F4F7FA")
    )

    pdf.roundRect(
        card_x + 10 * mm,
        info_y,
        card_width - 62 * mm,
        13 * mm,
        2.5 * mm,
        fill=1,
        stroke=0,
    )

    # Certificate ID

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica",
        6.5,
    )

    pdf.drawString(
        card_x + 15 * mm,
        info_y + 8 * mm,
        "CERTIFICATE ID",
    )

    pdf.setFillColor(navy)

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        card_x + 15 * mm,
        info_y + 4 * mm,
        certificate.certificate_id,
    )

    # Status

    status_x = card_x + 78 * mm

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica",
        6.5,
    )

    pdf.drawString(
        status_x,
        info_y + 8 * mm,
        "STATUS",
    )

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        status_x,
        info_y + 4 * mm,
        "VERIFIED",
    )

    # =====================================================
    # QR CODE PANEL
    # =====================================================

    qr_panel_x = (
        page_width
        - card_x
        - 39 * mm
    )

    qr_panel_y = card_y + 8 * mm

    pdf.setFillColor(
        colors.HexColor("#F8FAFC")
    )

    pdf.roundRect(
        qr_panel_x,
        qr_panel_y,
        31 * mm,
        29 * mm,
        3 * mm,
        fill=1,
        stroke=0,
    )

    # QR

    verification_url = build_verification_url(
        certificate.certificate_id
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )

    qr.add_data(verification_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    qr_buffer = BytesIO()

    qr_image.save(
        qr_buffer,
        format="PNG",
    )

    qr_buffer.seek(0)

    qr_size = 21 * mm

    qr_x = (
        qr_panel_x
        + (31 * mm - qr_size) / 2
    )

    qr_y = qr_panel_y + 6 * mm

    pdf.drawImage(
        ImageReader(qr_buffer),
        qr_x,
        qr_y,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.setFillColor(slate)

    pdf.setFont(
        "Helvetica-Bold",
        5.5,
    )

    pdf.drawCentredString(
        qr_panel_x + 15.5 * mm,
        qr_panel_y + 2.5 * mm,
        "SCAN TO VERIFY",
    )

    # =====================================================
    # FOOTER
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#94A3B8")
    )

    pdf.setFont(
        "Helvetica",
        5.5,
    )

    pdf.drawString(
        card_x + 10 * mm,
        card_y + 5.5 * mm,
        "Generated by CertiFlow",
    )

    pdf.drawRightString(
        page_width - card_x - 10 * mm,
        card_y + 5.5 * mm,
        "Authenticity can be verified through the QR code.",
    )

    # =====================================================
    # SAVE
    # =====================================================

    pdf.showPage()
    pdf.save()

    return str(
        output_path.relative_to(
            GENERATED_CERTIFICATES_DIR
        )
    )

