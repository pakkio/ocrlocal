# marker

Pipeline locale PDF → Markdown con descrizione automatica delle figure via LLM vision.

**Stack:** [Marker](https://github.com/VikParuchuri/marker) + [Surya OCR](https://github.com/VikParuchuri/surya) + GPU (CUDA) + [OpenRouter](https://openrouter.ai) per vision.

## Funzionalità

- Routing automatico: pdfplumber per PDF digitali semplici (sub-secondo/pagina), Marker+OCR per PDF complessi o scansionati
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

**Con figure e simboli matematici:**
```bash
uv run convert.py documento.pdf output it
uv run describe_figures.py output/documento.md          # → documento_described.md
uv run fix_symbols.py output/documento_described.md     # → documento_described_fixed.md
```

**Solo simboli matematici (nessuna figura):**
```bash
uv run convert.py documento.pdf output it
uv run fix_symbols.py output/documento.md               # → documento_fixed.md
```

`fix_symbols.py` esce subito se non trova `■`. `describe_figures.py` salta le immagini non trovate.

## Esempio reale: tesi di ingegneria scansionata

Scenario: tesi di 120 pagine in italiano, scansionata (no testo selezionabile), con grafici matplotlib, tabelle di dati e formule con ℝⁿ, λᵢ, ωₙ.

```bash
# 1. Converti — Marker rileva la scansione e avvia OCR su GPU (~35 min)
uv run convert.py tesi_scansionata.pdf output it
# → output/tesi_scansionata.md  (testo + tabelle in Markdown)
# → output/tesi_scansionata/    (23 figure estratte come JPEG)

# 2. Descrivi le 23 figure in italiano (~6 min con minicpm-v offline)
uv run describe_figures.py output/tesi_scansionata.md
# → output/tesi_scansionata_described.md
#   Ogni ![]() diventa:
#   ![Grafico della risposta al gradino con ζ=0.5 e ωₙ=10 rad/s...](fig.jpeg)
#   > **Figura:** Grafico della risposta al gradino...

# 3. Ricostruisci i simboli Unicode persi dall'OCR (~18 min con gemma4)
uv run fix_symbols.py output/tesi_scansionata_described.md
# → output/tesi_scansionata_described_fixed.md   ← file finale completo
#   "il vettore ■(t) ∈ ■ⁿ"  →  "il vettore x(t) ∈ ℝⁿ"
```

Risultato finale: Markdown leggibile con figure descritte e simboli matematici corretti, pronto per indicizzazione, ricerca full-text o input a un RAG.

**Stesso documento con PDF digitale** (testo selezionabile, nessuna scansione):
```bash
uv run convert.py tesi_digitale.pdf output it   # pdfplumber: ~12s invece di 35 min
```

## Qualità e limiti

| Elemento | Qualità |
|---|---|
| Testo italiano | Eccellente |
| Tabelle | Eccellente |
| Formule LaTeX semplici | Buona |
| Simboli matematici Unicode (ℝⁿ, λᵢ, ωₙ) | Buona — ricostruiti con `fix_symbols.py` via LLM |
| Figure / fotografie | Estratte + descritte via LLM |

> I giudizi della tabella sono impressioni d'uso, **non misure**: nessuno li ha mai confrontati con un testo di riferimento. Vedi [Valutazione OCR](#valutazione-ocr) per il modo di misurarli.

I caratteri Unicode avanzati sono un limite di Surya OCR, non risolvibile con hardware migliore. `fix_symbols.py` li ricostruisce tramite contesto matematico con gemma4 (18/18 corretti nel test, ~266s). Per LaTeX pesante (tesi scientifiche) valutare Nougat o GOT-OCR.

## Valutazione OCR

`eval_ocr.py` misura l'errore (CER = errori sui caratteri, WER = errori sulle parole) confrontando l'output con un testo noto: genera un PDF da un corpus italiano, lo rasterizza in un PDF **senza strato di testo** (come una scansione), lo degrada (risoluzione, sfocatura, rotazione, JPEG) e lo passa al motore.

```bash
uv run eval_ocr.py --self-test                          # controlla il banco di prova (non serve la GPU)
uv run eval_ocr.py --engine marker --engine tesseract   # misura Marker, con Tesseract come riferimento
uv run eval_ocr.py --engine marker --pair tesi.pdf tesi_trascritta.txt   # su un documento vero
```

Il banco di prova è stato validato con Tesseract 5.3 (`ita`): CER 0,04% sul PDF digitale, 0,08% a 200 dpi, 0,9% a 90 dpi, 15% a 75 dpi, 26% a 65 dpi; `pdfplumber` sulle scansioni dà 100% (nessun OCR), come deve. **Questi non sono i numeri di Marker**: il motore `marker` richiede GPU e pesi Surya e va lanciato a mano. Quando lo fai, incolla qui la tabella.

Limiti: il corpus è prosa pulita, quindi misura un errore *minimo*; tabelle, formule, simboli Unicode, layout a colonne e scansioni vere richiedono un documento reale con trascrizione (`--pair`).

## Licenze

*(verificato il 24/11/2026 sui README e sul `MODEL_LICENSE` di [marker](https://github.com/datalab-to/marker) e [surya](https://github.com/datalab-to/surya); non è consulenza legale, il testo che vale è quello nei repo)*

| Cosa | Licenza |
|---|---|
| Questo repo | nessun file `LICENSE`: per default tutti i diritti sono riservati |
| Codice di Marker e di Surya | Apache 2.0 |
| **Pesi dei modelli** (scaricati da HuggingFace alla prima conversione) | "AI Pubs Open RAIL-M (Modified)" v0.1, file `MODEL_LICENSE` |

I pesi hanno condizioni diverse dal codice:

- **Uso di ricerca e personale:** esente dalle soglie economiche qui sotto.
- **Uso commerciale:** ristretto se tu, il tuo datore di lavoro o un'entità affiliata avete avuto più di 5 milioni di USD di ricavi lordi nell'anno precedente **oppure** avete raccolto più di 5 milioni di USD di finanziamenti totali (capitale o debito). Basta una delle due: è gratuito solo restando sotto entrambe.
- **Prodotti concorrenti:** vietato offrire prodotti o servizi che competono con quelli di Datalab, **senza** eccezione per ricerca o uso personale. La licenza considera distribuzione anche i servizi hosted, l'accesso via API e via web: se esponi `server.py` a terzi, conta.
- **Attenzione ai riassunti:** i README di marker e surya scrivono "startups under $5M funding/revenue" senza dire se le soglie siano in E o in O. Il `MODEL_LICENSE` dice O (una sola basta per la restrizione). Per un uso commerciale leggi il file, non il riassunto; per licenze oltre le soglie i README rimandano alla pagina prezzi di Datalab.

## Performance

**Conversione PDF → Markdown:**

| Percorso | Condizione | Tempo (5 pag.) | Tempo (500 pag.) |
|---|---|---|---|
| pdfplumber | PDF digitale, no immagini/tabelle | ~0.5s | ~5 min |
| Marker + CPU | PDF complesso | ~5 min | ~8 ore |
| Marker + GTX 1080 | PDF complesso | ~85s | ~2.5 ore |

Il routing è automatico: `convert.py` sceglie il percorso in base al contenuto del PDF.

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

## Web server

```bash
uv run python -m uvicorn server:app --reload
```

Apri `http://localhost:8000` per il form di upload. Oppure via API:

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@documento.pdf" \
  -F "langs=it"
```

Il PDF viene processato in una directory temporanea e cancellato dopo la risposta.

## File

| File | Scopo |
|---|---|
| `server.py` | Web server FastAPI (upload PDF → Markdown) |
| `convert.py` | Conversione PDF → Markdown |
| `describe_figures.py` | Descrizione figure via LLM vision |
| `fix_symbols.py` | Ricostruzione simboli Unicode ■ via LLM testuale |
| `eval_ocr.py` | Misura CER/WER di un motore OCR su PDF a testo noto (`--self-test` per il banco di prova) |
| `crea_pdf.py` | Genera PDF di test (testo + tabelle + formule) |
| `crea_pdf_grafici.py` | Genera PDF di test con grafici matplotlib |
