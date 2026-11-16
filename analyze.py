"""Piosenka + tekst -> czasy fraz (Whisper, dopasowany do podanego tekstu) -> propozycja chunkow."""
import difflib, math, re


def parse_lyrics(text):
    """Jedna linijka = jedna fraza. Linia [Nazwa] ustawia sekcje dla kolejnych fraz."""
    sec, out = "", []
    for l in text.splitlines():
        l = l.strip()
        if not l:
            continue
        m = re.fullmatch(r"\[(.+)\]", l)
        if m:
            sec = m.group(1).strip()
        else:
            out.append({"text": l, "section": sec})
    return out


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def transcribe(audio, language, model_name, hint):
    import whisper                      # ladowany dopiero tutaj - apka startuje bez niego
    model = whisper.load_model(model_name, device="cpu")
    return model.transcribe(audio, language=language or None, word_timestamps=True, condition_on_previous_text=False,
                            no_speech_threshold=0.1, logprob_threshold=-2.0, initial_prompt=hint, fp16=False)


def align(lines, res):
    """Czasy slow z Whispera przypisane do podanych fraz (dopasowanie sekwencji slow)."""
    words = [(norm(w["word"]), w["start"], w["end"]) for s in res["segments"] for w in s.get("words", []) if norm(w["word"])]
    lw = [(norm(t), i) for i, l in enumerate(lines) for t in l["text"].split() if norm(t)]
    sm = difflib.SequenceMatcher(None, [x[0] for x in lw], [x[0] for x in words], autojunk=False)
    hit = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            hit.setdefault(lw[a + k][1], []).append(words[b + k][1:])
    out = []
    for i, l in enumerate(lines):
        h = hit.get(i, [])
        out.append({"line": i, "text": l["text"], "section": l["section"],
                    "start": round(min(x[0] for x in h), 2) if h else None,
                    "end": round(max(x[1] for x in h), 2) if h else None,
                    "matched": len(h), "total": sum(1 for x in lw if x[1] == i)})
    return out


def split(lines, duration, max_len, gap=4.0):
    """Chunki <= max_len z calych fraz. Ciecie tylko na poczatku frazy; przerwy bez wokalu > gap to chunki instrumentalne."""
    L = sorted((l for l in lines if l.get("start") is not None), key=lambda l: l["start"])
    chunks, cur, pos = [], None, 0.0

    def instr(a, b, sec):
        n = max(1, math.ceil((b - a) / max_len - 1e-9))
        for k in range(n):
            chunks.append({"start": round(a + (b - a) * k / n, 2), "end": round(a + (b - a) * (k + 1) / n, 2),
                           "section": sec, "text": "", "instrumental": True})

    for i, l in enumerate(L):
        nxt = L[i + 1]["start"] if i + 1 < len(L) else duration
        bs, be = l["start"], nxt if nxt - l["end"] <= gap else min(duration, round(l["end"] + 0.3, 2))
        if bs - pos > 3.0:                                   # dluzszy kawalek bez wokalu przed fraza (krotszy wchodzi do chunka)
            if cur:
                chunks.append(cur); cur = None
            instr(pos, bs, "intro" if pos == 0 else "instrumental")
        else:
            bs = pos
        if cur and (l.get("section", "") != cur["section"] or be - cur["start"] > max_len):
            chunks.append(cur); cur = None
        if cur is None:
            cur = {"start": round(bs, 2), "end": be, "section": l.get("section", ""), "text": l["text"]}
        else:
            cur["end"] = be; cur["text"] += " / " + l["text"]
        pos = be
    if cur:
        chunks.append(cur)
    if duration - pos > 3.0:
        instr(pos, duration, "outro")
    elif chunks:
        chunks[-1]["end"] = round(duration, 2)
    for c in chunks:
        c["end"] = round(c["end"], 2)
        c["long"] = c["end"] - c["start"] > max_len + 0.01      # jedna fraza dluzsza niz limit
    return chunks
