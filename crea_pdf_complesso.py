from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    ListFlowable,
    ListItem,
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT


def build():
    doc = SimpleDocTemplate(
        "pdf_complesso_italiano.pdf",
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titolo = ParagraphStyle(
        "titolo",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=10,
        alignment=TA_CENTER,
    )
    sottotitolo = ParagraphStyle(
        "sottotitolo",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20,
    )
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Heading1"],
        fontSize=14,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.darkblue,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.steelblue,
    )
    corpo = ParagraphStyle(
        "corpo",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    caption = ParagraphStyle(
        "caption",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=4,
        spaceAfter=12,
    )
    nota = ParagraphStyle(
        "nota",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.darkred,
        spaceBefore=6,
        spaceAfter=6,
    )

    story = []

    # ===== PRIMA PAGINA: Titolo e Introduzione =====
    story.append(
        Paragraph("Rapporto Annuale sul Turismo Sostenibile in Italia", titolo)
    )
    story.append(
        Paragraph("Edizione 2024 — Ministero del Turismo e Ambiente", sottotitolo)
    )
    story.append(Spacer(1, 0.5 * cm))

    # Introduzione con testo lungo
    story.append(Paragraph("1. Panoramica Generale", h1))
    story.append(
        Paragraph(
            "Il presente rapporto analizza l'evoluzione del turismo sostenibile nel territorio italiano "
            "nel triennio 2021-2024. I dati raccolti evidenziano una crescita significativa del segmento "
            "del turismo ecologico, con un incremento del 23% rispetto al periodo pre-pandemico. "
            "Le destinazioni di montagna e le aree marine protette hanno registrato le performance migliori, "
            "con tassi di occupazione stagionali superiori alla media nazionale.",
            corpo,
        )
    )
    story.append(
        Paragraph(
            "L'analisi comparativa tra le diverse regioni italiane mette in luce disparità significative: "
            "il Nord-Est e le isole maggiori mostrano un livello di maturità superiore nell'offerta turistica "
            "sostenibile, mentre il Mezzogiorno presenta margini di crescita considerevoli ma anche "
            "maggiori criticità infrastrutturali.",
            corpo,
        )
    )

    # ===== TABELLA COMPLESSA 1: Dati regionali =====
    story.append(Paragraph("2. Dati Regionali Comparati", h1))
    story.append(
        Paragraph(
            "La Tabella 1 riporta gli indicatori chiave di performance per le principali regioni turistiche italiane.",
            corpo,
        )
    )

    dati_regionali = [
        [
            "Regione",
            "Arrivi 2023",
            "Presenze 2023",
            "Tasso Crescita",
            "Soddisfazione",
            "Emissioni CO₂/persona",
        ],
        ["Toscana", "12.450.000", "58.230.000", "+18.5%", "8.7/10", "125 kg"],
        ["Veneto", "15.890.000", "72.150.000", "+22.3%", "8.4/10", "98 kg"],
        ["Sicilia", "8.760.000", "42.180.000", "+31.2%", "8.9/10", "142 kg"],
        ["Lombardia", "11.230.000", "38.950.000", "+12.8%", "8.1/10", "156 kg"],
        ["Sardegna", "3.890.000", "28.670.000", "+28.7%", "9.1/10", "89 kg"],
        ["Puglia", "6.540.000", "31.420.000", "+35.4%", "8.6/10", "108 kg"],
        ["Trentino", "4.120.000", "22.850.000", "+15.2%", "9.0/10", "76 kg"],
    ]

    tabella1 = Table(
        dati_regionali,
        colWidths=[2.8 * cm, 2.4 * cm, 2.6 * cm, 2.2 * cm, 2.2 * cm, 2.8 * cm],
    )
    tabella1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4788")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#f0f4f8"), colors.white],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(tabella1)
    story.append(
        Paragraph(
            "Tabella 1 — Indicatori di performance turistica per regione (dati in migliaia).",
            caption,
        )
    )

    story.append(
        Paragraph(
            "I dati evidenziano come il Veneto mantenga la leadership assoluta in termini di volume, "
            "mentre la Puglia mostra il tasso di crescita più elevato (+35.4%). Particolarmente rilevante "
            "è il dato relativo alle emissioni di CO₂: le destinazioni montane (Trentino) e insulari (Sardegna) "
            "registrano valori significativamente inferiori rispetto alle metropoli.",
            corpo,
        )
    )

    # ===== SECONDA PAGINA: Immagine e altro testo =====
    story.append(PageBreak())
    story.append(Paragraph("3. Analisi delle Destinazioni", h1))

    # Prima immagine: paesaggio
    try:
        story.append(Image("img_paesaggio.jpg", width=14 * cm, height=9 * cm))
        story.append(
            Paragraph(
                "Figura 1 — Cinque Terre, Liguria: esempio di turismo costiero sostenibile.",
                caption,
            )
        )
    except:
        story.append(Paragraph("[Immagine: Paesaggio costiero Cinque Terre]", corpo))

    story.append(
        Paragraph(
            "Le aree costiere rappresentano un caso studio particolarmente interessante. La gestione "
            "del flusso turistico n località come le Cinque Terre ha richiesto l'implementazione di "
            "sistemi di prenotazione obbligatoria e limitazione degli accessi durante i periodi di picco. "
            "Queste misure, inizialmente controverse, hanno prodotto risultati positivi: riduzione del "
            "30% dei rifiuti abbandonati, miglioramento della qualità dell'aria e aumento della "
            "soddisfazione dei visitatori.",
            corpo,
        )
    )

    # ===== TERZA PAGINA: Tabelle complesse e grafici =====
    story.append(PageBreak())
    story.append(Paragraph("4. Stagionalità e Segmenti di Mercato", h1))

    story.append(Paragraph("4.1 Distribuzione stagionale", h2))

    # Tabella stagionale complessa
    dati_stagionali = [
        [
            "Periodo",
            "Escursionisti",
            "Culturali",
            "Balneari",
            "Enogastronomici",
            "Totale",
        ],
        ["Gen-Mar", "2.1M", "1.8M", "0.3M", "0.9M", "5.1M"],
        ["Apr-Giu", "4.2M", "3.5M", "1.2M", "2.1M", "11.0M"],
        ["Lug-Ago", "3.8M", "2.9M", "8.7M", "3.4M", "18.8M"],
        ["Set-Nov", "3.5M", "4.2M", "2.1M", "2.8M", "12.6M"],
        ["Dic", "1.2M", "2.8M", "0.1M", "1.9M", "6.0M"],
        ["TOTALE", "14.8M", "15.2M", "12.4M", "11.1M", "53.5M"],
    ]

    tabella2 = Table(dati_stagionali, colWidths=[2.2 * cm] + [2.6 * cm] * 5)
    tabella2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d5d31")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -2),
                    [colors.HexColor("#e8f5e9"), colors.white],
                ),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#c8e6c9")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(tabella2)
    story.append(
        Paragraph(
            "Tabella 2 — Distribuzione dei turisti per segmento e periodo stagionale (2023).",
            caption,
        )
    )

    story.append(Paragraph("4.2 Andamento trend", h2))

    # Seconda immagine: grafico
    try:
        story.append(Image("img_grafico.png", width=10 * cm, height=10 * cm))
        story.append(
            Paragraph(
                "Figura 2 — Distribuzione statistica delle recensioni turistiche (media 4.2/5).",
                caption,
            )
        )
    except:
        story.append(
            Paragraph("[Grafico: Distribuzione normalizzata delle valutazioni]", corpo)
        )

    # ===== QUARTA PAGINA: Architettura e conclusioni =====
    story.append(PageBreak())
    story.append(Paragraph("5. Il Patrimonio Architettonico", h1))

    try:
        story.append(Image("img_architettura.jpg", width=13 * cm, height=8 * cm))
        story.append(
            Paragraph(
                "Figura 3 — Venezia: gestione della frequentazione nei siti UNESCO.",
                caption,
            )
        )
    except:
        story.append(Paragraph("[Immagine: Vista architettonica di Venezia]", corpo))

    story.append(
        Paragraph(
            "I centri storici delle città d'arte italiane affrontano sfide uniche. Venezia, con i suoi "
            "20 milioni di visitatori annui, ha implementato il sistema di prenotazione per l'accesso "
            "alla città storica. Il contributo di accesso (5€) ha generato nel 2023 oltre 12 milioni di euro, "
            "interamente reinvestiti nella manutenzione del patrimonio.",
            corpo,
        )
    )

    story.append(
        Paragraph(
            "L'analisi dei flussi evidenzia una concentrazione critica durante i weekend di primavera "
            "e i ponti festivi. Il rapporto tra residenti e turisti in certe ore del giorno supera 1:50, "
            "creando tensioni sociali e problemi di vivibilità. Le soluzioni proposte includono: "
            "decentralizzazione degli attracchi delle navi da crociera, promozione del turismo "
            "fuori stagione, e sviluppo di itinerari alternativi nei quartieri meno conosciuti.",
            corpo,
        )
    )

    # Tabella finale con costi/benefici
    story.append(Paragraph("6. Analisi Costi-Benefici", h1))
    story.append(
        Paragraph(
            "La Tabella 3 sintetizza l'analisi economica delle principali politiche di gestione "
            "della domanda turistica attuate nel 2023.",
            corpo,
        )
    )

    dati_costi = [
        [
            "Misura",
            "Costo Implementazione",
            "Entrate Generate",
            "ROI",
            "Impatto Ambientale",
        ],
        [
            "Prenotazione obbligatoria Cinque Terre",
            "€ 450.000",
            "€ 1.200.000",
            "+167%",
            "-28% rifiuti",
        ],
        [
            "Contributo accesso Venezia",
            "€ 890.000",
            "€ 12.400.000",
            "+1292%",
            "-15% congestione",
        ],
        ["ZTL estiva Firenze", "€ 230.000", "€ 3.800.000", "+1552%", "-22% emissioni"],
        [
            "Tassa soggiorno incrementata",
            "€ 120.000",
            "€ 45.000.000",
            "+37400%",
            "Neutro",
        ],
        [
            "App ricerca carico-diffuso",
            "€ 680.000",
            "€ 450.000",
            "-34%",
            "+18% dispersione",
        ],
    ]

    tabella3 = Table(dati_costi, colWidths=[4.5 * cm, 3 * cm, 3 * cm, 2 * cm, 3.5 * cm])
    tabella3.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7b1fa2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#f3e5f5"), colors.white],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(tabella3)
    story.append(
        Paragraph(
            "Tabella 3 — Analisi costi-benefici delle politiche di gestione turistica (2023).",
            caption,
        )
    )

    # Note finali
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "<b>Nota metodologica:</b> I dati sono stati raccolti attraverso rilevazioni campionarie "
            "presso strutture ricettive, interviste ai visitatori e analisi dei big data derivanti dai "
            "sistemi di prenotazione online. L'errore campionario stimato è del ±2.3% al 95% di confidenza.",
            nota,
        )
    )

    story.append(Spacer(1, 0.8 * cm))
    story.append(
        Paragraph(
            "<i>Rapporto realizzato dal Dipartimento per il Turismo — Ministero del Turismo e della "
            "Navigazione. Ultimo aggiornamento: dicembre 2024.</i>",
            ParagraphStyle(
                "footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(story)
    print("PDF complesso creato: pdf_complesso_italiano.pdf")
    print("Pagine: 4 | Tabelle: 3 | Immagini: 3")


if __name__ == "__main__":
    build()
