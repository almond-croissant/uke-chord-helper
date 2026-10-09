(() => {
  const root = document.getElementById("song-section");
  const NS = "http://www.w3.org/2000/svg";
  const state = { id: null, transpose: 0, capo: 0 };
  let seq = 0, timer = null;

  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  };
  const sv = (tag, attrs) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  };

  root.innerHTML = `
    <h2>Songs</h2>
    <div class="song-layout">
      <aside><h3>Saved songs</h3><ul id="song-list"></ul></aside>
      <div class="song-main">
        <input id="song-title" placeholder="Song title">
        <textarea id="song-text" rows="12"
          placeholder="Paste a song. Either [Am]inline chords or chords on the line above the lyrics."></textarea>
        <div class="song-controls">
          <span>Transpose
            <button id="tr-down">&minus;</button>
            <b id="tr-val">0</b>
            <button id="tr-up">+</button></span>
          <span>Capo
            <button id="capo-down">&minus;</button>
            <b id="capo-val">0</b>
            <button id="capo-up">+</button></span>
          <button id="song-save">Save</button>
          <button id="song-new">New</button>
          <span id="song-status"></span>
        </div>
        <div id="song-note"></div>
        <div id="song-chart"></div>
        <div id="song-strip"></div>
      </div>
    </div>`;
  const $ = (id) => document.getElementById(id);

  function diagram(name, frets) {
    const card = el("div", "chord-card");
    card.append(el("div", "chord-name", name));
    if (!frets) { card.append(el("div", "chord-unknown", "no diagram")); return card; }
    const pos = frets.filter((f) => f > 0);
    const max = Math.max(0, ...pos);
    const base = max <= 4 ? 1 : Math.min(...pos);
    const rows = Math.max(4, max - base + 1);
    const x0 = 14, dx = 12, y0 = 18, dy = 16, W = 64, H = y0 + rows * dy + 6;
    const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H });
    for (let s = 0; s < 4; s++)
      svg.append(sv("line", { x1: x0 + s * dx, x2: x0 + s * dx, y1: y0, y2: y0 + rows * dy, stroke: "currentColor" }));
    for (let r = 0; r <= rows; r++)
      svg.append(sv("line", { x1: x0, x2: x0 + 3 * dx, y1: y0 + r * dy, y2: y0 + r * dy,
        stroke: "currentColor", "stroke-width": r === 0 && base === 1 ? 3 : 1 }));
    if (base > 1) {
      const t = sv("text", { x: 1, y: y0 + dy * 0.75, "font-size": 9, fill: "currentColor" });
      t.textContent = base; svg.append(t);
    }
    frets.forEach((f, s) => {
      const cx = x0 + s * dx;
      if (f === 0) svg.append(sv("circle", { cx, cy: 9, r: 3, fill: "none", stroke: "currentColor" }));
      else if (f > 0) svg.append(sv("circle", { cx, cy: y0 + (f - base + 0.5) * dy, r: 4.5, fill: "currentColor" }));
    });
    card.append(svg);
    return card;
  }

  function draw(data) {
    const chart = $("song-chart");
    chart.replaceChildren();
    for (const line of data.lines) {
      const row = el("div", "song-line");
      for (const seg of line) {
        const cell = el("span", "song-seg");
        cell.append(el("span", "song-chord", seg.chord || ""), el("span", "song-text", seg.text));
        row.append(cell);
      }
      chart.append(row);
    }
    const strip = $("song-strip");
    strip.replaceChildren();
    data.chords.forEach((c) => strip.append(diagram(c.name, c.frets)));
  }

  async function render() {
    const mine = ++seq;
    const res = await fetch("/api/song/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: $("song-text").value, transpose: state.transpose, capo: state.capo }),
    });
    if (!res.ok || mine !== seq) return;   // ignore failures and stale responses
    draw(await res.json());
  }

  function updateControls() {
    const t = state.transpose;
    $("tr-val").textContent = t > 0 ? `+${t}` : t;
    $("capo-val").textContent = state.capo;
    $("song-note").textContent = state.capo
      ? `Capo ${state.capo}: chords shown are the shapes to play.` : "";
    render();
  }

  const status = (msg) => { $("song-status").textContent = msg; };

  async function loadList() {
    const songs = await (await fetch("/api/songs")).json();
    const ul = $("song-list");
    ul.replaceChildren();
    if (!songs.length) ul.append(el("li", "muted", "Nothing saved yet"));
    for (const s of songs) {
      const li = el("li");
      const open = el("button", "link", s.title);
      open.onclick = () => openSong(s.id);
      const del = el("button", "del", "×");
      del.title = "Delete";
      del.onclick = async () => {
        if (!confirm(`Delete "${s.title}"?`)) return;
        await fetch(`/api/songs/${s.id}`, { method: "DELETE" });
        if (state.id === s.id) newSong();
        loadList();
      };
      li.append(open, del);
      ul.append(li);
    }
  }

  async function openSong(id) {
    const s = await (await fetch(`/api/songs/${id}`)).json();
    state.id = s.id; state.transpose = s.transpose; state.capo = s.capo;
    $("song-title").value = s.title;
    $("song-text").value = s.text;
    status("");
    updateControls();
  }

  function newSong() {
    Object.assign(state, { id: null, transpose: 0, capo: 0 });
    $("song-title").value = ""; $("song-text").value = "";
    status(""); updateControls();
  }

  async function save() {
    const title = $("song-title").value.trim();
    if (!title) { status("Add a title first"); return; }
    const body = JSON.stringify({ title, text: $("song-text").value, transpose: state.transpose, capo: state.capo });
    const res = await fetch(state.id ? `/api/songs/${state.id}` : "/api/songs", {
      method: state.id ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" }, body,
    });
    if (!res.ok) { status("Save failed"); return; }
    state.id = (await res.json()).id;
    status("Saved");
    loadList();
  }

  const step = (key, d, lo, hi) => () => {
    state[key] = Math.min(hi, Math.max(lo, state[key] + d));
    updateControls();
  };
  $("tr-down").onclick = step("transpose", -1, -11, 11);
  $("tr-up").onclick = step("transpose", 1, -11, 11);
  $("capo-down").onclick = step("capo", -1, 0, 12);
  $("capo-up").onclick = step("capo", 1, 0, 12);
  $("song-save").onclick = save;
  $("song-new").onclick = newSong;
  $("song-text").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 250); });

  loadList();
  updateControls();
})();