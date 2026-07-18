# Greyhound Edge Engine v3.2

A pure LLM-native Australian greyhound racing analysis engine. This project removes the need for fragile external APIs and scraping scripts by leveraging the LLM you are already talking to.

## Architecture

The system has two main stages:

```text
┌──────────────────────────────────────────────────────────────┐
│  STAGE 1: DATA EXTRACTION (racing-form-extractor)            │
│                                                              │
│  R&S Enhanced PDF  ──→  greyhound_extract.py  ──→  .xlsx     │
│  (or manual paste)      (pdfplumber + regex)      workbook   │
│                                                              │
│  Output: Race Summary + Runner Cards + Run History tabs      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  STAGE 2: LLM ANALYSIS (v3.2 methodology skill)             │
│                                                              │
│  User pastes extracted data (or raw text) into LLM           │
│  LLM auto-loads .gemini/skills.md + methodology              │
│  Follows 9-skill pipeline: parse → profile → map → value     │
│                                                              │
│  Output: Full A–K structured analysis                        │
└──────────────────────────────────────────────────────────────┘
```

## Setup & Usage

### 1. Using with Claude Code / Gemini Code Assist
If you are using a coding assistant that supports `.gemini` folders or `AGENTS.md` (like this one!):
1. Navigate to this directory in your assistant.
2. Say "Analyse this race" and paste your form guide data (or provide an extracted Excel file).
3. The LLM will automatically load the skills and follow the exact A-K methodology.

### 2. Using with any other LLM (ChatGPT, Claude web, etc.)
1. Open `prompts/master_prompt.md`.
2. Copy the entire contents and paste it as your first message (system prompt).
3. Paste your form guide data.
4. The LLM will follow the instructions to generate the analysis.

## PDF Form Extraction
If you want to use Racing And Sports Enhanced PDFs as input:
1. Put your downloaded PDFs in `racing-form-extractor/input/`.
2. Run `racing-form-extractor/run.bat` (Windows) or `python racing-form-extractor/scripts/process_folder.py input output`.
3. Open the generated Excel workbook in `racing-form-extractor/output/` and copy the data for your race to paste into the LLM.
*(You can also use `download.bat` to help fetch PDFs semi-automatically).*

## Parameter Tuning
All analysis parameters (weights, thresholds, scaling, staking caps) are located in `config/settings.yaml`. You can edit this file to tweak the engine's behavior. The LLM will read these settings when performing the analysis.

## Project Structure
- `.gemini/` - Skill and Agent definitions.
- `prompts/` - Step-by-step templates for the LLM to structure its output.
- `config/` - `settings.yaml` and `track_meta.json`.
- `racing-form-extractor/` - Tooling to convert PDFs to Excel data.
