---
name: racing-form-extractor
description: Extract structured data from Racing And Sports (racingandsports.com.au) "Feature Form" Enhanced PDF form guides, for both thoroughbred and greyhound meetings. Use when the user has a Feature Form PDF (or a folder of them) and wants race cards, runner fields, and full past-run history turned into a spreadsheet. Produces one Excel workbook per meeting with a Race Summary tab, one runner-card tab per race, and a Run History tab (one row per past run per runner - class, margin, sectional times, jockey/trainer, odds, winner/placegetters, settling position). Includes an optional semi-automated downloader that opens a real browser for the user to manually log in / clear Cloudflare, then automates navigation and clicking after that - it never solves the Cloudflare challenge itself.
license: Proprietary. Built for personal, non-commercial use consistent with racingandsports.com.au's Terms and Conditions.
---

# Racing Form Extractor

## Overview

Racing And Sports "Feature Form" Enhanced PDFs pack a huge amount of data into a
layout that's easy for a human to skim but painful to work with programmatically:
runner tables, then per-runner detail blocks with career stats, sire/dam, and a
run-by-run history that wraps across lines and pages. This skill turns one of
those PDFs into a clean Excel workbook, and optionally helps get the PDF in the
first place.

Two racing codes are supported with **separate parser scripts**, because the
underlying PDF layout differs enough that one parser can't safely cover both:

- `scripts/horse_extract.py` - thoroughbred meetings. Handles the jockey+trainer
  field, which the PDF glues together with no delimiter unless the jockey has an
  apprentice claim like "(a2.0)". Resolved using corpus-wide evidence (claim
  markers, recurring trainer names, single-name-only trainer rows) rather than a
  fixed word-count guess.
- `scripts/greyhound_extract.py` - greyhound meetings. No jockey field (trainer
  only), box instead of barrier, no weight.

Both scripts auto-detect race boundaries and runner counts from the PDF itself -
they are not hardcoded to a specific number of races.

`scripts/process_folder.py` is the batch driver: it scans an input folder,
detects each PDF's code by inspecting the weight column (greyhound weights are
always a placeholder "0.0kg"/"0kg", thoroughbred weights are real), dispatches
to the right script, and writes one workbook per PDF. `run.bat` wraps this for
Windows users with no command-line.

`scripts/download_form_guides.py` (optional, `download.bat` wraps it) is a
semi-automated PDF fetcher. It is NOT full automation and must never be turned
into full automation - see "Bot-detection boundary" below, this is a hard
constraint, not a preference.

## When to use this skill

Trigger on: a `.pdf` form guide is attached or referenced, the user mentions
"form guide", "Feature Form", "Racing and Sports", "R&S PDF", wants runner data
or "run history" or "past form" extracted from a racing PDF, or wants a
spreadsheet built from a thoroughbred/greyhound form guide. Also trigger the
downloader path when the user wants help *getting* PDFs from the site, not just
parsing ones they already have.

## Bot-detection boundary (read before touching download_form_guides.py)

racingandsports.com.au's PDF download pages run Cloudflare bot-detection
("Verify you are human"). Building or modifying anything that solves that
challenge programmatically is out of scope - not a judgment call to make case
by case, a categorical line. `download_form_guides.py` is built specifically to
respect this:

- It launches a **visible, non-headless** browser and pauses with `input()`,
  waiting for a human to log in and clear any Cloudflare challenge manually.
- It reuses the resulting session (via a persistent Playwright profile dir) to
  automate the parts that aren't bot-detection - navigating to a known URL and
  clicking a known button.
- If Cloudflare re-triggers on a later page, it stops and asks the human to
  solve it again. It does not retry, does not add wait-and-hope loops, and does
  not try alternate rendering paths to dodge the check.

