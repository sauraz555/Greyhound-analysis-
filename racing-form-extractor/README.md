# Racing Form Extractor

Turns Racing And Sports (racingandsports.com.au) "Feature Form" Enhanced PDF
form guides into structured Excel workbooks - race cards, runner fields, and
full past-run history - for both thoroughbred and greyhound meetings.

## What it does

Each PDF (one racing meeting, multiple races) becomes one `.xlsx` workbook:

- **Race Summary** tab - every race at a glance (time, venue, distance,
  class, prizemoney, field size).
- **R1...Rn** tabs - one per race, one row per current runner (form figures,
  weight, barrier/box, jockey + trainer, career record).
- **Run History** tab - the deep data: one row per *past run* for every
  runner in the meeting. Finish position, margin, sectional times, class,
  race name, jockey/trainer, odds, prize won, winner/placegetters, and
  settling position.

## Why two parser scripts

Thoroughbred and greyhound Feature Form PDFs share a template but differ in
ways that matter for parsing:

| | Thoroughbred | Greyhound |
|---|---|---|
| Jockey field | Yes (glued to trainer name, no delimiter) | No - trainer only |
| Weight | Real values | Always `0.0kg` (irrelevant) |
| Barrier label | Barrier | Box |
| Run-history extras | Weight, CD, Rail, Gear Change | - |

`scripts/horse_extract.py` and `scripts/greyhound_extract.py` share the same
architecture (race-boundary detection, per-runner block splitting, run-history
regex) but each handles its code's specific fields. Don't try to force one
script to handle both - that was tried and produces silent data loss.

`scripts/process_folder.py` sits on top of both: it detects each PDF's code
automatically and dispatches to the right one, so you never have to sort your
PDFs by code yourself.

## Getting the PDFs: two ways

### 1. Manual download (simplest, always works)

1. Go to the meeting's form guide page on racingandsports.com.au
2. Open the **PDF / Data Download** tab
3. Download the **Enhanced PDF** (has run-by-run detail; the "Brief PDF" does
   not have enough detail for the Run History tab to be useful)
4. Drop it in the `input` folder

### 2. Semi-automated download (`download.bat` / `scripts/download_form_guides.py`)

racingandsports.com.au runs Cloudflare bot-detection on these pages. This
script does not and will not solve that challenge for you - it opens a real,
visible browser window and waits for **you** to log in and click through any
"Verify you are human" check yourself. Once you confirm you're through, it
reuses that same browser session to open each meeting's PDF/Data Download
page and click Enhanced PDF automatically, saving straight into `input/`.

Setup (first time only):
```bash
pip install -r requirements.txt
playwright install chromium
```

