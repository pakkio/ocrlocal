from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

styles = getSampleStyleSheet()
corpo = ParagraphStyle("corpo", parent=styles["Normal"], fontSize=10.5, leading=15,
                       alignment=TA_JUSTIFY, spaceAfter=6)
did = ParagraphStyle("did", parent=styles["Normal"], fontSize=9,
                     alignment=TA_CENTER, textColor=colors.grey, spaceAfter=10)

doc = SimpleDocTemplate("test_reale.pdf", pagesize=A4,
                        leftMargin=2.5*cm, rightMargin=2.5*cm,
                        topMargin=2.5*cm, bottomMargin=2.5*cm)
story = []

story.append(Paragraph("Test con Immagine Reale da Internet", styles["Title"]))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph(
    "Il documento seguente contiene una fotografia reale scaricata da internet "
    "(non generata da AI) per testare la capacità del sistema di riconoscere e "
    "descrivere immagini generiche all'interno di un PDF.",
    corpo))

story.append(Image("test_photo.jpg", width=13*cm, height=9*cm))
story.append(Paragraph("Figura 1 — Fotografia reale: paesaggio costiero (Cinque Terre, Italia).", did))

story.append(Paragraph(
    "La fotografia mostra un paesaggio naturale. Il sistema di OCR estrae l'immagine "
    "dal PDF e il modello vision la descrive semanticamente, indipendentemente dal fatto "
    "che si tratti di un grafico scientifico o di una fotografia qualsiasi.",
    corpo))

doc.build(story)
print("PDF creato: test_reale.pdf")
