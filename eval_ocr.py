#!/usr/bin/env python3
"""Misura l'errore di un motore OCR (CER / WER) su PDF di cui si conosce il testo esatto.

Perche' esiste: il README dice "Testo italiano: Eccellente", ma nessuno ha mai confrontato l'output
con un testo di riferimento. Qui il riferimento c'e': il PDF si genera da un corpus noto (reportlab),
si rasterizza in un PDF *senza* testo (solo immagini, come una scansione) e l'OCR si confronta con
l'originale.

Uso:
    uv run eval_ocr.py --engine marker                      # su GPU: il caso che interessa
    uv run eval_ocr.py --engine marker --engine tesseract   # con un riferimento esterno
    uv run eval_ocr.py --engine pdfplumber                  # sanity: sulle scansioni DEVE dare CER 100%
    uv run eval_ocr.py --pair scansione.pdf trascrizione.txt --engine marker   # documento reale
    uv run eval_ocr.py --self-test                          # controlla il banco di prova (senza GPU)

Metriche (testo normalizzato: NFKC, virgolette/trattini tipografici -> ASCII, spazi collassati,
markdown rimosso per i motori che lo producono):
    CER = distanza di Levenshtein sui caratteri / lunghezza del riferimento
    WER = distanza di Levenshtein sui token (split sugli spazi) / numero di token del riferimento
Possono superare 100% se l'output e' molto piu' lungo del riferimento.

Limiti, da leggere prima di citare un numero:
  * il corpus sintetico e' prosa italiana pulita (Helvetica): e' un limite *inferiore* dell'errore.
    Non misura tabelle, formule, simboli Unicode, layout a colonne, scansioni reali. Per quelli
    serve un documento vero con trascrizione (--pair).
  * le degradazioni (risoluzione, sfocatura, rotazione, JPEG) sono deterministiche e arbitrarie:
    confrontano i motori tra loro, non predicono una scansione specifica.
  * il motore "marker" non e' eseguibile in CI/sandbox senza GPU e pesi Surya: va lanciato a mano.
"""
import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------- corpus di riferimento

CORPUS = [
    "Il nuovo regolamento sulla gestione dei rifiuti entrerà in vigore il 1° settembre 2025 e "
    "riguarderà circa 38.500 famiglie. Chi non effettuerà correttamente la raccolta differenziata "
    "potrà ricevere una sanzione compresa tra 50 e 300 euro. Il comune ha precisato che, nei primi "
    "sei mesi, verrà applicato soltanto un richiamo scritto; dopodiché le verifiche saranno a "
    "campione, con un massimo di quattro controlli per quartiere ogni trimestre.",

    "Nel corso dell'esperimento sono stati misurati i tempi di risposta di 120 utenti, divisi in "
    "tre gruppi di uguale numerosità. Il gruppo di controllo ha impiegato in media 4,8 secondi "
    "(deviazione standard 1,2), mentre il gruppo con l'interfaccia semplificata ne ha impiegati "
    "3,9. La differenza, pari al 18,75%, è risultata significativa con p < 0,05; tuttavia il "
    "campione è piccolo e proviene da un'unica università, perciò i risultati vanno interpretati "
    "con cautela.",

    "«Non esiste un metodo perfetto», disse il vecchio restauratore, «ma esiste un metodo onesto: "
    "dichiarare ciò che si è fatto e ciò che non si è potuto fare». Quella frase, trascritta con "
    "cura nel registro del laboratorio, è rimasta appesa per anni sopra il banco da lavoro, accanto "
    "a un calendario del 1987 e a una fotografia sbiadita della cattedrale di Santa Maria.",

    "Per prenotare una visita è necessario scrivere a segreteria@esempio.it indicando nome, "
    "cognome, data preferita e numero di partecipanti (massimo 25). La risposta arriva di norma "
    "entro due giorni lavorativi. In caso di pioggia l'ingresso al giardino è sospeso; il museo, "
    "invece, resta aperto dalle 9:30 alle 17:00, tutti i giorni tranne il lunedì.",

    "Le prime reti di calcolatori occupavano intere stanze e comunicavano a velocità oggi "
    "impensabili: 300 bit al secondo erano considerati un risultato più che dignitoso. Eppure "
    "bastò un decennio perché quelle macchine, costose e capricciose, diventassero lo strumento "
    "quotidiano di migliaia di ricercatori. Chi ha vissuto quegli anni ricorda soprattutto "
    "l'attesa: un messaggio poteva impiegare ore ad arrivare, e nessuno se ne lamentava.",

    "Ingredienti per quattro persone: 320 g di pasta corta, 400 g di pomodori maturi, due spicchi "
    "d'aglio, mezzo peperoncino, un mazzetto di basilico, olio extravergine q.b. Si soffrigge "
    "l'aglio a fuoco basso, si aggiungono i pomodori tagliati a pezzi e si lascia cuocere per circa "
    "15 minuti. Nel frattempo si lessa la pasta in abbondante acqua salata, scolandola due minuti "
    "prima del tempo indicato.",
]

