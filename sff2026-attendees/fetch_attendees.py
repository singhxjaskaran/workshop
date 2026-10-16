#!/usr/bin/env python3
"""Download the full SFF 2026 attendee list from Jublia.

The attendee list on e.jublia.com loads 25 people at a time. Each batch is a
POST to .../people/populate_list/<page>. Nobody tells us how many pages there
are, so this script keeps asking for the next page until the server stops
sending people it has not seen before. Then it saves everyone to CSV and JSON.

Usage:
    python3 fetch_attendees.py                     # try without logging in
    python3 fetch_attendees.py --curl request.txt  # reuse your browser login

No extra packages needed. See README.md for how to make request.txt.
"""

import argparse
import csv
import json
import re
import shlex
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qsl, urlencode, urljoin
from urllib.request import Request, urlopen

DEFAULT_PAYLOAD = {
    "type": "people", "in": "", "attribute_ids": {}, "free_texts": [],
    "sched_date": "", "AZ": "", "map_marker": "", "row": 25,
    "is_exact_search": False, "page": 0, "search_id": "", "person_group_id": "",
}
DEFAULT_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0 Safari/537.36",
}
# Headers from a copied curl command that urllib must not resend as-is.
DROP_HEADERS = {"accept-encoding", "content-length", "host", "connection"}
# Fields that identify a person, used to skip people we already have.
ID_KEYS = ("id", "person_id", "user_id", "attendee_id", "uuid", "_id",
           "encrypted_id", "data-id", "data-person-id", "data-user-id")
NAME_KEYS = {"name", "full_name", "fullname", "first_name", "firstname", "last_name",
             "lastname", "display_name", "given_name", "family_name"}
# Columns shown first in the CSV when they exist.
FRONT_COLUMNS = ["name", "full_name", "first_name", "last_name", "job_title", "title",
                 "designation", "position", "company", "company_name",
                 "organisation", "organization", "country"]


# ---------------------------------------------------------------- request setup

def parse_curl(text):
    """Pull the URL, headers and body out of a 'Copy as cURL (bash)' command."""
    tokens = shlex.split(text.replace("\\\n", " "))
    url, headers, body = None, {}, None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if tok in ("-H", "--header"):
            name, _, value = nxt.partition(":")
            headers[name.strip().lower()] = value.strip()
            i += 1
        elif tok in ("-b", "--cookie"):
            headers["cookie"] = nxt
            i += 1
        elif tok in ("-A", "--user-agent"):
            headers["user-agent"] = nxt
            i += 1
        elif tok in ("-e", "--referer"):
            headers["referer"] = nxt
            i += 1
        elif tok in ("-d", "--data", "--data-raw", "--data-binary", "--data-ascii"):
            body = nxt
            i += 1
        elif tok in ("-X", "--request"):
            i += 1
        elif tok.startswith("http"):
            url = tok
        i += 1
    headers = {k: v for k, v in headers.items()
               if k not in DROP_HEADERS and not k.startswith(":")}
    return url, headers, body


def parse_body(body):
    """Turn the browser's request body into a template we can change the page in."""
    for candidate in (body, body.lstrip("$")):  # Chrome sometimes writes $'...'
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except ValueError:
            pass
    return parse_qsl(body, keep_blank_values=True)  # form-encoded body


def build_body(template, page, row):
    """Same body the browser sends, with only the page (and maybe row) changed."""
    if isinstance(template, dict):
        data = dict(template, page=page)
        if row:
            data["row"] = row
        return json.dumps(data).encode(), "application/json"
    pairs = []
    for key, value in template:
        if key == "page":
            value = str(page)
        elif key == "row" and row:
            value = str(row)
        pairs.append((key, value))
    return urlencode(pairs).encode(), "application/x-www-form-urlencoded; charset=UTF-8"


def post(url, body, headers, tries=4):
    """POST with a few retries. Returns (status, final_url, text)."""
    for attempt in range(tries):
        try:
            req = Request(url, data=body, headers=headers, method="POST")
            with urlopen(req, timeout=30) as resp:
                return resp.status, resp.geturl(), resp.read().decode("utf-8", "replace")
        except HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return err.code, url, err.read().decode("utf-8", "replace")
        except OSError:  # network error or timeout
            if attempt == tries - 1:
                raise
            time.sleep(2 ** (attempt + 1))


# ------------------------------------------------------------ reading responses

def looks_like_people(items):
    """A list of records with a name field and at least 4 fields in total.

    This skips small lists such as filters ({"id": 1, "label": "Fintech"}).
    """
    if not items or not all(isinstance(x, dict) for x in items):
        return False
    keys = {k for item in items for k in flatten(item)}
    return len(keys) >= 4 and any(k.rsplit(".", 1)[-1].lower() in NAME_KEYS for k in keys)


