"""
ArthRakshak — PDF Generator Backend
Generates official government-grade PDF reports for schemes and departments.
Uses reportlab if available, falls back to raw PDF bytes if not.
"""

import io
import os
import math
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable, PageBreak)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB = True
except ImportError:
    REPORTLAB = False


# ── Colors ────────────────────────────────────────────────────────────
NAVY    = (0, 33, 71)
SAFFRON = (232, 93, 0)
WHITE   = (255, 255, 255)
GREY    = (247, 249, 252)
TEXT    = (15, 23, 42)
MUTED   = (100, 116, 139)


def generate_scheme_pdf(scheme: dict, user: dict) -> bytes:
    """Generate a detailed PDF for a single scheme."""
    if REPORTLAB:
        return _rl_scheme_pdf(scheme, user)
    return _simple_scheme_pdf(scheme, user)


def generate_department_report(schemes: list, user: dict,
                                 report_type: str = "full",
                                 period: str = "FY 2025-26") -> bytes:
    """Generate a full department report PDF."""
    if REPORTLAB:
        return _rl_department_pdf(schemes, user, report_type, period)
    return _simple_department_pdf(schemes, user, report_type, period)


def generate_risk_report(schemes: list, user: dict) -> bytes:
    """Generate a risk-focused PDF report."""
    from risk_score import score_all_schemes
    scored = score_all_schemes(schemes)
    if REPORTLAB:
        return _rl_risk_pdf(scored, user)
    return _simple_risk_pdf(scored, user)


def generate_anomaly_report(schemes: list, user: dict) -> bytes:
    """Generate anomaly detection PDF report."""
    from anomaly_detection import get_anomaly_summary
    summary = get_anomaly_summary(schemes)
    if REPORTLAB:
        return _rl_anomaly_pdf(summary, user)
    return _simple_anomaly_pdf(summary, user)


# ── ReportLab PDF builders ────────────────────────────────────────────
def _rl_scheme_pdf(scheme: dict, user: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=18*mm, rightMargin=18*mm,
                             topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story  = []

    navy_c = colors.HexColor('#002147')
    saff_c = colors.HexColor('#e85d00')
    grey_c = colors.HexColor('#f7f9fc')

    # Title block
    story.append(Paragraph(
        f'<font color="#e85d00">ArthRakshak</font> — Scheme Intelligence Report',
        ParagraphStyle('title', parent=styles['Title'], fontSize=20, spaceAfter=4,
                       fontName='Helvetica-Bold', textColor=navy_c)))
    story.append(Paragraph(
        f'National Budget Intelligence Platform | Confidential',
        ParagraphStyle('sub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=12)))
    story.append(HRFlowable(width='100%', thickness=2, color=navy_c))
    story.append(Spacer(1, 10))

    # Scheme name
    story.append(Paragraph(scheme.get('name','—'),
        ParagraphStyle('schname', parent=styles['Heading1'], fontSize=16, textColor=navy_c, spaceAfter=6)))

    # Meta row
    risk = scheme.get('riskScore', 0)
    risk_lv = 'Low' if risk<30 else 'Medium' if risk<55 else 'High' if risk<75 else 'Critical'
    meta_data = [
        ['Field', 'Value', 'Field', 'Value'],
        ['Sector',         scheme.get('sector','—'),    'Utilization',   f"{scheme.get('utilization',0)}%"],
        ['Risk Score',     f"{risk}/100",               'Risk Level',    risk_lv],
        ['Budget',         scheme.get('budget','—'),    'Utilized',      scheme.get('utilized', scheme.get('distributed','—'))],
        ['Ministry',       scheme.get('ministry', user.get('dept','—')), 'Beneficiaries', scheme.get('beneficiaries','—')],
        ['Launch Year',    str(scheme.get('year','—')), 'State/District',scheme.get('state', scheme.get('district','National'))],
    ]
    t = Table(meta_data, colWidths=[40*mm, 55*mm, 40*mm, 40*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy_c),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,-1), grey_c),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [grey_c, colors.white]),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (2,1), (2,-1), 'Helvetica-Bold'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#d0dae8')),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Description
    desc = scheme.get('desc') or scheme.get('purpose','—')
    if desc and desc != '—':
        story.append(Paragraph('About This Scheme',
            ParagraphStyle('h2', parent=styles['Heading2'], textColor=navy_c, fontSize=12, spaceAfter=4)))
        story.append(Paragraph(desc, ParagraphStyle('body', parent=styles['Normal'], fontSize=10, leading=16,
                                                      textColor=colors.HexColor('#334155'))))
        story.append(Spacer(1, 10))

    # Utilization bar (text representation)
    util = scheme.get('utilization', 0)
    bar_filled = '█' * int(util / 5)
    bar_empty  = '░' * (20 - int(util / 5))
    story.append(Paragraph('Budget Utilization',
        ParagraphStyle('h2', parent=styles['Heading2'], textColor=navy_c, fontSize=12, spaceAfter=4)))
    story.append(Paragraph(
        f'<font face="Courier">{bar_filled}{bar_empty}</font>  <b>{util}%</b>',
        ParagraphStyle('bar', parent=styles['Normal'], fontSize=11)))
    story.append(Spacer(1, 10))

    # Footer
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f'Generated by: {user.get("name","—")} | {user.get("dept","—")} | {datetime.now().strftime("%d %b %Y %H:%M")} | CONFIDENTIAL',
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))

    doc.build(story)
    return buf.getvalue()


