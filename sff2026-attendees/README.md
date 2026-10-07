# SFF 2026 attendee list downloader

Downloads the full attendee list from the Jublia event app
(`https://e.jublia.com/SFF2026/...`) into `attendees.csv` and `attendees.json`.

## How it works

The website loads attendees 25 at a time. Each batch is one POST request to:

```
https://e.jublia.com/SFF2026/people/populate_list/<page>
```

The body is the same every time, except `"page"` (it matches the number at
the end of the URL). The site never says how many pages there are. So the tools
here ask for page 0, 1, 2, 3, ... and stop once 2 pages in a row bring
**no new people**. You don't need to know the last page number.

Other details:

- **Duplicates are removed.** Each person is tracked by their ID (or their
  full record), so if a page repeats, nobody is counted twice.
- **Any response shape works.** The server might send JSON, JSON with HTML
  inside, or plain HTML. The tools handle all three. They find the people list
  on the first page and read the same spot on every later page.
- **A short pause between pages** (0.5 s) keeps the load on the server low.

## Option A: browser console (easiest, no install)

1. Log in at https://e.jublia.com/SFF2026 and open the attendee list.
2. Open DevTools: press `F12` (or `Cmd+Option+J` on a Mac) and click **Console**.
3. Paste everything in [`fetch_attendees_console.js`](fetch_attendees_console.js) and press Enter.
   Chrome may ask you to type `allow pasting` first.
4. Watch the progress lines (`page 12: ... total 300`). When it finishes, the
   browser downloads `attendees.csv` and `attendees.json`.

This runs inside your logged-in tab, so it reuses your login automatically.

## Option B: Python script (good for re-running)

Needs Python 3.8+ and nothing else.

```bash
python3 fetch_attendees.py
```

If the list needs a login (likely), give the script a copy of a real request
from your browser:

1. Open the attendee list while logged in. Open DevTools > **Network**.
2. Scroll the list so it loads more people. Find the `populate_list/...` request.
3. Right-click it > **Copy** > **Copy as cURL (bash)**. On Windows, pick the
   **bash** version, not "cmd".
4. Paste it into a file named `request.txt` in this folder.
5. Run:

```bash
python3 fetch_attendees.py --curl request.txt
```

The script reuses your cookies, headers and body from that request and only
changes the page number. If you had filters on in the browser, they are kept.

Results go to `output/attendees.csv` and `output/attendees.json`. Every raw
server response is also saved in `output/raw/`, so nothing is lost if a column
looks odd.

Useful options:

| Option | What it does |
| --- | --- |
| `--row 100` | Ask for 100 people per page instead of 25 (fewer requests, if the server allows it) |
| `--delay 1` | Wait longer between pages |
| `--out somewhere` | Save results in a different folder |
| `--event OTHER2026` | Another Jublia event |

Press `Ctrl+C` at any time. It saves what it has so far.

## Troubleshooting

- **"got a web page instead of a list" / "Are you logged in?"**: your login
  has expired, or there wasn't one. Log in again. For Option B, copy a fresh
  `request.txt`.
- **"No people found"**: the response came in a shape the tools didn't
  expect. Look at `output/raw/page_0001.txt` (or the text printed in the
  console). That shows exactly what the server sent.

## Privacy

- `request.txt` contains your login cookie. It is like a temporary
  password, so don't share it. It is git-ignored, along with `output/`.
- Use the attendee data in line with the event's terms.