# nome, dpi finali, sfocatura (px), rotazione (gradi), qualita' JPEG
# (con Tesseract 5.3 'ita' danno circa 0%, 1%, 15-25%, 25-35%: sotto ~80 dpi l'OCR cade a picco,
#  quindi le ultime due servono a distinguere i motori, le prime a verificare che non sbaglino
#  su input facile)
VARIANTS = {
    "scan-200": dict(dpi=200, blur=0.0, angle=0.0, quality=95),
    "scan-90": dict(dpi=90, blur=1.0, angle=-1.2, quality=40),
    "scan-75": dict(dpi=75, blur=1.0, angle=-1.5, quality=35),
    "scan-65": dict(dpi=65, blur=0.8, angle=2.0, quality=25),
}
SRC_DPI = 200


# --------------------------------------------------------------------------- normalizzazione

_PUNCT = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    "­": None,
})
_TAGS = r"</?(?:span|div|br|p|sup|sub|b|i|em|strong|table|thead|tbody|tr|td|th|math|img|a)\b[^>]*>"


def strip_markdown(text):
    """Toglie la sintassi markdown/HTML che Marker aggiunge, lasciando il testo."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(_TAGS, " ", text, flags=re.I)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s*\{\d+\}-{5,}\s*$", " ", text, flags=re.M)
    text = re.sub(r"^\s*\|?[\s:|-]+\|?\s*$", " ", text, flags=re.M)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|<>~$])", r"\1", text)
    text = re.sub(r"(\*\*|__|\*|`)", "", text)
    text = re.sub(r"(?<!\w)_|_(?!\w)", "", text)
    return text.replace("|", " ")


def normalise(text, markdown=False, casefold=False):
    if markdown:
        text = strip_markdown(text)
    text = unicodedata.normalize("NFKC", text).translate(_PUNCT)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold() if casefold else text


# --------------------------------------------------------------------------- metriche

def levenshtein(a, b):
    """Distanza di Levenshtein globale (Hyyro' 2001, bit-parallela con interi Python).

    Funziona su qualunque sequenza di elementi hashabili (caratteri o token).
    """
    m = len(a)
    if m == 0:
        return len(b)
    if len(b) == 0:
        return m
    peq = {}
    for i, ch in enumerate(a):
        peq[ch] = peq.get(ch, 0) | (1 << i)
    mask = (1 << m) - 1
    last = 1 << (m - 1)
    pv, mv, score = mask, 0, m
    for ch in b:
        eq = peq.get(ch, 0)
        xv = eq | mv
        xh = (((eq & pv) + pv) ^ pv) | eq
        ph = mv | (~(xh | pv) & mask)
        mh = pv & xh
        if ph & last:
            score += 1
        elif mh & last:
            score -= 1
        ph = ((ph << 1) | 1) & mask
        mh = (mh << 1) & mask
        pv = mh | (~(xv | ph) & mask)
        mv = ph & xv
    return score


def _levenshtein_dp(a, b):
    """Riferimento lento (programmazione dinamica) usato solo da --self-test."""
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def error_rates(ref, hyp):
    ref_w, hyp_w = ref.split(), hyp.split()
    cer = levenshtein(ref, hyp) / max(1, len(ref))
    wer = levenshtein(ref_w, hyp_w) / max(1, len(ref_w))
    return cer, wer


def confusions(ref, hyp, top=8):
    """Le sostituzioni piu' frequenti (riferimento -> OCR), per capire *cosa* sbaglia il motore."""
    counts = Counter()
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and i2 - i1 <= 3 and j2 - j1 <= 3:
            counts[(ref[i1:i2], hyp[j1:j2])] += 1
        elif tag == "delete" and i2 - i1 <= 2:
            counts[(ref[i1:i2], "")] += 1
        elif tag == "insert" and j2 - j1 <= 2:
            counts[("", hyp[j1:j2])] += 1
    return counts.most_common(top)


# --------------------------------------------------------------------------- generazione dei PDF

def build_digital_pdf(path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    style = ParagraphStyle("corpo", fontName="Helvetica", fontSize=13, leading=21, spaceAfter=14)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            topMargin=2.5 * cm, bottomMargin=2.5 * cm)
    doc.build([item for p in CORPUS for item in (Paragraph(escape(p), style), Spacer(1, 2))])


def rasterise(pdf_path, dpi=SRC_DPI):
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        return [page.to_image(resolution=dpi).original.convert("L") for page in pdf.pages]


def degrade(img, dpi, blur, angle):
    from PIL import Image, ImageFilter
    if dpi != SRC_DPI:
        w, h = img.size
        img = img.resize((round(w * dpi / SRC_DPI), round(h * dpi / SRC_DPI)), Image.LANCZOS)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, fillcolor=255)
    return img


