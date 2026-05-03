from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

def build():
    doc = SimpleDocTemplate(
        "test_italiano.pdf",
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )

    styles = getSampleStyleSheet()
    titolo = ParagraphStyle("titolo", parent=styles["Title"], fontSize=18, spaceAfter=6, alignment=TA_CENTER)
    autore = ParagraphStyle("autore", parent=styles["Normal"], fontSize=11, spaceAfter=2, alignment=TA_CENTER, textColor=colors.grey)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, spaceBefore=14, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=3)
    corpo = ParagraphStyle("corpo", parent=styles["Normal"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
    formula = ParagraphStyle("formula", parent=styles["Normal"], fontSize=10.5, leading=15, alignment=TA_CENTER, spaceAfter=6, fontName="Courier")
    didascalia = ParagraphStyle("didascalia", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=8)

    story = []

    # Titolo
    story.append(Paragraph("Analisi dei Sistemi Dinamici Lineari<br/>con Applicazioni al Controllo Automatico", titolo))
    story.append(Paragraph("Prof. Marco Ferretti &mdash; Dipartimento di Ingegneria dell'Informazione", autore))
    story.append(Paragraph("Università degli Studi di Milano &mdash; A.A. 2024/2025", autore))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    story.append(Spacer(1, 0.3*cm))

    # Abstract
    story.append(Paragraph("Abstract", h1))
    story.append(Paragraph(
        "Il presente documento introduce i fondamenti matematici dei sistemi dinamici lineari "
        "tempo-invarianti (LTI), con particolare attenzione alla rappresentazione nello spazio di "
        "stato e all'analisi della stabilità mediante il criterio di Routh-Hurwitz. Vengono illustrati "
        "esempi applicativi nel contesto del controllo automatico industriale, con riferimento a "
        "sistemi del secondo ordine e alla loro risposta al gradino. I risultati numerici sono "
        "sintetizzati in tabelle comparative e le formule chiave sono esposte in forma esplicita.",
        corpo
    ))

    # Sezione 1
    story.append(Paragraph("1. Rappresentazione nello Spazio di Stato", h1))
    story.append(Paragraph(
        "Un sistema dinamico lineare tempo-invariante può essere descritto dal seguente sistema "
        "di equazioni differenziali del primo ordine:", corpo
    ))
    story.append(Paragraph("ẋ(t) = A x(t) + B u(t)", formula))
    story.append(Paragraph("y(t) = C x(t) + D u(t)", formula))
    story.append(Paragraph(
        "dove <b>x(t) ∈ ℝⁿ</b> è il vettore di stato, <b>u(t) ∈ ℝᵐ</b> è il vettore degli ingressi, "
        "<b>y(t) ∈ ℝᵖ</b> è il vettore delle uscite. Le matrici <b>A</b>, <b>B</b>, <b>C</b>, <b>D</b> "
        "caratterizzano completamente la struttura del sistema.",
        corpo
    ))

    story.append(Paragraph("1.1 Soluzione dell'equazione di stato", h2))
    story.append(Paragraph(
        "La soluzione dell'equazione di stato, noti lo stato iniziale x(0) e l'ingresso u(t), è data da:",
        corpo
    ))
    story.append(Paragraph("x(t) = e^(At) x(0) + ∫₀ᵗ e^(A(t-τ)) B u(τ) dτ", formula))
    story.append(Paragraph(
        "Il termine <b>e^(At)</b> è detto <i>matrice di transizione dello stato</i> o <i>esponenziale di matrice</i>. "
        "Quando A è diagonalizzabile, essa si calcola efficientemente tramite la decomposizione spettrale "
        "A = V Λ V⁻¹, che conduce a e^(At) = V e^(Λt) V⁻¹.",
        corpo
    ))

    # Sezione 2
    story.append(Paragraph("2. Analisi della Stabilità", h1))
    story.append(Paragraph(
        "Un sistema LTI è <b>asintoticamente stabile</b> se e solo se tutti gli autovalori della "
        "matrice A hanno parte reale strettamente negativa, ovvero:",
        corpo
    ))
    story.append(Paragraph("Re(λᵢ) < 0,   ∀i = 1, ..., n", formula))
    story.append(Paragraph(
        "Il <b>criterio di Routh-Hurwitz</b> consente di verificare questa condizione "
        "senza calcolare esplicitamente gli autovalori, analizzando i coefficienti del "
        "polinomio caratteristico det(λI - A).",
        corpo
    ))

    story.append(Paragraph("2.1 Sistema del secondo ordine", h2))
    story.append(Paragraph(
        "Per un sistema del secondo ordine con funzione di trasferimento standard:",
        corpo
    ))
    story.append(Paragraph("G(s) = ωₙ² / (s² + 2ζωₙs + ωₙ²)", formula))
    story.append(Paragraph(
        "i parametri caratteristici sono: <b>ωₙ</b> = pulsazione naturale [rad/s], "
        "<b>ζ</b> = coefficiente di smorzamento (adimensionale). "
        "Il sistema è stabile per ζ &gt; 0 e ωₙ &gt; 0. "
        "Il tempo di assestamento al 2% vale approssimativamente t_s ≈ 4/(ζωₙ).",
        corpo
    ))

    # Tabella
    story.append(Paragraph("3. Confronto Parametrico — Risposta al Gradino", h1))
    story.append(Paragraph(
        "La tabella seguente riassume le prestazioni nel dominio del tempo al variare del "
        "coefficiente di smorzamento ζ, con ωₙ = 10 rad/s fissato.",
        corpo
    ))

    dati = [
        ["ζ", "Tipo risposta", "Sovraelongazione (%)", "t_r (s)", "t_s (s)"],
        ["0.1", "Sottosmorzato", "73.0", "0.18", "3.95"],
        ["0.3", "Sottosmorzato", "37.2", "0.22", "1.32"],
        ["0.5", "Sottosmorzato", "16.3", "0.28", "0.81"],
        ["0.7", "Sottosmorzato", "4.6",  "0.35", "0.58"],
        ["1.0", "Criticamente smorzato", "0.0", "0.48", "0.46"],
        ["1.5", "Sovrasmorzato", "0.0", "0.72", "0.68"],
        ["2.0", "Sovrasmorzato", "0.0", "1.05", "0.99"],
    ]
    t = Table(dati, colWidths=[1.5*cm, 4.8*cm, 4.2*cm, 2.2*cm, 2.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 9),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE",     (0,1), (-1,-1), 9),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Paragraph("Tabella 1 — Prestazioni nel dominio del tempo, ωₙ = 10 rad/s.", didascalia))

    # Sezione 4
    story.append(Paragraph("4. Criterio di Routh-Hurwitz — Esempio", h1))
    story.append(Paragraph(
        "Dato il polinomio caratteristico di terzo grado:",
        corpo
    ))
    story.append(Paragraph("p(s) = s³ + 6s² + 11s + 6", formula))
    story.append(Paragraph("La tavola di Routh si costruisce come segue:", corpo))

    routh = [
        ["Riga", "Colonna 1", "Colonna 2"],
        ["s³", "1", "11"],
        ["s²", "6", "6"],
        ["s¹", "(6·11 - 1·6)/6 = 10", "0"],
        ["s⁰", "6", "—"],
    ]
    tr = Table(routh, colWidths=[2.5*cm, 6*cm, 4*cm])
    tr.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), colors.steelblue),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.lightblue, colors.white]),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    story.append(tr)
    story.append(Paragraph("Tabella 2 — Tavola di Routh per p(s) = s³ + 6s² + 11s + 6.", didascalia))
    story.append(Paragraph(
        "Tutti gli elementi della prima colonna sono positivi (1, 6, 10, 6), pertanto "
        "il sistema è <b>asintoticamente stabile</b>. Gli zeri del polinomio sono "
        "s₁ = −1, s₂ = −2, s₃ = −3, tutti con parte reale negativa.",
        corpo
    ))

    # Conclusioni
    story.append(Paragraph("5. Conclusioni", h1))
    story.append(Paragraph(
        "La rappresentazione nello spazio di stato fornisce uno strumento unificante per "
        "l'analisi e la sintesi dei sistemi di controllo. La stabilità asintotica, "
        "verificabile sia tramite gli autovalori di A sia con il criterio algebrico di "
        "Routh-Hurwitz, costituisce il requisito fondamentale per qualsiasi applicazione "
        "pratica. I risultati riportati in Tabella 1 evidenziano come il coefficiente di "
        "smorzamento ζ influenzi significativamente le prestazioni transitorie: valori "
        "compresi tra 0.5 e 0.8 rappresentano tipicamente il miglior compromesso tra "
        "velocità di risposta e sovraelongazione accettabile.",
        corpo
    ))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<i>Riferimenti: Ogata K., Modern Control Engineering, 5ª ed., Prentice Hall, 2010. "
        "Franklin G.F., Powell J.D., Emami-Naeini A., Feedback Control of Dynamic Systems, 8ª ed., Pearson, 2019.</i>",
        ParagraphStyle("ref", parent=styles["Normal"], fontSize=8.5, textColor=colors.grey, alignment=TA_LEFT)
    ))

    doc.build(story)
    print("PDF creato: test_italiano.pdf")

if __name__ == "__main__":
    build()
