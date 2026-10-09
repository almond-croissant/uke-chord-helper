import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .songs import render_song

DB_PATH = Path(__file__).resolve().parent.parent / "songs.db"
router = APIRouter(prefix="/api")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


with closing(db()) as _c, _c:
    _c.execute("""CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        transpose INTEGER NOT NULL DEFAULT 0,
        capo INTEGER NOT NULL DEFAULT 0,
        updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")


class RenderIn(BaseModel):
    text: str = Field(max_length=20000)
    transpose: int = Field(0, ge=-11, le=11)
    capo: int = Field(0, ge=0, le=12)


class SongIn(RenderIn):
    title: str = Field(min_length=1, max_length=200)


def _row_or_404(conn, song_id):
    row = conn.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Song not found")
    return row


@router.post("/song/render")
def render(body: RenderIn):
    return render_song(body.text, body.transpose, body.capo)


@router.get("/songs")
def list_songs():
    with closing(db()) as conn:
        rows = conn.execute(
            "SELECT id, title FROM songs ORDER BY updated DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


@router.get("/songs/{song_id}")
def get_song(song_id: int):
    with closing(db()) as conn:
        r = _row_or_404(conn, song_id)
    return {"id": r["id"], "title": r["title"], "text": r["body"],
            "transpose": r["transpose"], "capo": r["capo"]}


@router.post("/songs", status_code=201)
def create_song(s: SongIn):
    with closing(db()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO songs (title, body, transpose, capo) VALUES (?,?,?,?)",
            (s.title, s.text, s.transpose, s.capo))
    return {"id": cur.lastrowid}


@router.put("/songs/{song_id}")
def update_song(song_id: int, s: SongIn):
    with closing(db()) as conn, conn:
        _row_or_404(conn, song_id)
        conn.execute(
            "UPDATE songs SET title=?, body=?, transpose=?, capo=?, "
            "updated=CURRENT_TIMESTAMP WHERE id=?",
            (s.title, s.text, s.transpose, s.capo, song_id))
    return {"id": song_id}


@router.delete("/songs/{song_id}", status_code=204)
def delete_song(song_id: int):
    with closing(db()) as conn, conn:
        _row_or_404(conn, song_id)
        conn.execute("DELETE FROM songs WHERE id=?", (song_id,))