Usage: edit `scripts/meetings.txt` (copy `scripts/meetings.example.txt` if it
doesn't exist yet - one meeting URL per line) and run `download.bat`, or:
```bash
python scripts/download_form_guides.py --list scripts/meetings.txt
```

Things to know before relying on this:

- **It cannot get past Cloudflare on its own, ever.** If the challenge
  reappears on a later page - which can happen if R&S's check is per-page or
  your session expires - the script stops and asks you to solve it again in
  the same window. It will not retry against the challenge itself.
- **Selectors may need adjustment.** The "Enhanced PDF" button-finder was
  written from a screenshot, not live authenticated access (that page is
  behind the same login + Cloudflare wall this script doesn't bypass). If it
  can't find the button, it tells you exactly what it saw and points you at
  `playwright codegen` to get the right selector - see the script's
  docstring for the full instructions. It will not guess and download the
  wrong file.
- Your login session is cached in `scripts/playwright-profile/` so you
  shouldn't need to log in every single run - only when the session expires
  or R&S re-challenges you.

## Quick start (Windows, no command line needed)

1. Get PDFs into the `input` folder (manually, or via `download.bat`).
2. Double-click `run.bat`.
3. Collect the `.xlsx` workbooks from the `output` folder.

`run.bat` checks for Python, installs dependencies if missing, then runs
`scripts/process_folder.py` against `input/` and `output/`. It auto-detects
each PDF's racing code (thoroughbred vs greyhound) by checking the weight
column, so you can drop both kinds in the same folder. It also prints a
completeness check for every file - races/runners/run-history rows found,
and the run-history row count against an independent raw count from the PDF,
flagging anything under ~99.5% as `*** INCOMPLETE ***` so a bad parse never
ships silently. One broken PDF won't stop the rest of the batch.

## Quick start (command line / any OS)

```bash
pip install -r requirements.txt

# batch mode - process every PDF in a folder, auto-detects code
python scripts/process_folder.py input_dir output_dir

# single file, code-specific
python scripts/horse_extract.py     MEETING.pdf output.xlsx   # thoroughbred
python scripts/greyhound_extract.py MEETING.pdf output.xlsx   # greyhound
```

Each single-file run prints a JSON summary: `{"races": N, "runners": N, "runs": N}`.

R&S's Terms of Use permit personal, non-commercial download and viewing -
don't redistribute the PDFs or the extracted data.

## Running unattended on a Linux server (n8n)

Once PDFs exist on disk, everything downstream can run with zero human
involvement. `process_folder.py` was made idempotent for exactly this: it
moves each PDF into `input/processed/` (on success) or `input/failed/` (on
error) after handling it, so a scheduler can call it repeatedly and it will
only ever touch files that are new.

Setup:

1. Unzip this package on the server, e.g. `/opt/racing-form-extractor`.
2. `pip install -r requirements.txt`
3. Get PDFs onto the server's `input/` folder. Since the Cloudflare download
   step has to stay manual (see above), the practical pattern is: download on
   a machine where you have a real browser, then sync that folder to the
   server's `input/` - `rsync`, Syncthing, a shared network mount, whatever
   you're already using. This script doesn't care how the PDFs arrive, only
   that they land in `input/`.
4. Import `n8n-workflow.json` into n8n (Workflows -> Import from File).
5. Open the "Run process_folder.py" node and fix the path in the command to
   wherever you actually unzipped the package in step 1.
6. Wire the "Any file flagged INCOMPLETE?" node's true branch to however you
   want to be notified (email, Slack, ntfy, whatever n8n integration you
   already use) - this isn't included because it depends on what you have
   set up. The workflow runs fine without it; you'd just have to check the
   execution log manually to see if anything needs attention.
7. Activate the workflow. Default schedule is every 15 minutes - change the
   "Every 15 Minutes" node if you want a different interval.

What this does and doesn't get you: the parse-and-store half becomes fully
unattended, running on a schedule with no one watching it. The download half
does not become unattended - it can't, both racingandsports.com.au
(Cloudflare) and thegreyhoundrecorder.com.au (explicit ToS prohibition on
automated collection - see below) put a hard stop on that. Automating the
50% of the pipeline that's legitimately automatable is still a real win over
doing all of it by hand.

## Why thegreyhoundrecorder.com.au isn't a workaround

It might look like an easier target than R&S - no Cloudflare challenge, and
the "Long Form" pages have excellent structured data (ratings, full run
history, trainer stats, sectional times). But their Terms of Use (clause 18)
explicitly prohibit automated collection - not a robots.txt technicality, a
plainly stated ban that explicitly says robots.txt doesn't limit or expand
it: "You shall not... access, collect, text or data mine any content...
by automated means or any other method... (e.g., robot, spider, script,
service, software or any manual or automatic device, tool or process)." This
skill doesn't include anything that automates that site, and extending it to
do so isn't a good idea regardless of technique (Playwright, requests,
anything else) - the block here is legal/policy, not technical, so there's
no clever implementation that makes it fine.

## Verifying extraction completeness

Both parser scripts are regex-based and the PDF layout has real quirks (line
wraps, inconsistent field presence, occasional glitches like "0.65F" odds).
Every fix made so far came from comparing the reported run count against an
independent raw count of the "Nth of M date" run markers in the PDF text -
see `SKILL.md` for the verification snippet and the list of known failure
modes already handled. `process_folder.py` runs this check automatically per
file. If you extend this to a new sample PDF and the run count comes up
short, check that list before re-deriving a fix.

## Files

```
racing-form-extractor/
├── README.md                  - this file
├── SKILL.md                    - skill manifest (for Claude agents using this as a skill)
├── requirements.txt
├── run.bat                     - Windows one-click launcher: process PDFs into spreadsheets
├── download.bat                - Windows one-click launcher: semi-automated PDF download
├── input/                      - drop your PDFs here
├── output/                     - workbooks land here
└── scripts/
    ├── horse_extract.py        - thoroughbred parser
    ├── greyhound_extract.py    - greyhound parser
    ├── process_folder.py       - batch driver: auto-detects code, runs the right
    │                              parser on every PDF in input/, writes to output/
    ├── download_form_guides.py - semi-automated downloader (manual login/Cloudflare,
    │                              automated navigation + click after that)
    └── meetings.example.txt    - template for scripts/meetings.txt
```