def _rl_department_pdf(schemes: list, user: dict, report_type: str, period: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=18*mm, rightMargin=18*mm,
                             topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story  = []
    navy_c = colors.HexColor('#002147')
    saff_c = colors.HexColor('#e85d00')
    grey_c = colors.HexColor('#f7f9fc')

    TYPE_LABELS = {
        "utilization": "Budget Utilization Summary",
        "performance": "Scheme Performance Report",
        "risk":        "Risk Assessment Report",
        "anomaly":     "Anomaly Detection Report",
        "full":        "Full Department Overview",
    }

    # Cover
    story.append(Spacer(1, 10))
    story.append(Paragraph('🏛️ ArthRakshak',
        ParagraphStyle('cover1', parent=styles['Title'], fontSize=26, textColor=navy_c,
                       fontName='Helvetica-Bold', alignment=TA_CENTER)))
    story.append(Paragraph('National Budget Intelligence Platform',
        ParagraphStyle('cover2', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=6)))
    story.append(HRFlowable(width='100%', thickness=3, color=saff_c))
    story.append(Spacer(1, 10))
    story.append(Paragraph(TYPE_LABELS.get(report_type, "Report"),
        ParagraphStyle('reptype', parent=styles['Heading1'], fontSize=18, textColor=navy_c, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph(f'{user.get("dept","—")}  ·  {period}',
        ParagraphStyle('repinfo', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph(f'Generated: {datetime.now().strftime("%d %B %Y")}  ·  Official Use Only',
        ParagraphStyle('repdate', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))
    story.append(Spacer(1, 20))

    # Stats row
    avg_u   = round(sum(s.get("utilization",0) for s in schemes) / len(schemes)) if schemes else 0
    avg_r   = round(sum(s.get("riskScore",0) for s in schemes) / len(schemes)) if schemes else 0
    high_r  = len([s for s in schemes if s.get("riskScore",0) >= 55])
    stats_d = [['Total Schemes', 'Avg Utilization', 'Avg Risk Score', 'High Risk'],
               [str(len(schemes)), f'{avg_u}%', f'{avg_r}/100', str(high_r)]]
    st = Table(stats_d, colWidths=[42*mm, 42*mm, 42*mm, 42*mm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy_c), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,1), (-1,1), grey_c), ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 16), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0dae8')),
    ]))
    story.append(st)
    story.append(Spacer(1, 16))

    # Scheme table
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 8))
    story.append(Paragraph('Scheme-wise Data',
        ParagraphStyle('h2', parent=styles['Heading2'], textColor=navy_c, fontSize=13, spaceAfter=8)))

    tdata = [['#', 'Scheme Name', 'Sector', 'Utilization', 'Risk', 'Level']]
    for i, s in enumerate(schemes):
        risk = s.get("riskScore", 0)
        lv = 'Low' if risk<30 else 'Med' if risk<55 else 'High' if risk<75 else 'Crit'
        tdata.append([
            str(i+1),
            s.get("name","—")[:35],
            s.get("sector","—")[:15],
            f"{s.get('utilization',0)}%",
            str(risk),
            lv,
        ])
    col_widths = [10*mm, 68*mm, 28*mm, 22*mm, 16*mm, 16*mm]
    st2 = Table(tdata, colWidths=col_widths, repeatRows=1)
    st2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy_c), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [grey_c, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0dae8')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(st2)
    story.append(Spacer(1, 16))

    # Recommendations
    story.append(Paragraph('Recommendations',
        ParagraphStyle('h2', parent=styles['Heading2'], textColor=navy_c, fontSize=13, spaceAfter=8)))
    recs = []
    if high_r > 0:
        recs.append(f'Initiate investigation into {high_r} high-risk scheme(s) with risk scores above 55.')
    if avg_u < 50:
        recs.append(f'Average utilization of {avg_u}% is below target. Review disbursement bottlenecks.')
    recs.append('Conduct quarterly beneficiary verification to prevent duplicate entries.')
    recs.append('Submit Utilization Certificates within 30 days of quarter close per GFR guidelines.')
    recs.append('Implement real-time fund tracking via PFMS for schemes above ₹100 Cr.')
    for i, rec in enumerate(recs, 1):
        story.append(Paragraph(f'{i}. {rec}',
            ParagraphStyle('rec', parent=styles['Normal'], fontSize=9, leading=14,
                           textColor=colors.HexColor('#334155'), spaceAfter=4)))

    # Footer on each page handled by onFirstPage/onLaterPages
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph(
        f'ArthRakshak — Confidential Government Document | '
        f'Report ID: AR-{datetime.now().strftime("%Y%m%d%H%M")} | '
        f'Generated by: {user.get("name","—")}',
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=7,
                       textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))
    doc.build(story)
    return buf.getvalue()