If asked to make the downloader "fully automatic," "headless," or to "handle
the verification," the answer is no for the Cloudflare-solving part
specifically - explain the constraint (it's about what's being defeated, not
which tool does it - Playwright, Selenium, raw requests, doesn't matter) and
offer the legitimate alternative already built: session reuse after a manual
first solve. Headless mode is available as a flag for convenience *after* a
session is already established, but the user should know that going headless
means they won't see a re-challenge happen - it'll just fail.

## How to identify the racing code

Open the first page of the PDF and check the venue/distance line and the runner
rows:

- **Thoroughbred**: distances are 900m-3200m range, weight column has real
  values ("59.0kg"), and the field between barrier and career record contains
  a jockey name (sometimes with a trainer name run together).
- **Greyhound**: distances are 275m-732m range, weight column is always
  "0.0kg"/"0kg", and the field between barrier/box and career record is just a
  trainer name (no jockey).

`process_folder.py`'s `detect_code()` does this automatically - reuse it
rather than re-deriving the heuristic if you're scripting around this skill.

## Running the extractor

Batch mode (recommended - handles both codes in one folder):

```bash
pip install -r requirements.txt
python scripts/process_folder.py input_dir output_dir
```

Windows users can just drop PDFs in `input/` and double-click `run.bat`.

Single-file mode, when you already know the code:

```bash
# Thoroughbred meeting
python scripts/horse_extract.py MORUYA_10Jul2026.pdf MORUYA_10Jul2026_FormGuide.xlsx

# Greyhound meeting
python scripts/greyhound_extract.py GEELONG_10Jul2026.pdf GEELONG_10Jul2026_FormGuide.xlsx
```

Each script prints a JSON summary (`races`, `runners`, `runs`) when it
finishes - use this to sanity-check extraction completeness (see Verification
below). `process_folder.py` prints this plus a completeness percentage per
file automatically.

## Running the downloader

```bash
pip install -r requirements.txt
playwright install chromium
python scripts/download_form_guides.py --list scripts/meetings.txt
```

Or `download.bat` on Windows, which also creates `scripts/meetings.txt` from
the template on first run and opens it in Notepad for editing.

The script's `ENHANCED_PDF_SELECTORS` list was written from a screenshot, not
live authenticated access - if it can't find the button on a real page, it
says so explicitly (page title + "could not find" message) rather than
guessing. Direct the user to `playwright codegen` against an authenticated
session to get the real selector, then add it to that list - don't hand-guess
new selectors without evidence from the live page.

## Output structure

Every workbook has:

1. **Race Summary** - one row per race: time, venue, distance, class,
   prizemoney, race name, runner count.
2. **R1, R2, ... Rn** - one tab per race, one row per current runner: tab
   number, name, recent form figures, age/sex, weight, barrier/box,
   jockey+claim (thoroughbred only), trainer, career W-P-S, career prize,
   RTC/DLR/DLW.
3. **Run History** - the deep data. One row per PAST run per runner:
   finish position, field size, date, track, margin, distance, track
   condition, class, race name, prize, API, race time, sectional time(s),
   jockey/weight/CD (thoroughbred) or just box (greyhound), odds, prize won,
   trainer, trainer's ongoing win record, track direction, rail/gear change
   (thoroughbred), winner/second/third with box/weight, and a raw "Settled"
   string.

The "Settled" field is deliberately left as raw text (e.g. "1st 1200m 2nd
800m 2nd Turn 2nd") rather than split into fixed columns - different track
distances report a different number of sectional checkpoints, and forcing a
fixed schema silently drops data for tracks with extra or fewer checkpoints.
If the user needs specific checkpoints split out, ask which ones they care
about (800m/Turn only vs also 1200m) before writing a parser for it - don't
guess a schema.

## Verification (do this every time)

Before handing a workbook to the user, check extraction completeness. Both
parser scripts define a run-start pattern (the raw "Nth of M date" marker) -
compare the script's reported run count against an independent raw count:

```python
import re
raw_count = len(re.findall(r'\d+(?:st|nd|rd|th) of \d+ \d{1,2}/\d{1,2}/\d{4}',
                            full_pdf_text))
```

`process_folder.py` does this automatically and flags any file under ~99.5%
as `*** INCOMPLETE ***` in its console output - check for that flag before
telling the user extraction succeeded.

Known failure modes already handled by both parser scripts (don't re-solve
these from scratch if you see them again on a new sample):

- Odds with trailing letters ("2.3EF", "0.65F", "0.08F" - favourite/equal
  markers)
- Missing "Sec Time" or "Odds" fields entirely for some runs
- PDF line-wrap splitting a large win-place-start record across 3 lines
  (`fix_wrapped_runner_rows`)
- A runner's name coincidentally appearing as another runner's past-race
  winner, causing a false block-boundary match (banner detection requires a
  same-line marker like "Horse:", "j50s", or an all-caps line - not just a
  name-prefix match)
- Form-figure prefixes containing 'f' (not just digits/'x') on the runner
  name

Neither parser script currently writes Excel formulas - all values are
computed in Python and written as literals, which is intentional here since
this is a one-way data extraction, not a live model. No formula-error check
is needed.

## Other sites considered and rejected as automation targets

thegreyhoundrecorder.com.au was evaluated as a possible alternative to R&S
(it has no Cloudflare wall and excellent structured "Long Form" race pages -
ratings, full run history, trainer stats). It is NOT a viable target: their
Terms of Use clause 18 explicitly prohibits automated collection by any means
("robot, spider, script, service, software or any manual or automatic device,
tool or process") and explicitly states this isn't limited by robots.txt
either way. This is a flat legal/policy prohibition, not a technical one, so
there's no implementation approach (Playwright, requests, anything else) that
makes scraping this site acceptable. Don't reconsider this site as a target
without the user obtaining express written permission from the publisher, as
their own terms specify.

## Automating the pipeline on a server (n8n)

`process_folder.py` moves each PDF from `input/` into `input/processed/` (on
success) or `input/failed/` (on error) after handling it - this makes repeated
calls idempotent, which is what makes it safe to trigger from a scheduler
instead of a human. `n8n-workflow.json` is an importable n8n workflow: a Cron
trigger calls `process_folder.py` on a schedule via Execute Command, then
branches on whether any file in the output was flagged `*** INCOMPLETE ***`.

This only automates the parse-and-store half of the pipeline. The download
half (getting PDFs from R&S in the first place) cannot be automated end to
end - see the Bot-detection boundary section above. The realistic pattern for
a user running this on their own server: download PDFs manually/semi-
automated (with the human-in-the-loop steps already described) on a machine
with a real browser, sync that folder to the server, let n8n handle
everything from "PDF exists on disk" onward.

## What this skill does NOT do

- **Does not solve Cloudflare or any other bot-detection, ever, under any
  framing.** See "Bot-detection boundary" above.
- **Does not give betting advice.** This is a data-extraction tool. Analysis,
  ratings, and picks are a separate concern from the user.
- Respect R&S's Terms of Use: content is for personal, non-commercial use.
  Don't redistribute extracted data or PDFs to third parties.
