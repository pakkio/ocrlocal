"""
Post-processa un MD prodotto da Marker: chiede a un LLM testuale di ricostruire
i simboli matematici Unicode sostituiti con ■ durante l'OCR.

Usa Ollama in locale (nessun dato esce dalla macchina).
"""
import sys
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "qwen3.5")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

PROMPT_TEMPLATE = """Sei un esperto di matematica e fisica. Il testo seguente è stato estratto da un PDF tramite OCR.
Il carattere ■ indica un simbolo Unicode che l'OCR non ha riconosciuto (tipicamente: apici, pedici, lettere greche, simboli matematici come ℝ, ∈, λ, ω, ζ, ecc.).

Ricostruisci il testo corretto sostituendo ogni ■ con il simbolo più probabile in base al contesto matematico.
Restituisci SOLO il testo corretto, senza spiegazioni.

Testo da correggere:
{text}"""

CHUNK_SIZE = 1500


def call_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_TEXT_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"].strip()


def split_chunks(text: str, size: int) -> list[str]:
    """Spezza il testo preservando i paragrafi."""
    chunks, current = [], []
    current_len = 0
    for line in text.splitlines(keepends=True):
        if current_len + len(line) > size and current:
            chunks.append("".join(current))
            current, current_len = [], 0
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("".join(current))
    return chunks


def process(md_path: str):
    md_file = Path(md_path)
    if not md_file.exists():
        print(f"File non trovato: {md_file}", file=sys.stderr)
        sys.exit(1)

    text = md_file.read_text(encoding="utf-8")

    if "■" not in text:
        print("Nessun simbolo [?] trovato - nulla da correggere.")
        sys.exit(0)

    count = text.count("■")
    print(f"Trovati {count} simboli [?] - correzione con {OLLAMA_TEXT_MODEL}...")

    chunks = split_chunks(text, CHUNK_SIZE)
    fixed_parts = []
    for i, chunk in enumerate(chunks, 1):
        if "■" not in chunk:
            fixed_parts.append(chunk)
            continue
        print(f"  Chunk {i}/{len(chunks)} ({chunk.count('■')} simboli)...")
        prompt = PROMPT_TEMPLATE.format(text=chunk)
        fixed_parts.append(call_ollama(prompt))

    result = "".join(fixed_parts)
    remaining = result.count("■")

    out_file = md_file.parent / (md_file.stem + "_fixed.md")
    out_file.write_text(result, encoding="utf-8")
    print(f"\nSalvato: {out_file}")
    print(f"Simboli corretti: {count - remaining}/{count} ([?] rimasti: {remaining})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: uv run fix_symbols.py <output/file.md>")
        print("Esempio: uv run fix_symbols.py output/test_italiano.md")
        sys.exit(1)
    process(sys.argv[1])