def find_people_path(data):
    """Find where in the JSON the biggest list of people sits.

    Returns a path such as ("data", "people"), or None.
    """
    best, best_len = None, 0
    stack = [((), data)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, dict):
            stack.extend((path + (k,), v) for k, v in node.items())
        elif isinstance(node, list):
            stack.extend((path + (i,), v) for i, v in enumerate(node))
            if len(node) > best_len and looks_like_people(node):
                best, best_len = path, len(node)
    return best


def get_path(data, path):
    for step in path:
        try:
            data = data[step]
        except (KeyError, IndexError, TypeError):
            return None
    return data


def find_html(data):
    """Find the longest string inside the JSON that looks like HTML."""
    best = ""
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, str) and re.search(r"<[a-zA-Z]", node) and len(node) > len(best):
            best = node
    return best


def flatten(obj, prefix=""):
    """Turn nested JSON into flat columns, e.g. {"company": {"name": X}} -> company.name."""
    row = {}
    for key, value in obj.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            row.update(flatten(value, name + "."))
        elif isinstance(value, list):
            if all(not isinstance(v, (dict, list)) for v in value):
                row[name] = "; ".join(str(v) for v in value)
            else:
                row[name] = json.dumps(value, ensure_ascii=False)
        else:
            row[name] = value
    return row


class Node:
    __slots__ = ("tag", "attrs", "kids", "up")

    def __init__(self, tag, attrs, up):
        self.tag, self.attrs, self.kids, self.up = tag, attrs, [], up


class TreeBuilder(HTMLParser):
    """Tiny HTML-to-tree parser, so we don't need BeautifulSoup."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("#root", {}, None)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: v or "" for k, v in attrs}, self.cur)
        self.cur.kids.append(node)
        if tag not in self.VOID:
            self.cur = node

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.up
        if node is not self.root:
            self.cur = node.up

    def handle_data(self, data):
        if self.cur.tag not in ("script", "style") and data.strip():
            self.cur.kids.append(data)


def elements(node):
    for kid in node.kids:
        if isinstance(kid, Node):
            yield kid
            yield from elements(kid)


def texts_in(node):
    """Yield (text, element that holds the text) for every text inside node."""
    for kid in node.kids:
        if isinstance(kid, str):
            yield kid, node
        else:
            yield from texts_in(kid)


def signature(node):
    return f"{node.tag}.{node.attrs.get('class', '')}"


class CardParser:
    """Turns an HTML list of people into one row per person "card".

    We don't know Jublia's HTML in advance. On a list page, the people cards
    are the biggest group of sibling elements that share the same tag and
    class. We learn that pattern on the first full page, then reuse it, so a
    last page with only one person still parses correctly.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.card_key = None

    def __call__(self, html):
        tree = TreeBuilder()
        tree.feed(html)
        tree.close()
        key = lambda el: (signature(el.up), signature(el))
        if self.card_key:
            cards = [el for el in elements(tree.root) if key(el) == self.card_key]
        else:
            cards = []
            for parent in [tree.root, *elements(tree.root)]:
                groups = {}
                for kid in parent.kids:
                    if isinstance(kid, Node) and any(t.strip() for t, _ in texts_in(kid)):
                        groups.setdefault(signature(kid), []).append(kid)
                for group in groups.values():
                    if len(group) > len(cards):
                        cards = group
            if len(cards) < 2:
                return []
            self.card_key = key(cards[0])
        return [self.card_row(card) for card in cards]

    def card_row(self, card):
        """One row per card.

        Each text goes in a column named after the element that holds it: its
        class (e.g. "job-title"), or its tag if it has no class (e.g. "h4").
        Naming columns this way keeps them lined up when a person is missing a
        field. "name" is a best guess: the first text on the card.
        """
        name, fields, links, images = "", {}, [], []
        for text, holder in texts_in(card):
            text = " ".join(text.split())
            if not text:
                continue
            name = name or text
            if holder is card:
                key = "text"
            else:
                key = " ".join(holder.attrs.get("class", "").split()) or holder.tag
            values = fields.setdefault(key, [])
            if text not in values:
                values.append(text)
        for el in elements(card):
            href = el.attrs.get("href", "")
            if el.tag == "a" and href and not href.startswith(("#", "javascript:")):
                links.append(urljoin(self.base_url, href))
            if el.tag == "img":
                src = el.attrs.get("data-src") or el.attrs.get("src")
                if src:
                    images.append(urljoin(self.base_url, src))
        row = {"name": name}
        for key, values in fields.items():
            if key in ("name", "links", "image") or key.startswith("data-"):
                key = f"text_{key}"  # don't clash with the columns set here
            row[key] = "; ".join(values)
        row.update({k: v for k, v in card.attrs.items() if k.startswith("data-")})
        row["links"] = " ".join(dict.fromkeys(links))
        row["image"] = images[0] if images else ""
        return row


