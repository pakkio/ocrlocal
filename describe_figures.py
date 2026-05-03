"""
Post-processa un MD prodotto da Marker: sostituisce ![](...) con descrizioni
generate da un modello vision.

Modalità:
  OLLAMA_MODEL nel .env  → usa Ollama locale (privacy totale, offline)
  OPENROUTER_API_KEY     → usa OpenRouter (cloud, modelli più potenti)
"""
import sys
import re
import base64
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL      = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
VISION_MODEL      = os.getenv("VISION_MODEL", "google/gemini-2.5-flash")

PROMPT = (
    "Sei un assistente scientifico. Descrivi in italiano questa figura estratta da un documento PDF. "
    "Indica: tipo di grafico o immagine, assi se presenti, elementi principali, legenda se visibile, "
    "e il messaggio principale che la figura comunica. Sii preciso e conciso (max 5 righe)."
)


def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()


def describe_via_ollama(img_path: Path) -> str:
    import urllib.request, json
    data = encode_image(img_path)
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": PROMPT,
        "images": [data],
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"].strip()


def describe_via_openrouter(img_path: Path, client) -> str:
    ext = img_path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    data = encode_image(img_path)
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
            ],
        }],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()


def build_client():
    if OLLAMA_MODEL:
        print(f"Modalità: Ollama locale ({OLLAMA_MODEL})")
        return None
    if OPENROUTER_API_KEY:
        from openai import OpenAI
        print(f"Modalità: OpenRouter ({VISION_MODEL})")
        return OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
    print("Errore: definisci OLLAMA_MODEL o OPENROUTER_API_KEY nel .env", file=sys.stderr)
    sys.exit(1)


def describe_image(img_path: Path, client) -> str:
    if OLLAMA_MODEL:
        return describe_via_ollama(img_path)
    return describe_via_openrouter(img_path, client)


def process(md_path: str):
    client = build_client()

    md_file = Path(md_path)
    if not md_file.exists():
        print(f"File non trovato: {md_file}", file=sys.stderr)
        sys.exit(1)

    text = md_file.read_text(encoding="utf-8")
    pattern = re.compile(r"!\[\]\(([^)]+)\)")

    def replace(match):
        img_rel = match.group(1)
        img_path = md_file.parent / img_rel
        if not img_path.exists():
            img_path = md_file.parent / md_file.stem / img_rel
        if not img_path.exists():
            print(f"  [skip] non trovata: {img_rel}")
            return match.group(0)
        model_tag = OLLAMA_MODEL or VISION_MODEL
        print(f"  Descrivo: {img_path.name} ({model_tag})...")
        try:
            desc = describe_image(img_path, client)
            preview = desc[:80].encode("ascii", errors="replace").decode()
            print(f"    -> {preview}...")
            return f"![{desc}]({img_rel})\n\n> **Figura:** {desc}"
        except Exception as e:
            print(f"  [errore] {e}")
            return match.group(0)

    result = pattern.sub(replace, text)
    out_file = md_file.parent / (md_file.stem + "_described.md")
    out_file.write_text(result, encoding="utf-8")
    print(f"\nSalvato: {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: uv run describe_figures.py <output/file.md>")
        print("Esempio: uv run describe_figures.py output_grafici/test_grafici.md")
        sys.exit(1)
    process(sys.argv[1])
