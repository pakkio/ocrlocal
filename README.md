# marker

Pipeline locale PDF → Markdown con descrizione automatica delle figure via LLM vision.

**Stack:** [Marker](https://github.com/VikParuchuri/marker) + [Surya OCR](https://github.com/VikParuchuri/surya) + GPU (CUDA) + [OpenRouter](https://openrouter.ai) per vision.

## Funzionalità

- Converte PDF in Markdown strutturato (testo, tabelle, heading, formule LaTeX)
- Estrae figure/fotografie come immagini JPEG
- Descrive ogni figura in italiano tramite un modello vision (Gemini 2.5 Flash via OpenRouter o minicpm-v via Ollama)
- Ricostruisce i simboli matematici Unicode persi dall'OCR (ℝⁿ, λᵢ, ωₙ) tramite LLM testuale locale
- Modalità completamente offline: nessun dato esce dalla macchina (Ollama per vision + testo)

## Requisiti

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- GPU NVIDIA con CUDA 12.x e **almeno 6 GB VRAM** (facoltativo ma consigliato — ~4x più veloce; su CPU funziona ma lento)
- [Ollama](https://ollama.com) con `minicpm-v` per descrizione figure offline — oppure API key OpenRouter per modalità cloud

## Installazione

```bash
git clone ...
cd marker
uv sync
```

Al primo avvio `uv sync` scarica PyTorch+CUDA e `marker-pdf`. I modelli Surya (~1-2 GB) vengono scaricati da HuggingFace alla prima conversione.

## Configurazione

```bash
cp .env.example .env
# modifica .env con la tua chiave
```

`.env` — modalità offline (consigliata per privacy):
```
OLLAMA_MODEL=minicpm-v
```

`.env` — modalità cloud (OpenRouter):
```
OPENROUTER_API_KEY=sk-or-...
VISION_MODEL=google/gemini-2.5-flash
```

Se `OLLAMA_MODEL` è definito ha la precedenza su OpenRouter. `VISION_MODEL` può essere qualsiasi modello vision disponibile su OpenRouter.

## Utilizzo

### 1. Converti PDF → Markdown

```bash
uv run convert.py <file.pdf> [cartella_output] [lingue]
```

```bash
uv run convert.py documento.pdf output it
uv run convert.py tesi.pdf output it,en
```

Output in `output/`:
- `documento.md` — testo convertito
- `documento/` — immagini estratte (`_page_N_Figure_M.jpeg`)

### 2. Descrivi le figure con LLM vision

```bash
uv run describe_figures.py output/documento.md
```

Produce `output/documento_described.md`: ogni `![]()` viene sostituito con alt-text descrittivo generato dal modello vision + blocco citazione.

### 3. Correggi i simboli matematici

```bash
uv run fix_symbols.py output/documento.md
```

Produce `output/documento_fixed.md`: ogni `■` (simbolo Unicode perso dall'OCR) viene ricostruito tramite LLM testuale in base al contesto matematico. Richiede Ollama con un modello testuale (es. `gemma4` o `gemma3:4b`).

### Workflow completo

```bash
uv run convert.py documento.pdf output it
uv run describe_figures.py output/documento.md
uv run fix_symbols.py output/documento.md
# risultati finali: output/documento_described.md + output/documento_fixed.md
```

## Qualità e limiti

| Elemento | Qualità |
|---|---|
| Testo italiano | Eccellente |
| Tabelle | Eccellente |
| Formule LaTeX semplici | Buona |
| Simboli matematici Unicode (ℝⁿ, λᵢ, ωₙ) | Buona — ricostruiti con `fix_symbols.py` via LLM |
| Figure / fotografie | Estratte + descritte via LLM |

I caratteri Unicode avanzati sono un limite di Surya OCR, non risolvibile con hardware migliore. `fix_symbols.py` li ricostruisce tramite contesto matematico con gemma4 (18/18 corretti nel test, ~266s). Per LaTeX pesante (tesi scientifiche) valutare Nougat o GOT-OCR.

## Performance

**Conversione PDF → Markdown (GTX 1080):**

| Hardware | Tempo (PDF 5 pag.) |
|---|---|
| CPU | ~5 min |
| GTX 1080 (8 GB VRAM) | ~85s |

**Correzione simboli Unicode (fix_symbols.py, GTX 1080):**

| Modello | Tempo (18 simboli, 5 pag.) | VRAM | Privacy |
|---|---|---|---|
| gemma4 (Ollama) | ~266s | 9.6 GB | totale |
| gemma3:4b (Ollama) | ~60s | 3.5 GB | totale (qualità inferiore) |

**Descrizione figure (per immagine, GTX 1080):**

| Modello | Latenza | VRAM | Privacy |
|---|---|---|---|
| minicpm-v (Ollama) | ~17s | 5.5 GB | totale |
| gemma4 (Ollama) | ~56s | 9.6 GB | totale |
| Gemini 2.5 Flash (OpenRouter) | ~5s | — | immagini in cloud |

## File

| File | Scopo |
|---|---|
| `convert.py` | Conversione PDF → Markdown |
| `describe_figures.py` | Descrizione figure via LLM vision |
| `fix_symbols.py` | Ricostruzione simboli Unicode ■ via LLM testuale |
| `crea_pdf.py` | Genera PDF di test (testo + tabelle + formule) |
| `crea_pdf_grafici.py` | Genera PDF di test con grafici matplotlib |
