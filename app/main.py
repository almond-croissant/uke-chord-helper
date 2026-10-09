"""The web server. Two JSON endpoints, plus the static frontend.

Run it from the project root with:  uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .chords import get_chord
from .theory import transpose

# The "static" folder sits next to the "app" folder. Building the path from
# this file's location means the server works no matter where you launch it.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Ukulele Chord Helper")


# The chord name goes in a *query parameter* (?name=F%23m7), not in the URL
# path. A "#" in a URL means "fragment" and the browser never sends it to the
# server, so "F#m7" has to be percent-encoded as "F%23m7". The frontend does
# that with encodeURIComponent().
@app.get("/api/chord")
def api_chord(name: str) -> dict:
    """GET /api/chord?name=Am7  ->  the chord's fret array and details."""
    try:
        return get_chord(name)
    except ValueError as err:
        # 400 = "the request was bad". The message is shown to the user.
        raise HTTPException(status_code=400, detail=str(err))


@app.get("/api/transpose")
def api_transpose(chord: str, semitones: int) -> dict:
    """GET /api/transpose?chord=C&semitones=2  ->  the chord D, with its fingering.

    FastAPI converts `semitones` to an int for us (and replies 422 if it isn't one).
    """
    try:
        return get_chord(transpose(chord, semitones))
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


# Serve everything in static/ (index.html, app.js, style.css). This mount is
# registered LAST: routes are matched in order, so /api/... is tried first and
# anything else falls through to the files. html=True makes "/" serve index.html.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")