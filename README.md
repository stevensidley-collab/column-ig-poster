# column-ig-poster

Local Streamlit tool that turns a Substack column URL into an Instagram-ready
1080x1350 image + caption, and keeps a permanent "link in bio" redirect
(served via GitHub Pages from `/docs`) pointing at the latest column.
Posting to Instagram itself is manual — this app has no Instagram API integration.

## Setup

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Git pushes for the bio redirect use your existing `gh`/git credentials on this
machine — no separate token needed.

## Run

```bash
.venv/bin/streamlit run app/main.py
```

## Workflow

1. Paste a Substack column URL and click "Fetch column".
2. Optionally add extra subtitle text; edit the auto-extracted teaser and caption.
3. Click "Generate image" to preview the 1080x1350 composite.
4. "Save image + caption to /output" writes the `.jpg`/`.txt` locally and appends
   a record to `posts_history.json`.
5. "Update bio redirect and push" writes the column URL to `docs/redirect.json`
   and commits/pushes so `https://stevensidley-collab.github.io/column-ig-poster/`
   redirects to it.
6. Post the image/caption to Instagram manually.

## Repo layout

- `app/` — Streamlit app (`main.py`), fetch/parse, image generation, caption, redirect push
- `docs/` — GitHub Pages redirect site (the permanent Instagram bio link)
- `output/` — generated images/captions (gitignored)
- `posts_history.json` — log of past posts (title, date, URL)