def _rl_risk_pdf(scored: list, user: dict) -> bytes:
    return _rl_department_pdf(scored, user, "risk", "Current Assessment")


def _rl_anomaly_pdf(summary: dict, user: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                             topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    navy_c = colors.HexColor('#002147')

    story.append(Paragraph('ArthRakshak — Anomaly Detection Report',
        ParagraphStyle('title', parent=styles['Title'], fontSize=18, textColor=navy_c, spaceAfter=4)))
    story.append(Paragraph(
        f'{user.get("dept","—")} | {datetime.now().strftime("%d %B %Y")} | CONFIDENTIAL',
        ParagraphStyle('sub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=12)))
    story.append(HRFlowable(width='100%', thickness=2, color=navy_c))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f'Total Anomalies: {summary["total_anomalies"]}  |  At Risk: ₹{summary["total_at_risk_cr"]} Cr  |  Critical: {summary["distribution"].get("critical",0)}',
        ParagraphStyle('stats', parent=styles['Normal'], fontSize=11, textColor=navy_c, spaceAfter=12)))

    if summary["anomalies"]:
        tdata = [['Severity', 'Scheme', 'Type', 'Amount (Cr)', 'Action']]
        for a in summary["anomalies"]:
            tdata.append([
                a['severity'].upper(), a['scheme_name'][:28], a['anomaly_type'][:20],
                f"₹{a['amount_cr']}", a['recommendation'][:30]+'…' if len(a.get('recommendation',''))>30 else a.get('recommendation','')
            ])
        t = Table(tdata, colWidths=[22*mm, 52*mm, 38*mm, 22*mm, 40*mm], repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy_c), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f7f9fc'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0dae8')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)

    doc.build(story)
    return buf.getvalue()


# ── Fallback plain-text PDF (no reportlab) ───────────────────────────
def _simple_scheme_pdf(scheme: dict, user: dict) -> bytes:
    """Generate minimal PDF manually without reportlab."""
    lines = [
        "ArthRakshak — Scheme Intelligence Report",
        "=" * 50,
        f"Scheme: {scheme.get('name','—')}",
        f"Sector: {scheme.get('sector','—')}",
        f"Utilization: {scheme.get('utilization',0)}%",
        f"Risk Score: {scheme.get('riskScore',0)}/100",
        f"Budget: {scheme.get('budget','—')}",
        f"Generated by: {user.get('name','—')} | {user.get('dept','—')}",
        f"Date: {datetime.now().strftime('%d %B %Y')}",
        "",
        "CONFIDENTIAL — Government Use Only",
    ]
    text = "\n".join(lines)
    # Minimal valid PDF structure
    pdf = _make_minimal_pdf(text)
    return pdf.encode()


