"""Music theory helpers: note names, chord-name parsing, and transposing.

Nothing in here knows about FastAPI or the web, so you can play with it in a
Python REPL (run from the project folder):

    >>> from app.theory import transpose
    >>> transpose("Am7", 3)
    'Cm7'
    >>> transpose("Bb", 2)
    'C'
"""

from typing import NamedTuple

# There are 12 different notes before the pattern repeats. Some have two
# names (C# and Db are the same pitch), so we keep one list per spelling.
# The list index is the number of semitones above C.
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Semitones above C for the white-key notes. Sharps/flats adjust from here.
NATURAL_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Every spelling of a chord type we accept, mapped to the canonical key used
# in chords.py. Add an alias here and it works everywhere.
QUALITY_ALIASES = {
    "": "major", "M": "major", "maj": "major", "major": "major",
    "m": "minor", "min": "minor", "minor": "minor", "-": "minor",
    "7": "7", "dom7": "7",
    "maj7": "maj7", "M7": "maj7",
    "m7": "m7", "min7": "m7", "-7": "m7",
    "sus2": "sus2",
    "sus4": "sus4", "sus": "sus4",
    "dim": "dim",
}


class ParsedChord(NamedTuple):
    """The pieces of a chord name. Example for "Bbm7":"""
    root: str     # "Bb"  - the note, normalised (capital letter, ASCII # or b)
    suffix: str   # "m7"  - the chord-type text exactly as the user typed it
    quality: str  # "m7"  - canonical chord type (the key used in chords.py)


def note_to_semitone(note: str) -> int:
    """Turn a note name into 0-11 (C=0, C#=1, ... B=11).

    Accepts sharps and flats, so "C#" and "Db" both give 1.
    """
    letter = note[:1].upper()
    if letter not in NATURAL_SEMITONES:
        raise ValueError(f"'{note}' is not a note name. Use a letter from A to G.")

    semitone = NATURAL_SEMITONES[letter]
    for accidental in note[1:]:
        if accidental == "#":
            semitone += 1
        elif accidental == "b":
            semitone -= 1
        else:
            raise ValueError(f"'{note}' is not a note name.")

    # % 12 wraps around: B# (12) -> 0, and Cb (-1) -> 11.
    return semitone % 12


def _lookup_quality(suffix: str) -> str | None:
    """Find the canonical chord type for a suffix, or None if unknown."""
    if suffix in QUALITY_ALIASES:  # exact match first, so "M" and "m" stay different
        return QUALITY_ALIASES[suffix]
    # Be forgiving about capitals ("MAJ7" is fine) - but never lowercase a
    # suffix containing "M", because that would turn major into minor.
    if "M" not in suffix:
        return QUALITY_ALIASES.get(suffix.lower())
    return None


def parse_chord(name: str) -> ParsedChord:
    """Split a chord name like "F#m7" into root, suffix and quality.

    Raises ValueError with a readable message if the name isn't valid.
    """
    # Accept the typographic sharp/flat symbols too.
    text = name.strip().replace("\u266f", "#").replace("\u266d", "b")

    if not text or text[0].upper() not in NATURAL_SEMITONES:
        raise ValueError("Start the chord with a note from A to G, like Am7 or F#.")

    # The root is a letter plus at most one accidental.
    root = text[0].upper()
    rest = text[1:]
    # Note the tuple: `"" in "#b"` would be True for a plain string, but
    # `"" in ("#", "b")` is False, which is what we want when rest is empty.
    if rest[:1] in ("#", "b"):
        root += rest[0]
        rest = rest[1:]

    quality = _lookup_quality(rest)
    if quality is None:
        raise ValueError(
            f"Unknown chord type '{rest}'. Supported: major (no suffix), "
            "m, 7, maj7, m7, sus2, sus4, dim."
        )

    return ParsedChord(root=root, suffix=rest, quality=quality)


def transpose(chord_name: str, semitones: int) -> str:
    """Shift a chord up (positive) or down (negative) by some semitones.

        transpose("C", 2)    -> "D"
        transpose("Am7", -3) -> "F#m7"
        transpose("Bb", 1)   -> "B"
        transpose("Eb", 1)   -> "E"
        transpose("Dbm", 2)  -> "Ebm"   (flat in, flats out)

    Only the root note moves; the chord type ("m7", "sus4"...) is kept as typed.
    If the original root was written with a flat we answer with flats,
    otherwise with sharps.
    """
    parsed = parse_chord(chord_name)

    names = FLAT_NAMES if parsed.root.endswith("b") else SHARP_NAMES

    # Python's % always gives 0-11 even for negative numbers: -1 % 12 == 11.
    # That makes "down" and "wrap past B" work without special cases.
    new_index = (note_to_semitone(parsed.root) + semitones) % 12

    return names[new_index] + parsed.suffix