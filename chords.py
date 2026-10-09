"""Chord data for a standard-tuned ukulele (G-C-E-A, "re-entrant" high G).

Each fingering is a list of 4 fret numbers, one per string, in the same order
as TUNING (left to right in a chord diagram):

    [0, 0, 0, 3]  ->  G string open, C open, E open, A string at fret 3  ->  C major

    0 means "open string", 1 means "press at the 1st fret", and so on.

Data is keyed by root note, then by chord quality. Roots are stored with
SHARP names only (C#, not Db). get_chord() converts flats for you, so the
table doesn't need 21 roots.

How the fingerings were made: I searched every combination of frets 0-12 for
ones that contain exactly the chord's notes, kept those that fit within a
4-fret stretch, and preferred low positions and few fingers. E and Em were
then swapped for the textbook shapes. The table is plain data - edit any
fingering you'd rather play differently.
"""

from .theory import SHARP_NAMES, note_to_semitone, parse_chord

# Open-string note names, in the order used by every fret array below.
TUNING = ["G", "C", "E", "A"]

CHORDS: dict[str, dict[str, list[int]]] = {
    "C": {
        "major": [0, 0, 0, 3],
        "minor": [0, 3, 3, 3],
        "7": [0, 0, 0, 1],
        "maj7": [0, 0, 0, 2],
        "m7": [3, 3, 3, 3],
        "sus2": [0, 2, 3, 3],
        "sus4": [0, 0, 1, 3],
        "dim": [5, 3, 2, 3],
    },
    "C#": {
        "major": [1, 1, 1, 4],
        "minor": [1, 1, 0, 4],
        "7": [1, 1, 1, 2],
        "maj7": [1, 1, 1, 3],
        "m7": [1, 1, 0, 2],
        "sus2": [1, 3, 4, 4],
        "sus4": [1, 1, 2, 4],
        "dim": [0, 4, 0, 4],
    },
    "D": {
        "major": [2, 2, 2, 0],
        "minor": [2, 2, 1, 0],
        "7": [2, 2, 2, 3],
        "maj7": [2, 2, 2, 4],
        "m7": [2, 2, 1, 3],
        "sus2": [2, 2, 0, 0],
        "sus4": [0, 2, 3, 0],
        "dim": [7, 5, 4, 5],
    },
    "D#": {
        "major": [0, 3, 3, 1],
        "minor": [3, 3, 2, 1],
        "7": [3, 3, 3, 4],
        "maj7": [3, 3, 3, 5],
        "m7": [3, 3, 2, 4],
        "sus2": [3, 3, 1, 1],
        "sus4": [1, 3, 4, 1],
        "dim": [2, 3, 2, 0],
    },
    "E": {
        "major": [4, 4, 4, 2],
        "minor": [0, 4, 3, 2],
        "7": [1, 2, 0, 2],
        "maj7": [1, 3, 0, 2],
        "m7": [0, 2, 0, 2],
        "sus2": [4, 4, 2, 2],
        "sus4": [4, 4, 0, 0],
        "dim": [0, 4, 0, 1],
    },
    "F": {
        "major": [2, 0, 1, 0],
        "minor": [1, 0, 1, 3],
        "7": [2, 3, 1, 3],
        "maj7": [2, 4, 1, 3],
        "m7": [1, 3, 1, 3],
        "sus2": [0, 0, 1, 3],
        "sus4": [3, 0, 1, 1],
        "dim": [4, 5, 4, 2],
    },
    "F#": {
        "major": [3, 1, 2, 1],
        "minor": [2, 1, 2, 0],
        "7": [3, 4, 2, 4],
        "maj7": [3, 5, 2, 4],
        "m7": [2, 4, 2, 4],
        "sus2": [1, 1, 2, 4],
        "sus4": [4, 1, 2, 2],
        "dim": [2, 0, 2, 0],
    },
    "G": {
        "major": [0, 2, 3, 2],
        "minor": [0, 2, 3, 1],
        "7": [0, 2, 1, 2],
        "maj7": [0, 2, 2, 2],
        "m7": [0, 2, 1, 1],
        "sus2": [0, 2, 3, 0],
        "sus4": [0, 2, 3, 3],
        "dim": [0, 1, 3, 1],
    },
    "G#": {
        "major": [1, 3, 4, 3],
        "minor": [4, 3, 4, 2],
        "7": [1, 3, 2, 3],
        "maj7": [1, 3, 3, 3],
        "m7": [1, 3, 2, 2],
        "sus2": [1, 3, 4, 1],
        "sus4": [1, 3, 4, 4],
        "dim": [4, 2, 4, 2],
    },
    "A": {
        "major": [2, 1, 0, 0],
        "minor": [2, 0, 0, 0],
        "7": [0, 1, 0, 0],
        "maj7": [1, 1, 0, 0],
        "m7": [0, 0, 0, 0],
        "sus2": [4, 4, 0, 0],
        "sus4": [2, 2, 0, 0],
        "dim": [5, 3, 5, 0],
    },
    "A#": {
        "major": [3, 2, 1, 1],
        "minor": [3, 1, 1, 1],
        "7": [1, 2, 1, 1],
        "maj7": [2, 2, 1, 1],
        "m7": [1, 1, 1, 1],
        "sus2": [3, 0, 1, 1],
        "sus4": [3, 3, 1, 1],
        "dim": [3, 1, 0, 1],
    },
    "B": {
        "major": [4, 3, 2, 2],
        "minor": [4, 2, 2, 2],
        "7": [2, 3, 2, 2],
        "maj7": [3, 3, 2, 2],
        "m7": [2, 2, 2, 2],
        "sus2": [4, 1, 2, 2],
        "sus4": [4, 4, 2, 2],
        "dim": [4, 2, 1, 2],
    },
}


def get_chord(name: str) -> dict:
    """Look up a chord by name, e.g. "Am7", "F#", "Bbsus4".

    Returns a dict that FastAPI turns into JSON:
        {"name": "Bbsus4", "root": "Bb", "quality": "sus4",
         "frets": [3, 3, 1, 1], "tuning": ["G", "C", "E", "A"]}

    Raises ValueError if the name can't be understood.
    """
    parsed = parse_chord(name)

    # Convert the root to a number 0-11, then back to its sharp spelling,
    # so "Bb" and "A#" both find the same row in CHORDS.
    sharp_root = SHARP_NAMES[note_to_semitone(parsed.root)]

    return {
        "name": parsed.root + parsed.suffix,
        "root": parsed.root,
        "quality": parsed.quality,
        "frets": list(CHORDS[sharp_root][parsed.quality]),  # copy, so callers can't edit our table
        "tuning": TUNING,
    }