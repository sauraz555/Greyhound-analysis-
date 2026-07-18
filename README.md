# Greyhound Edge Engine v3.2

A pure LLM-native Australian greyhound racing analysis engine. This project relies entirely on the LLM's intelligence to parse and analyze form guide data manually pasted by the user.

## Architecture

The system operates purely through an LLM analyzing manual input:

```text
┌──────────────────────────────────────────────────────────────┐
│  LLM ANALYSIS (v3.2 methodology skill)                       │
│                                                              │
│  User pastes raw form guide data into the LLM                │
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
2. Say "Analyse this race" and paste your form guide data.
3. The LLM will automatically load the skills and follow the exact A-K methodology.

### 2. Using with any other LLM (ChatGPT, Claude web, etc.)
1. Open `prompts/master_prompt.md`.
2. Copy the entire contents and paste it as your first message (system prompt).
3. Paste your form guide data.
4. The LLM will follow the instructions to generate the analysis.

## Parameter Tuning
All analysis parameters (weights, thresholds, scaling, staking caps) are located in `config/settings.yaml`. You can edit this file to tweak the engine's behavior. The LLM will read these settings when performing the analysis.

## Project Structure
- `.gemini/` - Skill and Agent definitions.
- `prompts/` - Step-by-step templates for the LLM to structure its output.
- `config/` - `settings.yaml` and `track_meta.json`.