def is_full_page(text):
    """A whole web page (usually the login page) instead of a list."""
    head = text[:2000]
    return not head.lstrip().startswith(("{", "[")) and bool(re.search(r"<html[\s>]|<!doctype", head, re.I))


class PeopleExtractor:
    """Returns a list of person rows from one API response, whatever its shape.

    Like CardParser, it learns where the people list sits on the first page
    that has people, and only reads from there afterwards. Otherwise an empty
    last page could make some other list in the response look like people.
    """

    def __init__(self, base_url):
        self.cards = CardParser(base_url)
        self.json_path = None

    def __call__(self, text):
        try:
            data = json.loads(text)
        except ValueError:
            data = None
        if data is not None:
            if self.json_path is None:
                self.json_path = find_people_path(data)
            if self.json_path is not None:
                people = get_path(data, self.json_path)
                if not isinstance(people, list):
                    return []
                return [flatten(p) for p in people if isinstance(p, dict)]
            html = find_html(data)
            return self.cards(html) if html else []
        return [] if is_full_page(text) else self.cards(text)


def person_key(row):
    for key in ID_KEYS:
        if row.get(key) not in (None, ""):
            return f"{key}={row[key]}"
    return json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------- output

def save(people, out_dir):
    columns = []
    for row in people:
        for key in row:
            if key not in columns:
                columns.append(key)
    columns.sort(key=lambda c: FRONT_COLUMNS.index(c) if c in FRONT_COLUMNS else len(FRONT_COLUMNS))
    # utf-8-sig so Excel shows accented names correctly.
    with open(out_dir / "attendees.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(people)
    (out_dir / "attendees.json").write_text(
        json.dumps(people, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# ------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--curl", help="file with a request copied from DevTools as 'Copy as cURL (bash)'")
    ap.add_argument("--event", default="SFF2026", help="event code in the URL (default: SFF2026)")
    ap.add_argument("--base-url", help="override the full .../populate_list URL")
    ap.add_argument("--row", type=int, help="people per page (default: whatever the browser sent, 25)")
    ap.add_argument("--start-page", type=int, default=0, help="first page to ask for (default: 0)")
    ap.add_argument("--max-pages", type=int, default=5000, help="safety limit (default: 5000)")
    ap.add_argument("--patience", type=int, default=2,
                    help="stop after this many pages in a row with no new people (default: 2)")
    ap.add_argument("--delay", type=float, default=0.5, help="seconds to wait between pages (default: 0.5)")
    ap.add_argument("--out", default="output", help="folder to write results to (default: output)")
    args = ap.parse_args()

    base = args.base_url or f"https://e.jublia.com/{args.event}/people/populate_list"
    headers = dict(DEFAULT_HEADERS)
    template = dict(DEFAULT_PAYLOAD)
    if args.curl:
        url, curl_headers, body = parse_curl(Path(args.curl).read_text(encoding="utf-8"))
        if url and not args.base_url:
            base = re.sub(r"/\d+/?(\?.*)?$", "", url)
        headers.update(curl_headers)
        if body:
            template = parse_body(body)
    base = base.rstrip("/")
    origin = re.match(r"https?://[^/]+", base).group(0)
    headers.setdefault("origin", origin)
    headers.setdefault("referer", base.replace("/populate_list", ""))

    out_dir = Path(args.out)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    extract_people = PeopleExtractor(origin)
    seen, people, quiet = set(), [], 0
    text = ""
    print(f"Fetching from {base}/<page>")
    try:
        for page in range(args.start_page, args.start_page + args.max_pages):
            body, content_type = build_body(template, page, args.row)
            status, final_url, text = post(f"{base}/{page}", body, {"content-type": content_type, **headers})
            (raw_dir / f"page_{page:04d}.txt").write_text(text, encoding="utf-8")

            redirected = final_url != f"{base}/{page}"
            if status in (401, 403, 419) or redirected or is_full_page(text):
                print(f"page {page}: HTTP {status}, got a web page instead of a list"
                      + (f" (redirected to {final_url})" if redirected else ""))
                print("The server wants you logged in. Use --curl with a request copied "
                      "from your browser (see README.md).")
                break

            rows = extract_people(text) if status == 200 else []
            new = 0
            for row in rows:
                key = person_key(row)
                if key not in seen:
                    seen.add(key)
                    people.append(row)
                    new += 1
            print(f"page {page}: HTTP {status}, {len(rows)} people, {new} new, total {len(people)}")

            quiet = 0 if new else quiet + 1
            if quiet >= args.patience:
                break
            time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\nStopped early. Saving what we have so far.")
    finally:
        save(people, out_dir)

    print(f"\nSaved {len(people)} people to {out_dir / 'attendees.csv'} and {out_dir / 'attendees.json'}")
    print(f"Raw server responses are in {raw_dir}/")
    if not people:
        print("\nNo people found. Start of the last response, to help see what went wrong:")
        print(text[:500])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
