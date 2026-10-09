import re
from .theory import transpose
from .chords import get_chord

CHORD_RE = re.compile(r"^[A-G][#b]?(?:maj7|m7|sus2|sus4|dim|m|7)?$")
INLINE_RE = re.compile(r"\[([^\]]*)\]")


def _is_chord_line(line: str) -> bool:
    toks = line.split()
    return bool(toks) and all(CHORD_RE.match(t) for t in toks)


def _inline(line: str):
    """'Hel[Am]lo' -> ('Hello', [(3, 'Am')]). Non-chord brackets like [Chorus] stay as text."""
    lyric, chords, last = "", [], 0
    for m in INLINE_RE.finditer(line):
        lyric += line[last:m.start()]
        name = m.group(1).strip()
        if CHORD_RE.match(name):
            chords.append((len(lyric), name))
        else:
            lyric += m.group(0)
        last = m.end()
    return lyric + line[last:], chords


def parse_song(text: str):
    """Returns [(lyric, [(column, chord), ...]), ...] for either input style."""
    lines = text.replace("\t", "    ").splitlines()
    rows, i = [], 0
    while i < len(lines):
        line = lines[i].rstrip()
        if _is_chord_line(line):
            chords = [(m.start(), m.group()) for m in re.finditer(r"\S+", line)]
            nxt = lines[i + 1].rstrip() if i + 1 < len(lines) else ""
            if nxt.strip() and not _is_chord_line(nxt):
                rows.append((nxt, chords))
                i += 2
                continue
            rows.append(("", chords))
        else:
            rows.append(_inline(line))
        i += 1
    return rows


def _segments(lyric, chords):
    if not chords:
        return [{"chord": None, "text": lyric}]
    segs = []
    if chords[0][0] > 0:
        segs.append({"chord": None, "text": lyric[:chords[0][0]]})
    for k, (pos, ch) in enumerate(chords):
        end = chords[k + 1][0] if k + 1 < len(chords) else len(lyric)
        segs.append({"chord": ch, "text": lyric[pos:end]})
    return segs


def _frets(name):
    try:
        c = get_chord(name)
        return c["frets"] if c else None
    except Exception:
        return None


def render_song(text: str, semitones: int = 0, capo: int = 0):
    """Chords shown are the SHAPES to play: transposed by `semitones`, then lowered by `capo`."""
    shift = (semitones - capo) % 12
    lines, unique = [], []
    for lyric, chords in parse_song(text):
        shaped = [(p, transpose(c, shift) if shift else c) for p, c in chords]
        for _, c in shaped:
            if c not in unique:
                unique.append(c)
        lines.append(_segments(lyric, shaped))
    return {"lines": lines,
            "chords": [{"name": n, "frets": _frets(n)} for n in unique]}