def _simple_department_pdf(schemes: list, user: dict, rtype: str, period: str) -> bytes:
    lines = [
        "ArthRakshak — Department Report",
        "=" * 50,
        f"Department: {user.get('dept','—')}",
        f"Period: {period}",
        f"Total Schemes: {len(schemes)}",
        f"Avg Utilization: {round(sum(s.get('utilization',0) for s in schemes)/len(schemes))}%" if schemes else "N/A",
        "",
        "Schemes:",
    ]
    for i, s in enumerate(schemes, 1):
        lines.append(f"{i:2}. {s.get('name','—')[:40]:40} | Util: {s.get('utilization',0):3}% | Risk: {s.get('riskScore',0):3}")
    lines += ["", f"Generated: {datetime.now().strftime('%d %B %Y')}", "CONFIDENTIAL"]
    return _make_minimal_pdf("\n".join(lines)).encode()


def _simple_risk_pdf(scored: list, user: dict) -> bytes:
    lines = ["ArthRakshak — Risk Report", "=" * 50]
    for s in scored:
        lines.append(f"{s.get('scheme_name','—')[:35]:35} | {s.get('score',0):3}/100 | {s.get('level','—').upper()}")
    lines.append(f"\nGenerated: {datetime.now().strftime('%d %B %Y')} | CONFIDENTIAL")
    return _make_minimal_pdf("\n".join(lines)).encode()


def _simple_anomaly_pdf(summary: dict, user: dict) -> bytes:
    lines = ["ArthRakshak — Anomaly Report", "=" * 50,
             f"Total: {summary['total_anomalies']} | At Risk: ₹{summary['total_at_risk_cr']} Cr", ""]
    for a in summary.get("anomalies", []):
        lines.append(f"[{a['severity'].upper():8}] {a['scheme_name'][:30]:30} | {a['anomaly_type']}")
    lines.append(f"\nGenerated: {datetime.now().strftime('%d %B %Y')} | CONFIDENTIAL")
    return _make_minimal_pdf("\n".join(lines)).encode()


def _make_minimal_pdf(text: str) -> str:
    """Build a bare-minimum valid PDF with given text content."""
    lines = text.split("\n")
    stream_lines = []
    y = 750
    stream_lines.append("BT")
    stream_lines.append("/F1 10 Tf")
    for line in lines:
        safe = line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
        stream_lines.append(f"50 {y} Td ({safe}) Tj")
        y -= 14
        if y < 50:
            break
    stream_lines.append("ET")
    stream = "\n".join(stream_lines)
    stream_bytes = stream.encode('latin-1', errors='replace')

    obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj"
    obj2 = "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj"
    obj3 = f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj"
    obj4 = f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n{stream}\nendstream\nendobj"
    obj5 = "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj"

    body = f"%PDF-1.4\n{obj1}\n{obj2}\n{obj3}\n{obj4}\n{obj5}\n"
    xref_pos = len(body)
    body += "xref\n0 6\n0000000000 65535 f \n"
    body += "trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
    body += f"{xref_pos}\n%%EOF"
    return body


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_user = {"name": "Anil Kumar", "dept": "Finance Ministry"}
    test_scheme = {"id":"n1","name":"PM-KISAN","sector":"Agriculture","utilization":91,"riskScore":22,
                   "budget":"₹60,000 Cr","distributed":"₹80,000 Cr total","beneficiaries":"11.4 Cr farmers",
                   "year":2019,"ministry":"Ministry of Agriculture","desc":"Direct income support of ₹6,000/year."}
    test_schemes = [test_scheme,
                    {"id":"n4","name":"MGNREGA","sector":"Employment","utilization":55,"riskScore":57,"budget":"₹60,000 Cr"},
                    {"id":"n8","name":"Beti Bachao Beti Padhao","sector":"Social Welfare","utilization":25,"riskScore":68,"budget":"₹2,000 Cr"}]

    if REPORTLAB:
        print("✅ ReportLab available — generating full PDF")
        pdf = generate_scheme_pdf(test_scheme, test_user)
        with open("/tmp/test_scheme.pdf","wb") as f: f.write(pdf)
        print(f"Scheme PDF: {len(pdf)} bytes → /tmp/test_scheme.pdf")

        pdf2 = generate_department_report(test_schemes, test_user, "full", "FY 2025-26")
        with open("/tmp/test_dept.pdf","wb") as f: f.write(pdf2)
        print(f"Dept PDF: {len(pdf2)} bytes → /tmp/test_dept.pdf")
    else:
        print("⚠️ ReportLab not installed — using minimal PDF fallback")
        print("Install: pip install reportlab")
        pdf = generate_scheme_pdf(test_scheme, test_user)
        print(f"Fallback PDF: {len(pdf)} bytes")