def build_image_only_pdf(images, path, dpi, quality):
    images[0].save(str(path), "PDF", resolution=float(dpi), save_all=True,
                   append_images=images[1:], quality=quality)


@dataclass
class Case:
    variant: str
    pdf: Path
    truth: str


def synthetic_cases(workdir, only=None):
    truth = normalise("\n\n".join(CORPUS))
    digital = workdir / "digital.pdf"
    build_digital_pdf(digital)
    cases = [Case("digital", digital, truth)]
    pages = rasterise(digital)
    for name, v in VARIANTS.items():
        pdf = workdir / f"{name}.pdf"
        build_image_only_pdf([degrade(p, v["dpi"], v["blur"], v["angle"]) for p in pages],
                             pdf, v["dpi"], v["quality"])
        cases.append(Case(name, pdf, truth))
    return [c for c in cases if not only or c.variant in only]


# --------------------------------------------------------------------------- motori

def engine_oracle(pdf, case):
    """Restituisce il riferimento: serve solo a dimostrare che il banco di prova da' 0%."""
    return case.truth


def engine_pdfplumber(pdf, case):
    """Solo strato di testo (il ramo 'PDF digitale' di convert.py). Su una scansione non legge nulla."""
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        return "\n\n".join((p.extract_text() or "") for p in doc.pages)


def engine_tesseract(pdf, case):
    """Riferimento esterno: Tesseract (modello 'ita') sulle pagine rasterizzate a 300 dpi."""
    out = []
    for img in rasterise(pdf, dpi=300):
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "p.png"
            img.save(png)
            run = subprocess.run(["tesseract", str(png), "stdout", "-l", "ita"],
                                 capture_output=True, text=True, check=True)
            out.append(run.stdout)
    return "\n\n".join(out)


_MARKER_MODELS = {}


