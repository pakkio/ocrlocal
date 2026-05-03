from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


def build():
    doc = SimpleDocTemplate(
        "solo_testo_italiano.pdf",
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()
    titolo = ParagraphStyle(
        "titolo",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    h1 = ParagraphStyle(
        "h1", parent=styles["Heading1"], fontSize=13, spaceBefore=14, spaceAfter=8
    )
    corpo = ParagraphStyle(
        "corpo",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    story = []

    # Titolo
    story.append(Paragraph("Guida alla Cura delle Piante Grasse", titolo))
    story.append(Spacer(1, 0.3 * cm))

    # Sezione 1
    story.append(Paragraph("Introduzione", h1))
    story.append(
        Paragraph(
            "Le piante grasse, conosciute anche come piante succulente, rappresentano una delle famiglie "
            "più affascinanti del regno vegetale. Originarie principalmente delle zone aride e semiaride "
            "del pianeta, queste piante hanno sviluppato nel corso dell'evoluzione meccanismi sorprendenti "
            "per la conservazione dell'acqua. Il loro habitat naturale comprende deserti, steppe e zone "
            "rocciose dove le precipitazioni sono scarse e irregolari.",
            corpo,
        )
    )
    story.append(
        Paragraph(
            "Il termine 'grassa' si riferisce alla consistenza delle foglie e dei fusti, che sono "
            "rigonfi di tessuti specializzati chiamati parenchimi acquiferi. Questi tessuti funzionano "
            "come veri e propri serbatoi, permettendo alla pianta di sopravvivere durante lunghi periodi "
            "di siccità. La cuticola cerosa che ricopre la superficie delle foglie riduce ulteriormente "
            "la traspirazione, rendendo queste piante estremamente resistenti.",
            corpo,
        )
    )

    # Sezione 2
    story.append(Paragraph("Annaffiatura e Esposizione", h1))
    story.append(
        Paragraph(
            "L'errore più comune nella coltivazione delle piante grasse è l'eccesso di annaffiatura. "
            "Contrariamente a quanto si potrebbe pensare, queste piante preferiscono ricevere meno acqua "
            "piuttosto che troppa. Durante la stagione primaverile ed estiva, quando la pianta è in "
            "fase vegetativa, è consigliabile annaffiare solo quando il terreno è completamente asciutto. "
            "In inverno, invece, la frequenza va ridotta drasticamente: una volta al mese è sufficiente.",
            corpo,
        )
    )
    story.append(
        Paragraph(
            "Per quanto riguarda l'esposizione luminosa, la maggior parte delle succulente richiede "
            "molta luce diretta. Posizionarle su un davanzale soleggiato a sud garantisce una crescita "
            "compatta e colorata. Tuttavia, occorre prestare attenzione nelle giornate più calde: un "
            "vetro che funge da lente può bruciare i tessuti. In caso di luce scarsa, le piante tendono "
            "ad allungarsi in cerca di luminosità, perdendo la loro forma caratteristica.",
            corpo,
        )
    )

    # Sezione 3
    story.append(Paragraph("Terreno e Rinvaso", h1))
    story.append(
        Paragraph(
            "Il substrato ideale per le piante grasse deve garantire un drenaggio eccellente. "
            "Una miscela che funziona sempre è composta da terra universale, sabbia grossolana "
            "e pomice in parti uguali. Questa combinazione permette all'acqua di defluire rapidamente, "
            "evitando i ristagni che causano il temuto marciume radicale. Il vaso deve sempre essere "
            "dotato di fori di drenaggio sul fondo.",
            corpo,
        )
    )
    story.append(
        Paragraph(
            "Il rinvaso si effettua generalmente in primavera, quando la pianta riprende la crescita. "
            "Non è necessario cambiare vaso ogni anno: solo quando le radici fuoriescono dai fori di "
            "drenaggio o quando la pianta sembra soffocare nel contenitore attuale. Dopo il rinvaso, "
            "è buona norma sospendere l'annaffiatura per circa una settimana per permettere alle radici "
            "di cicatrizzare eventuali ferite.",
            corpo,
        )
    )

    # Sezione 4
    story.append(Paragraph("Riproduzione", h1))
    story.append(
        Paragraph(
            "La moltiplicazione delle piante grasse è un'attività semplice e gratificante. "
            "Il metodo più comune è la talea: si stacca una foglia o una porzione di fusto "
            "e si lascia asciugare per alcuni giorni finché non si forma un callo sul taglio. "
            "Successivamente si poggia la talea sul terreno umido e in poche settimane si svilupperanno "
            "nuove radici e germogli.",
            corpo,
        )
    )

    # Sezione 5
    story.append(Paragraph("Conclusioni", h1))
    story.append(
        Paragraph(
            "Coltivare piante grasse è un hobby accessibile a tutti, anche a chi non possiede il pollice "
            "verde. La loro resistenza e la loro bellezza geometrica le rendono perfette per arredare "
            "casa e ufficio. Ricordando semplicemente di non annaffiare troppo spesso e di garantire "
            "abbastanza luce, queste piante ripagheranno con una crescita lenta ma costante, "
            "fioriture spettacolari e la soddisfazione di avere accanto un pezzo di deserto vivente.",
            corpo,
        )
    )

    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "<i>Testo generato per dimostrazione — Nessuna immagine, solo testo italiano.</i>",
            ParagraphStyle(
                "ref",
                parent=styles["Normal"],
                fontSize=8.5,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(story)
    print("PDF creato: solo_testo_italiano.pdf")


if __name__ == "__main__":
    build()
