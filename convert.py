import sys
import os
from pathlib import Path


def convert(pdf_path: str, output_dir: str = "output", langs: list[str] = ["it"]):
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    from marker.config.parser import ConfigParser

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"File non trovato: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Caricamento modelli...")
    models = create_model_dict()

    print(f"Conversione: {pdf_path.name}")
    config = ConfigParser({"langs": ",".join(langs)})
    converter = PdfConverter(artifact_dict=models, config=config.generate_config_dict())
    rendered = converter(str(pdf_path))

    text, _, images = text_from_rendered(rendered)

    out_file = out_dir / (pdf_path.stem + ".md")
    out_file.write_text(text, encoding="utf-8")
    print(f"Salvato: {out_file}")

    if images:
        img_dir = out_dir / pdf_path.stem
        img_dir.mkdir(exist_ok=True)
        for name, img in images.items():
            img.save(img_dir / name)
        print(f"Immagini: {img_dir}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: uv run convert.py <file.pdf> [output_dir] [lang1,lang2,...]")
        print("Esempio: uv run convert.py documento.pdf output it,en")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "output"
    langs = sys.argv[3].split(",") if len(sys.argv) > 3 else ["it"]

    convert(pdf, out, langs)