def engine_marker(pdf, case):
    """Marker + Surya, con lo stesso codice di convert.py (nessun ramo pdfplumber)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import convert
    if "models" not in _MARKER_MODELS:
        from marker.models import create_model_dict
        print("  carico i modelli Marker (una volta sola)...", flush=True)
        _MARKER_MODELS["models"] = create_model_dict()
    out_dir = Path(tempfile.mkdtemp(prefix="eval_marker_"))
    try:
        md = convert._convert_marker(pdf, out_dir, ["it"], _MARKER_MODELS["models"])
        return md.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


ENGINES = {
    # nome: (funzione, produce markdown?)
    "oracle": (engine_oracle, False),
    "pdfplumber": (engine_pdfplumber, False),
    "tesseract": (engine_tesseract, False),
    "marker": (engine_marker, True),
}


# --------------------------------------------------------------------------- esecuzione

def evaluate(cases, engines, casefold=False, show_confusions=True):
    rows = []
    for engine in engines:
        fn, is_md = ENGINES[engine]
        for case in cases:
            t0 = time.time()
            raw = fn(case.pdf, case)
            secs = time.time() - t0
            hyp = normalise(raw, markdown=is_md, casefold=casefold)
            ref = normalise(case.truth, casefold=casefold)
            cer, wer = error_rates(ref, hyp)
            rows.append(dict(engine=engine, variant=case.variant, cer=cer, wer=wer,
                             seconds=round(secs, 2), ref_chars=len(ref), hyp_chars=len(hyp),
                             confusions=confusions(ref, hyp) if show_confusions else []))
    return rows


def print_table(rows):
    print(f"\n{'variante':10s} {'motore':11s} {'CER':>7s} {'WER':>7s} {'sec':>7s} {'car. out/rif':>14s}")
    for r in rows:
        print(f"{r['variant']:10s} {r['engine']:11s} {100 * r['cer']:6.2f}% {100 * r['wer']:6.2f}% "
              f"{r['seconds']:7.1f} {r['hyp_chars']:>7d}/{r['ref_chars']:<6d}")
    print()
    for r in rows:
        if r["confusions"] and r["cer"] > 0:
            top = ", ".join(f"{a or '∅'}→{b or '∅'} ×{n}" for (a, b), n in r["confusions"])
            print(f"  errori frequenti [{r['engine']} / {r['variant']}]: {top}")


# --------------------------------------------------------------------------- self-test

def self_test():
    import random
    failures = []

    def check(cond, msg):
        print(("PASS  " if cond else "FAIL  ") + msg)
        if not cond:
            failures.append(msg)

    rng = random.Random(7)
    alphabet = "abcé àù"
    ok = True
    for _ in range(600):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
        ok &= levenshtein(a, b) == _levenshtein_dp(a, b)
    for _ in range(20):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(150, 400)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(150, 400)))
        ok &= levenshtein(a, b) == _levenshtein_dp(a, b)
    ok &= levenshtein(list("a b c".split()), list("a x c d".split())) == 2
    check(ok, "Levenshtein bit-parallelo == programmazione dinamica (620 coppie, anche vuote e lunghe)")

    check(error_rates("abc", "abd")[0] == 1 / 3, "CER('abc','abd') = 1/3")
    check(error_rates("a b c", "a x c")[1] == 1 / 3, "WER('a b c','a x c') = 1/3")
    md = "## Titolo\n\n**grassetto** e _corsivo_ <!-- page 1 -->\n![](img.jpg)\n{0}------------\nfine"
    check(normalise(md, markdown=True) == "Titolo grassetto e corsivo fine", "strip del markdown di Marker")
    check(normalise("“x” – l’uno") == "\"x\" - l'uno", "virgolette e trattini tipografici -> ASCII")
    check("p < 0,05" in normalise(CORPUS[1], markdown=True),
          "il markdown strip non mangia il '<' del corpus")

    with tempfile.TemporaryDirectory() as tmp:
        cases = synthetic_cases(Path(tmp))
        import pdfplumber
        for c in cases:
            with pdfplumber.open(c.pdf) as doc:
                n_chars = sum(len(p.chars) for p in doc.pages)
            if c.variant == "digital":
                check(n_chars > 1000, f"digital.pdf ha uno strato di testo ({n_chars} caratteri)")
            else:
                check(n_chars == 0, f"{c.variant}.pdf e' solo immagine (0 caratteri di testo)")
        rows = {(r["engine"], r["variant"]): r for r in evaluate(cases, ["oracle", "pdfplumber"])}
        check(all(rows[("oracle", c.variant)]["cer"] == 0 for c in cases), "oracolo: CER 0 su tutte le varianti")
        check(rows[("pdfplumber", "digital")]["cer"] < 0.01,
              f"pdfplumber sul PDF digitale: CER {100 * rows[('pdfplumber', 'digital')]['cer']:.2f}% (< 1%)")
        check(all(rows[("pdfplumber", v)]["cer"] == 1.0 for v in VARIANTS),
              "pdfplumber sulle scansioni: CER 100% (nessun OCR, il banco lo vede)")
        if shutil.which("tesseract"):
            t = {r["variant"]: r for r in evaluate(cases, ["tesseract"], show_confusions=False)}
            print("      tesseract:", ", ".join(f"{v} CER {100 * t[v]['cer']:.1f}%" for v in t))
            check(t["scan-200"]["cer"] < 0.10, "tesseract su scan-200: CER < 10% (il banco misura un OCR vero)")
            check(t["scan-90"]["cer"] > t["scan-200"]["cer"],
                  "la degradazione peggiora davvero il risultato (scan-90 > scan-200)")
            check(t["scan-65"]["cer"] > 0.05,
                  "la variante peggiore lascia margine (Tesseract CER > 5%): il banco distingue i motori")
        else:
            print("SKIP  tesseract non installato")
    if failures:
        sys.exit(f"\n{len(failures)} controlli falliti")
    print("\nTutti i controlli passati.")


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", action="append", choices=sorted(ENGINES), help="motore da misurare (ripetibile)")
    ap.add_argument("--variant", action="append", help="solo queste varianti sintetiche (default: tutte)")
    ap.add_argument("--pair", nargs=2, action="append", metavar=("PDF", "TXT"),
                    help="documento reale con trascrizione; sostituisce il corpus sintetico (ripetibile)")
    ap.add_argument("--casefold", action="store_true", help="ignora maiuscole/minuscole")
    ap.add_argument("--out", help="scrive i risultati in JSON")
    ap.add_argument("--workdir", help="cartella in cui tenere i PDF sintetici (default: temporanea)")
    ap.add_argument("--self-test", action="store_true", help="verifica il banco di prova e termina")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.engine:
        ap.error("serve almeno un --engine (o --self-test)")

    tmp = None
    if args.pair:
        cases = [Case(Path(p).stem, Path(p), normalise(Path(t).read_text(encoding="utf-8")))
                 for p, t in args.pair]
    else:
        if args.workdir:
            workdir = Path(args.workdir)
            workdir.mkdir(parents=True, exist_ok=True)
        else:
            tmp = tempfile.TemporaryDirectory()
            workdir = Path(tmp.name)
        cases = synthetic_cases(workdir, only=set(args.variant) if args.variant else None)
    try:
        rows = evaluate(cases, args.engine, casefold=args.casefold)
    finally:
        if tmp:
            tmp.cleanup()
    print_table(rows)
    if args.out:
        Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"risultati in {args.out}")


if __name__ == "__main__":
    main()
