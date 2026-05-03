"""
Web server: upload a PDF, get back Markdown.

Routes automatically: pdfplumber for simple digital PDFs (sub-second),
Marker+OCR for scanned/complex PDFs (minutes).

Usage:
    uv run python -m uvicorn server:app --reload
    open http://localhost:8000
"""
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from convert import _is_simple_pdf, _convert_pdfplumber, _convert_marker

app = FastAPI(title="PDF → Markdown", version="1.0")

UPLOAD_FORM = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>PDF → Markdown</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 60px auto; }
    input[type=file] { margin: 12px 0; }
    button { padding: 8px 20px; cursor: pointer; }
    #result { margin-top: 24px; white-space: pre-wrap; font-family: monospace;
              font-size: 13px; background: #f4f4f4; padding: 16px;
              border-radius: 6px; max-height: 600px; overflow: auto; }
  </style>
</head>
<body>
  <h2>PDF → Markdown</h2>
  <p>Carica un PDF. Il server sceglie automaticamente pdfplumber (veloce)
     o Marker+OCR (complesso/scansionato).</p>
  <form id="f">
    <input type="file" name="file" accept=".pdf" required><br>
    <label><input type="checkbox" name="langs" value="it" checked> italiano</label>
    &nbsp;<label><input type="checkbox" name="langs" value="en"> english</label><br><br>
    <button type="submit">Converti</button>
  </form>
  <div id="result"></div>
  <script>
    document.getElementById('f').addEventListener('submit', async e => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const langs = [...document.querySelectorAll('[name=langs]:checked')]
                    .map(el => el.value).join(',') || 'it';
      fd.append('langs', langs);
      document.getElementById('result').textContent = 'Elaborazione in corso...';
      const r = await fetch('/convert?langs=' + langs, { method: 'POST', body: fd });
      document.getElementById('result').textContent = r.ok
        ? await r.text()
        : 'Errore: ' + await r.text();
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return UPLOAD_FORM


@app.post("/convert", response_class=PlainTextResponse)
async def convert(file: UploadFile = File(...), langs: str = "it"):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File deve essere un PDF")

    lang_list = [l.strip() for l in langs.split(",") if l.strip()]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pdf_path = tmp_path / file.filename
        pdf_path.write_bytes(await file.read())
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        if _is_simple_pdf(pdf_path):
            out_file = _convert_pdfplumber(pdf_path, out_dir)
        else:
            out_file = _convert_marker(pdf_path, out_dir, lang_list)

        return out_file.read_text(encoding="utf-8")
