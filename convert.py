import sys
import os
from pathlib import Path


MIN_TEXT_PER_PAGE = 50  # chars below this = likely scanned page


def _is_simple_pdf(pdf_path: Path) -> bool:
    """Returns True if the PDF has no images, no tables, and extractable text on every page."""
    import pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.images:
                    return False
                if page.extract_tables():
                    return False
                text = page.extract_text() or ""
                if len(text.strip()) < MIN_TEXT_PER_PAGE:
                    return False
        return True
    except Exception:
        return False


def _convert_pdfplumber(pdf_path: Path, out_dir: Path) -> Path:
    import pdfplumber
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"<!-- page {i} -->\n{text}")
    md = "\n\n".join(parts)
    out_file = out_dir / (pdf_path.stem + ".md")
    out_file.write_text(md, encoding="utf-8")
    return out_file


def _convert_marker(pdf_path: Path, out_dir: Path, langs: list[str]) -> Path:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    from marker.config.parser import ConfigParser

    print("Caricamento modelli Marker...")
    models = create_model_dict()
    config = ConfigParser({"langs": ",".join(langs)})
    converter = PdfConverter(artifact_dict=models, config=config.generate_config_dict())
    rendered = converter(str(pdf_path))
    text, _, images = text_from_rendered(rendered)

    out_file = out_dir / (pdf_path.stem + ".md")
    out_file.write_text(text, encoding="utf-8")

    if images:
        img_dir = out_dir / pdf_path.stem
        img_dir.mkdir(exist_ok=True)
        for name, img in images.items():
            img.save(img_dir / name)
        print(f"Immagini: {img_dir}/")

    return out_file


def convert(pdf_path: str, output_dir: str = "output", langs: list[str] = ["it"]):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"File non trovato: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analisi PDF: {pdf_path.name}...")
    if _is_simple_pdf(pdf_path):
        print("PDF semplice rilevato — uso pdfplumber (veloce)")
        out_file = _convert_pdfplumber(pdf_path, out_dir)
        print(f"Salvato: {out_file}")
    else:
        print("PDF complesso rilevato (scansione / immagini / tabelle) — uso Marker+OCR")
        out_file = _convert_marker(pdf_path, out_dir, langs)
        print(f"Salvato: {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: uv run convert.py <file.pdf> [output_dir] [lang1,lang2,...]")
        print("Esempio: uv run convert.py documento.pdf output it,en")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "output"
    langs = sys.argv[3].split(",") if len(sys.argv) > 3 else ["it"]

    convert(pdf, out, langs)
