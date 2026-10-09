// Frontend logic: ask the server for a chord, then draw its diagram as SVG.
// Plain JavaScript, no libraries.

// ---------------------------------------------------------------------------
// 1. Drawing the diagram
// ---------------------------------------------------------------------------

// Layout numbers for the SVG, in SVG units (the viewBox scales it to fit the page).
const STRING_NAMES = ["G", "C", "E", "A"]; // left to right, same order as the fret arrays
const FRET_ROWS = 4;      // how many frets the diagram shows
const STRING_GAP = 30;    // distance between neighbouring strings
const FRET_GAP = 34;      // distance between neighbouring fret lines
const LEFT = 35;          // x of the first (G) string
const TOP = 34;           // y of the nut (the top line); open-string circles sit above it

/**
 * Turn a fret array like [0, 0, 0, 3] into an SVG string.
 *
 * Only numbers and fixed text go into this string, never anything the user
 * typed, so it's safe to put in the page with innerHTML.
 */
function chordSvg(frets) {
  const parts = []; // we collect SVG snippets here and join them at the end

  // If the chord fits in the first 4 frets, draw from the nut (fret 1).
  // Otherwise start the diagram at the lowest pressed fret and label it ("5fr").
  const highest = Math.max(...frets);
  const pressed = frets.filter((f) => f > 0);
  const baseFret = highest <= FRET_ROWS ? 1 : Math.min(...pressed);

  const stringX = (i) => LEFT + i * STRING_GAP;
  const width = (STRING_NAMES.length - 1) * STRING_GAP;
  const bottom = TOP + FRET_ROWS * FRET_GAP;

  // Horizontal lines: the nut (row 0) and one under each fret row.
  for (let row = 0; row <= FRET_ROWS; row++) {
    const y = TOP + row * FRET_GAP;
    const cls = row === 0 && baseFret === 1 ? "nut" : "fret-line";
    parts.push(`<line class="${cls}" x1="${LEFT}" y1="${y}" x2="${LEFT + width}" y2="${y}"/>`);
  }

  // Vertical lines: the four strings, plus the note name under each.
  STRING_NAMES.forEach((name, i) => {
    const x = stringX(i);
    parts.push(`<line class="string" x1="${x}" y1="${TOP}" x2="${x}" y2="${bottom}"/>`);
    parts.push(`<text class="label" x="${x}" y="${bottom + 20}" text-anchor="middle">${name}</text>`);
  });

  // "5fr" label beside the first row when the diagram doesn't start at the nut.
  if (baseFret > 1) {
    parts.push(
      `<text class="label" x="${LEFT - 8}" y="${TOP + FRET_GAP / 2 + 4}" text-anchor="end">${baseFret}fr</text>`
    );
  }

  // The dots. Fret 0 = open string (hollow circle above the nut).
  // Any other fret = filled dot in the matching row.
  frets.forEach((fret, i) => {
    const x = stringX(i);
    if (fret === 0) {
      parts.push(`<circle class="open-mark" cx="${x}" cy="${TOP - 12}" r="6"/>`);
    } else {
      const row = fret - baseFret; // 0 = first row shown
      const y = TOP + (row + 0.5) * FRET_GAP; // +0.5 puts the dot between two fret lines
      parts.push(`<circle class="dot" cx="${x}" cy="${y}" r="11"/>`);
    }
  });

  return `<svg viewBox="0 0 160 200" role="img">${parts.join("")}</svg>`;
}

// ---------------------------------------------------------------------------
// 2. Talking to the server
// ---------------------------------------------------------------------------

/** fetch() a URL and return its JSON, or throw an Error with the server's message. */
async function getJson(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    // Our server sends {"detail": "readable message"} for bad chord names.
    throw new Error(typeof data.detail === "string" ? data.detail : "Something went wrong.");
  }
  return data;
}

// ---------------------------------------------------------------------------
// 3. Updating the page
// ---------------------------------------------------------------------------

const form = document.querySelector("#chord-form");
const input = document.querySelector("#chord-input");
const errorEl = document.querySelector("#error");
const resultEl = document.querySelector("#result");
const titleEl = document.querySelector("#chord-title");
const diagramEl = document.querySelector("#diagram");
const fretTextEl = document.querySelector("#fret-text");
const transposeEl = document.querySelector("#transpose-controls");

let currentChord = null; // name of the chord on screen, used by the transpose buttons

/** Draw a chord object from the server ({name, frets, tuning, ...}) on the page. */
function showChord(chord) {
  currentChord = chord.name;
  errorEl.textContent = "";

  // textContent (not innerHTML) for anything that came from the user.
  titleEl.textContent = chord.name;
  fretTextEl.textContent = `Frets (${chord.tuning.join(" ")}): ${chord.frets.join(" ")}`;

  diagramEl.innerHTML = chordSvg(chord.frets);
  diagramEl
    .querySelector("svg")
    .setAttribute("aria-label", `${chord.name} ukulele chord, frets ${chord.frets.join(" ")}`);

  input.value = chord.name; // keeps the text box in sync after transposing
  resultEl.hidden = false;
  transposeEl.hidden = false;
}

/** Show an error message and hide the old diagram so it can't be mistaken for the answer. */
function showError(message) {
  errorEl.textContent = message;
  resultEl.hidden = true;
  transposeEl.hidden = true;
  currentChord = null;
}

async function lookUpChord(name) {
  try {
    // encodeURIComponent turns "#" into "%23" so it survives the trip to the server.
    showChord(await getJson(`/api/chord?name=${encodeURIComponent(name)}`));
  } catch (err) {
    showError(err.message);
  }
}

async function transposeCurrent(semitones) {
  if (!currentChord) return;
  try {
    const url = `/api/transpose?chord=${encodeURIComponent(currentChord)}&semitones=${semitones}`;
    showChord(await getJson(url));
  } catch (err) {
    showError(err.message);
  }
}

// ---------------------------------------------------------------------------
// 4. Wiring up events
// ---------------------------------------------------------------------------

form.addEventListener("submit", (event) => {
  event.preventDefault(); // stop the browser from reloading the page
  lookUpChord(input.value);
});

document.querySelector("#down").addEventListener("click", () => transposeCurrent(-1));
document.querySelector("#up").addEventListener("click", () => transposeCurrent(1));

lookUpChord(input.value); // show the starting chord (C) on page load