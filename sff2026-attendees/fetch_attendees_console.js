// SFF 2026 attendee downloader.
//
// How to use: log in at https://e.jublia.com/SFF2026, open the attendee list,
// open DevTools (F12) > Console, paste this whole file, press Enter.
// It asks for page 0, 1, 2, ... until the server stops sending new people,
// then downloads attendees.csv and attendees.json.
//
// It runs inside your logged-in tab, so your login is reused automatically.
(async () => {
  const EVENT = 'SFF2026';
  const BASE = `${location.origin}/${EVENT}/people/populate_list`;
  const ROW = 25;          // people per page, same as the website
  const DELAY_MS = 500;    // pause between pages, to be gentle on the server
  const PATIENCE = 2;      // stop after this many pages in a row with no new people
  const MAX_PAGES = 5000;  // safety limit
  const PAYLOAD = {
    type: 'people', in: '', attribute_ids: {}, free_texts: [], sched_date: '', AZ: '',
    map_marker: '', row: ROW, is_exact_search: false, page: 0, search_id: '', person_group_id: '',
  };
  const ID_KEYS = ['id', 'person_id', 'user_id', 'attendee_id', 'uuid', '_id',
    'encrypted_id', 'data-id', 'data-person-id', 'data-user-id'];
  const NAME_KEYS = ['name', 'full_name', 'fullname', 'first_name', 'last_name', 'display_name'];
  const FRONT_COLUMNS = ['name', 'full_name', 'first_name', 'last_name', 'job_title', 'title',
    'designation', 'position', 'company', 'company_name', 'organisation', 'organization', 'country'];

  if (location.hostname !== 'e.jublia.com') {
    console.warn(`You are on ${location.hostname}. Run this on an e.jublia.com tab.`);
  }

  // Some sites need a CSRF token (an anti-forgery code) on every POST.
  const csrfMatch = document.cookie.match(/(?:^|;\s*)(?:csrftoken|csrf_token|XSRF-TOKEN)=([^;]+)/);
  const csrf = document.querySelector('meta[name="csrf-token"], meta[name="csrf_token"], meta[name="_csrf"]')
    ?.content || (csrfMatch && decodeURIComponent(csrfMatch[1]));
  const headers = { 'Accept': 'application/json, text/javascript, */*; q=0.01' };
  if (csrf) headers['X-CSRFToken'] = headers['X-CSRF-Token'] = csrf;

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // Prefer the site's own jQuery: it carries any extra headers the site adds to its requests.
  function postOnce(url, body) {
    const $ = window.jQuery;
    if ($ && $.ajax) {
      return new Promise(resolve => $.ajax({
        url, type: 'POST', data: body, contentType: 'application/json', dataType: 'text', headers,
        success: (text, _s, xhr) => resolve({ status: xhr.status, text }),
        error: xhr => resolve({ status: xhr.status, text: xhr.responseText || '' }),
      }));
    }
    return fetch(url, {
      method: 'POST', credentials: 'include', body,
      headers: { ...headers, 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
    }).then(async res => ({ status: res.status, text: await res.text(), redirected: res.redirected }));
  }

  async function post(url, body) {
    for (let attempt = 1; ; attempt++) {
      try {
        const res = await postOnce(url, body);
        if (![429, 500, 502, 503, 504].includes(res.status) || attempt >= 4) return res;
      } catch (err) {
        if (attempt >= 4) throw err;
      }
      await sleep(2000 * 2 ** (attempt - 1));
    }
  }

  // ---- reading responses: JSON list, JSON with HTML inside, or plain HTML ----

  const isRecord = x => x !== null && typeof x === 'object' && !Array.isArray(x);

  // A list of records with a name field and at least 4 fields in total.
  // This skips small lists such as filters ({id: 1, label: 'Fintech'}).
  function looksLikePeople(items) {
    if (!items.length || !items.every(isRecord)) return false;
    const keys = new Set(items.flatMap(item => Object.keys(flatten(item))));
    return keys.size >= 4 && [...keys].some(k => NAME_KEYS.includes(k.split('.').pop().toLowerCase()));
  }

  // Where in the JSON the biggest list of people sits, e.g. ['data', 'people'].
  function findPeoplePath(data) {
    let best = null, bestLen = 0;
    const stack = [[[], data]];
    while (stack.length) {
      const [path, node] = stack.pop();
      if (Array.isArray(node)) {
        node.forEach((v, i) => stack.push([[...path, i], v]));
        if (node.length > bestLen && looksLikePeople(node)) { best = path; bestLen = node.length; }
      } else if (isRecord(node)) {
        for (const [k, v] of Object.entries(node)) stack.push([[...path, k], v]);
      }
    }
    return best;
  }

  function findHtml(data) {
    let best = '';
    const stack = [data];
    while (stack.length) {
      const node = stack.pop();
      if (Array.isArray(node)) stack.push(...node);
      else if (node && typeof node === 'object') stack.push(...Object.values(node));
      else if (typeof node === 'string' && /<[a-zA-Z]/.test(node) && node.length > best.length) best = node;
    }
    return best;
  }

  function flatten(obj, prefix = '') {
    const row = {};
    for (const [key, value] of Object.entries(obj)) {
      const name = prefix + key;
      if (Array.isArray(value)) {
        row[name] = value.every(v => v === null || typeof v !== 'object')
          ? value.join('; ') : JSON.stringify(value);
      } else if (value && typeof value === 'object') {
        Object.assign(row, flatten(value, name + '.'));
      } else {
        row[name] = value;
      }
    }
    return row;
  }

  // We don't know Jublia's HTML in advance. The people "cards" are the biggest
  // group of sibling elements sharing the same tag and class. We learn that
  // pattern on the first full page and reuse it on later pages.
  let cardKey = null;
  const signature = el => `${el.tagName}.${el.getAttribute('class') || ''}`;
  const keyOf = el => `${el.parentElement ? signature(el.parentElement) : ''}>${signature(el)}`;

  function cardsFromHtml(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    let cards;
    if (cardKey) {
      cards = [...doc.body.querySelectorAll('*')].filter(el => keyOf(el) === cardKey);
    } else {
      cards = [];
      for (const parent of [doc.body, ...doc.body.querySelectorAll('*')]) {
        const groups = {};
        for (const kid of parent.children) {
          if (kid.textContent.trim()) (groups[signature(kid)] ||= []).push(kid);
        }
        for (const group of Object.values(groups)) if (group.length > cards.length) cards = group;
      }
      if (cards.length < 2) return [];
      cardKey = keyOf(cards[0]);
    }
    return cards.map(cardRow);
  }

  function cardRow(card) {
    const texts = [];
    const walker = card.ownerDocument.createTreeWalker(card, NodeFilter.SHOW_TEXT);
    for (let n; (n = walker.nextNode());) {
      if (/^(SCRIPT|STYLE)$/.test(n.parentElement.tagName)) continue;
      const t = n.textContent.replace(/\s+/g, ' ').trim();
      if (t && !texts.includes(t)) texts.push(t);
    }
    const row = { name: texts[0] || '' };
    texts.slice(1).forEach((t, i) => { row[`line_${i + 2}`] = t; });
    for (const attr of card.attributes) if (attr.name.startsWith('data-')) row[attr.name] = attr.value;
    const links = [...card.querySelectorAll('a[href]')]
      .map(a => a.getAttribute('href'))
      .filter(h => !/^(#|javascript:)/.test(h))
      .map(h => new URL(h, location.origin).href);
    row.links = [...new Set(links)].join(' ');
    const img = card.querySelector('img');
    const src = img && (img.getAttribute('data-src') || img.getAttribute('src'));
    row.image = src ? new URL(src, location.origin).href : '';
    return row;
  }

  // Like the card pattern, the JSON path to the people list is learned on the
  // first page that has people. Otherwise an empty last page could make some
  // other list in the response look like people.
  let jsonPath = null;

  // A whole web page (usually the login page) instead of a list.
  const isFullPage = text => !/^\s*[{[]/.test(text) && /<html[\s>]|<!doctype/i.test(text.slice(0, 2000));

  function extractPeople(text) {
    let data = null;
    try { data = JSON.parse(text); } catch { /* not JSON */ }
    if (data !== null) {
      jsonPath ||= findPeoplePath(data);
      if (jsonPath) {
        const people = jsonPath.reduce((node, step) => (node == null ? undefined : node[step]), data);
        return Array.isArray(people) ? people.filter(isRecord).map(p => flatten(p)) : [];
      }
      const html = findHtml(data);
      return html ? cardsFromHtml(html) : [];
    }
    return isFullPage(text) ? [] : cardsFromHtml(text);
  }

  function personKey(row) {
    for (const k of ID_KEYS) if (row[k] !== undefined && row[k] !== null && row[k] !== '') return `${k}=${row[k]}`;
    return JSON.stringify(Object.keys(row).sort().map(k => [k, row[k]]));
  }

  // ---- output ----

  function toCsv(rows) {
    const cols = [];
    for (const r of rows) for (const k of Object.keys(r)) if (!cols.includes(k)) cols.push(k);
    const rank = c => (FRONT_COLUMNS.includes(c) ? FRONT_COLUMNS.indexOf(c) : FRONT_COLUMNS.length);
    cols.sort((a, b) => rank(a) - rank(b));
    const cell = v => {
      const s = v === null || v === undefined ? '' : String(v);
      return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    // The ﻿ mark makes Excel read accented names correctly.
    return '﻿' + [cols.map(cell).join(','), ...rows.map(r => cols.map(c => cell(r[c])).join(','))].join('\r\n');
  }

  function download(name, content, type) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  // ---- main loop ----

  const seen = new Set();
  const people = [];
  let quiet = 0, lastText = '';
  console.log(`Fetching from ${BASE}/<page>`);
  for (let page = 0; page < MAX_PAGES; page++) {
    const { status, text, redirected } = await post(`${BASE}/${page}`, JSON.stringify({ ...PAYLOAD, page }));
    lastText = text;
    if ([401, 403, 419].includes(status) || redirected || isFullPage(text)) {
      console.error(`page ${page}: HTTP ${status}, got a web page instead of a list. Are you logged in?`);
      break;
    }
    const rows = status === 200 ? extractPeople(text) : [];
    let added = 0;
    for (const row of rows) {
      const key = personKey(row);
      if (!seen.has(key)) { seen.add(key); people.push(row); added++; }
    }
    console.log(`page ${page}: HTTP ${status}, ${rows.length} people, ${added} new, total ${people.length}`);
    quiet = added ? 0 : quiet + 1;
    if (quiet >= PATIENCE) break;
    await sleep(DELAY_MS);
  }

  window.sffAttendees = people;
  if (!people.length) {
    console.error('No people found. Start of the last response:', lastText.slice(0, 500));
    return;
  }
  download('attendees.csv', toCsv(people), 'text/csv;charset=utf-8');
  download('attendees.json', JSON.stringify(people, null, 2), 'application/json');
  console.log(`Done: ${people.length} people. Saved attendees.csv and attendees.json. ` +
    'They are also in window.sffAttendees.');
})();
