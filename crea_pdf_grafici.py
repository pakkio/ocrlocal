import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


def make_step_response_chart():
    fig, ax = plt.subplots(figsize=(7, 3.5))
    t = np.linspace(0, 5, 500)
    wn = 10
    configs = [
        (0.2, "ζ=0.2 (sottosmorzato)", "tab:red"),
        (0.7, "ζ=0.7 (ottimale)",       "tab:green"),
        (1.0, "ζ=1.0 (critico)",         "tab:blue"),
        (2.0, "ζ=2.0 (sovrasmorzato)",   "tab:orange"),
    ]
    for zeta, label, color in configs:
        wd = wn * np.sqrt(abs(1 - zeta**2)) if zeta < 1 else 0
        if zeta < 1:
            y = 1 - np.exp(-zeta*wn*t) * (np.cos(wd*t) + (zeta/np.sqrt(1-zeta**2))*np.sin(wd*t))
        elif zeta == 1:
            y = 1 - np.exp(-wn*t) * (1 + wn*t)
        else:
            r1 = -wn*(zeta - np.sqrt(zeta**2-1))
            r2 = -wn*(zeta + np.sqrt(zeta**2-1))
            y = 1 + (r2/(r1-r2))*np.exp(r1*t) - (r1/(r1-r2))*np.exp(r2*t)
        ax.plot(t, y, label=label, color=color, linewidth=1.8)

    ax.axhline(1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.axhline(1.02, color="gray", linestyle=":", linewidth=0.7)
    ax.axhline(0.98, color="gray", linestyle=":", linewidth=0.7)
    ax.fill_between(t, 0.98, 1.02, alpha=0.07, color="gray")
    ax.set_xlabel("Tempo [s]", fontsize=10)
    ax.set_ylabel("y(t)", fontsize=10)
    ax.set_title("Risposta al gradino — sistema del 2° ordine (ωₙ = 10 rad/s)", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0, 5)
    ax.set_ylim(-0.1, 1.6)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def make_poles_chart():
    fig, ax = plt.subplots(figsize=(5, 4))
    wn = 10
    zetas = [0.2, 0.5, 0.7, 1.0, 1.5]
    colors_list = ["tab:red", "tab:purple", "tab:green", "tab:blue", "tab:orange"]

    for zeta, color in zip(zetas, colors_list):
        if zeta < 1:
            re = -zeta * wn
            im = wn * np.sqrt(1 - zeta**2)
            ax.plot(re, im, "o", color=color, markersize=8, label=f"ζ={zeta}")
            ax.plot(re, -im, "o", color=color, markersize=8)
            ax.plot([0, re], [0, im], "--", color=color, alpha=0.4, linewidth=0.8)
            ax.plot([0, re], [0, -im], "--", color=color, alpha=0.4, linewidth=0.8)
        else:
            r1 = -wn*(zeta - np.sqrt(zeta**2-1)) if zeta > 1 else -wn
            r2 = -wn*(zeta + np.sqrt(zeta**2-1)) if zeta > 1 else -wn
            ax.plot(r1, 0, "s", color=color, markersize=8, label=f"ζ={zeta}")
            if zeta > 1:
                ax.plot(r2, 0, "s", color=color, markersize=8)

    ax.axvline(0, color="black", linewidth=1.2)
    ax.axhline(0, color="black", linewidth=1.2)
    ax.set_xlabel("Re(s)", fontsize=10)
    ax.set_ylabel("Im(s)", fontsize=10)
    ax.set_title("Piano dei poli — variazione di ζ (ωₙ = 10)", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-25, 5)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def build():
    styles = getSampleStyleSheet()
    corpo = ParagraphStyle("corpo", parent=styles["Normal"], fontSize=10.5, leading=15,
                           alignment=TA_JUSTIFY, spaceAfter=6)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, spaceBefore=14, spaceAfter=4)
    didascalia = ParagraphStyle("did", parent=styles["Normal"], fontSize=9,
                                alignment=TA_CENTER, textColor=colors.grey, spaceAfter=10)

    doc = SimpleDocTemplate("test_grafici.pdf", pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    story = []

    story.append(Paragraph("Analisi Grafica dei Sistemi del 2° Ordine", styles["Title"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1. Risposta al Gradino", h1))
    story.append(Paragraph(
        "Il grafico seguente mostra la risposta al gradino unitario per quattro valori del coefficiente "
        "di smorzamento ζ, con pulsazione naturale ωₙ = 10 rad/s. La banda tratteggiata grigia indica "
        "la fascia di tolleranza al ±2% attorno al valore finale. Si osserva come al diminuire di ζ "
        "aumentino sovraelongazione e oscillazioni, mentre per ζ ≥ 1 la risposta è monotona crescente.",
        corpo))

    img1 = make_step_response_chart()
    story.append(Image(img1, width=14*cm, height=7*cm))
    story.append(Paragraph("Figura 1 — Risposta al gradino per diversi valori di ζ (ωₙ = 10 rad/s).", didascalia))

    story.append(Paragraph("2. Piano dei Poli (Piano s)", h1))
    story.append(Paragraph(
        "La posizione dei poli nel piano complesso determina interamente il comportamento transitorio. "
        "Per sistemi sottosmorzati (ζ < 1) i poli sono complessi coniugati, disposti su un arco di "
        "cerchio di raggio ωₙ. Al crescere di ζ i poli si avvicinano all'asse reale fino a "
        "confluire nel punto −ωₙ (smorzamento critico, ζ = 1). Per ζ > 1 i poli sono reali e distinti, "
        "entrambi sul semiasse reale negativo, garantendo la stabilità.",
        corpo))

    img2 = make_poles_chart()
    story.append(Image(img2, width=10*cm, height=8*cm))
    story.append(Paragraph("Figura 2 — Piano dei poli al variare di ζ. Cerchi = poli complessi, quadrati = poli reali.", didascalia))

    story.append(Paragraph("3. Interpretazione", h1))
    story.append(Paragraph(
        "Dalla lettura congiunta delle due figure emerge la regola progettuale fondamentale: "
        "il luogo delle radici descrive la traiettoria continua dei poli al variare di ζ, "
        "e ogni punto su tale traiettoria corrisponde a una curva di risposta nel dominio del tempo. "
        "Il progetto del controllore consiste nel posizionare i poli nella regione del piano s "
        "che soddisfa simultaneamente i vincoli su sovraelongazione, tempo di assestamento e margine "
        "di stabilità richiesti dalla specifica di progetto.",
        corpo))

    doc.build(story)
    print("PDF creato: test_grafici.pdf")


if __name__ == "__main__":
    build()
