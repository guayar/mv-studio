#!/usr/bin/env python3
"""MV Studio - lokalna apka do robienia teledyskow metoda extend (H3 Timeline w ComfyUI).
Start: python3 server.py [port]  ->  http://127.0.0.1:8777
Stan projektow: projects/<nazwa>.json, robocze pliki: projects/<nazwa>/ (prompty, logi, zlozone filmy).
Apka niczego nie kasuje: odrzucone rendery i stare wersje zostaja na dysku."""
import glob, json, mimetypes, os, re, subprocess, sys, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import analyze

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(ROOT, "projects")
LOCK = threading.RLock()
JOB = {"state": "idle"}          # jeden render naraz (GPU)
ANALYZE = {"state": "idle"}      # Whisper w tle

DEFAULTS = {
    "dir": "", "song": "", "lines": "", "words": "",
    "fps": 24, "width": 1344, "height": 768,
    "window": 39,                # zamrozony prefiks z poprzedniego klipu (klatki)
    "overlap": 4,                # klatki nakladki na poczatku klipu extend (ucinane przy laczeniu)
    "lead": 12,                  # swiezy start: ile klatek nowego klipu pomijamy przed cieciem
    "mp": 0.98, "steps": "20", "seed": 1234, "prefix": "mv_", "refs": "",
    "base_film": {"file": "", "frames": 0},   # zaakceptowany film sprzed apki
    "base_clip": "",             # ostatni klip tego filmu (wzgledem ComfyUI/output) - baza pierwszego extendu
    "comfy": {"url": "http://127.0.0.1:8188", "input": "~/ComfyUI/input", "output": "~/ComfyUI/output",
              "python": "~/ComfyUI/venv/bin/python",
              "runner": os.path.join(ROOT, "comfy", "tl_run_master.py")},
    # zamowione sekundy -> dostarczone klatki (dlugosc klipu jest skokowa, zmierzone w praktyce)
    "tiers": {"extend": [[8.4, 9.0, 157], [9.5, 11.0, 208]],
              "start": [[8.0, 8.7, 153], [11.0, 11.0, 204], [12.0, 12.0, 255]]},
    "forbidden": ["no", "not", "never", "without", "nothing", "don't", "n't", "calm", "deadpan", "claw", "guitar"],
    "lyrics_text": "", "max_chunk": 8.0, "language": "en", "whisper_model": "medium", "proposal": [],
    "rules": [], "rejects": [], "chunks": [],
}


def P(p):
    return os.path.expanduser(p) if p else p


def pfile(name):
    if not re.fullmatch(r"[\w\-]+", name or ""):
        raise ValueError("zla nazwa projektu (litery, cyfry, _ i -)")
    return os.path.join(PROJ, name + ".json")


def load(name):
    p = json.load(open(pfile(name)))
    for k, v in DEFAULTS.items():
        p.setdefault(k, json.loads(json.dumps(v)))
    return p


def save(name, p):
    tmp = pfile(name) + ".tmp"
    json.dump(p, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, pfile(name))


def workdir(name, sub):
    d = os.path.join(PROJ, name, sub)
    os.makedirs(d, exist_ok=True)
    return d


def nframes(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", f], capture_output=True, text=True)
    return int(r.stdout.strip().split(",")[0])


def read_json(path, default):
    try:
        return json.load(open(P(path)))
    except Exception:
        return default


def song_words(p):
    w = read_json(p["words"], {})
    return [{"w": x["word"].strip(), "s": x["start"], "e": x["end"]}
            for s in w.get("segments", []) for x in s.get("words", [])]


# ---------- wyliczenia czasu ----------
def predict(p, mode, order):
    for lo, hi, fr in p["tiers"].get(mode, []):
        if lo - 1e-6 <= order <= hi + 1e-6:
            return fr
    return None


def win(p, c):
    """Okno kontekstu (klatki ogona poprzedniego klipu) - wlasne chunka albo z projektu."""
    return int(c.get("window") or p["window"])


def calc(p, c, J, last_clip, words, lines):
    """Wszystkie czasy chunka. J = klatki filmu zlozonego przed tym chunkiem."""
    fps, W, ov = p["fps"], win(p, c), p["overlap"]
    acc = next((r for r in c["renders"] if r["name"] == c.get("accepted")), None)
    if J is None:
        return {"ready": False, "warn": ["Najpierw zaakceptuj poprzedni chunk - od niego zalezy J i raw0."]}
    order = float(c.get("order") or 0)
    tier = predict(p, c["mode"], order)
    fr = acc["frames"] if acc and acc.get("frames") else tier
    est = fr or round(order * fps)
    if c["mode"] == "extend":
        cut, skip, base = J, ov, last_clip
    else:
        cut, skip, base = int(c.get("cut_frame") or J), int(c.get("lead", p["lead"])), c.get("base", "")
    d0 = (cut - skip) / fps                     # czas piosenki dostarczonej klatki 0
    raw0 = d0 - (W - ov if c["mode"] == "extend" else W) / fps
    prefix_end = cut / fps if c["mode"] == "extend" else d0
    end = d0 + fr / fps if fr else None
    clip_len = (est + W) / fps
    master = {"ss": round(raw0, 3), "t": round(clip_len + 1.5, 2)}
    ref = {"ss": round(cut / fps - 0.3, 3), "t": round(est / fps + 1.3, 2)} if c["mode"] == "extend" else dict(master)
    warn = []
    if c.get("window") and W != p["window"]:
        warn.append(f"Okno kontekstu {W} kl. zamiast {p['window']} z projektu - mniej stylu z poprzedniego klipu, wiecej z refek; ciaglosc ruchu moze byc slabsza.")
    if c["mode"] == "extend" and W <= ov:
        warn.append(f"Okno kontekstu {W} kl. musi byc wieksze niz nakladka {ov} kl.")
    if not base:
        warn.append("Brak bazy: ustaw klip bazowy (extend) albo still (swiezy start).")
    if tier is None:
        warn.append(f"Nieznany tier dlugosci dla zamowienia {order} s w trybie {c['mode']} - koniec klipu to tylko szacunek.")
    for w in words:
        if prefix_end - 0.05 <= w["s"] < prefix_end + 0.4:
            warn.append(f"Slowo \"{w['w']}\" ({w['s']:.2f} s) wypada w pierwszych 0.4 s po prefiksie ({prefix_end:.2f} s) - lipsync moze nie zlapac.")
            break
    e = end or d0 + est / fps
    for ln in lines:
        if e - 0.6 < ln["start"] <= e + 0.05:
            warn.append(f"Fraza \"{ln['text'][:40]}\" zaczyna sie w {ln['start']:.2f} s, czyli w ostatnich 0.6 s klipu (koniec {e:.2f} s) - lipsync tam ginie.")
    if c.get("end") and e < float(c["end"]) - 0.05:
        warn.append(f"Klip skonczy sie w {e:.2f} s, przed koncem chunka ({float(c['end']):.2f} s).")
    return {"ready": True, "J": J, "cut": cut, "skip": skip, "base": base, "raw0": round(raw0, 3),
            "prefix_end": round(prefix_end, 3), "window": W, "tier": tier, "frames": fr, "end": round(e, 3),
            "end_measured": bool(acc), "J_after": cut + est - skip, "master": master, "ref": ref, "warn": warn}


def timeline(p):
    words, lines = song_words(p), read_json(p["lines"], [])
    J, last, out = p["base_film"]["frames"] or 0, p["base_clip"], []
    for c in p["chunks"]:
        info = calc(p, c, J, last, words, lines)
        out.append(info)
        acc = next((r for r in c["renders"] if r["name"] == c.get("accepted")), None)
        if acc and info["ready"]:
            J, last = info["J_after"], acc["file"]
        else:
            J = None
    return out, words, lines


# ---------- walidator promptu ----------
TIME_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+(?:to\s+(\d+(?:\.\d+)?)\s+seconds|seconds\s+to\s+the\s+end)\s*:", re.I)


def validate(p, prompt, info):
    issues, bad = [], set(x.lower() for x in p["forbidden"])
    prev_end, seen_time = None, False
    for i, line in enumerate(prompt.splitlines(), 1):
        if line.strip().lower().startswith("@ref"):
            continue                                    # spiewany tekst piosenki - wyjatek
        text = re.sub(r'"[^"]*"', " ", line).lower()    # cytaty tekstu tez
        for w in re.findall(r"[a-z]+(?:'[a-z]+)?", text):
            if w in bad or ("n't" in bad and w.endswith("n't")):
                issues.append({"level": "error", "msg": f"linia {i}: zakazane slowo \"{w}\" (tylko zdania pozytywne)"})
        m = TIME_RE.match(line)
        if m:
            a, b = float(m.group(1)), float(m.group(2)) if m.group(2) else None
            if b is not None and b <= a:
                issues.append({"level": "error", "msg": f"linia {i}: koniec {b} <= poczatek {a}"})
            if prev_end is not None and abs(a - prev_end) > 0.011:
                issues.append({"level": "error", "msg": f"linia {i}: zaczyna sie w {a}, a poprzednia konczy w {prev_end} (dziura albo nakladka)"})
            if not seen_time and info.get("ready") and a < info.get("window", p["window"]) / p["fps"] - 0.011:
                issues.append({"level": "warn", "msg": f"linia {i}: pierwszy czas {a} s jest w zamrozonym prefiksie (do {info.get('window', p['window']) / p['fps']:.2f} s)"})
            if info.get("ready") and info.get("frames") and a > (info["frames"] + info.get("window", p["window"])) / p["fps"]:
                issues.append({"level": "error", "msg": f"linia {i}: czas {a} s jest za koncem klipu"})
            prev_end, seen_time = b, True
    if not seen_time:
        issues.append({"level": "warn", "msg": "brak linijek czasu w formacie \"1.62 to 2.09 seconds:\""})
    if "@ref" not in prompt:
        issues.append({"level": "warn", "msg": "brak linii \"@ref1 sings: ...\" (dla chunka instrumentalnego to w porzadku)"})
    for k in ("subject_definitions:", "retention_analysis:", "detailed_description:"):
        if k not in prompt:
            issues.append({"level": "warn", "msg": f"brak sekcji {k}"})
    return issues


# ---------- render ----------
def comfy_queue(p):
    try:
        q = json.load(urllib.request.urlopen(p["comfy"]["url"] + "/queue", timeout=3))
        return {"up": True, "running": len(q["queue_running"]), "pending": len(q["queue_pending"])}
    except Exception:
        return {"up": False, "running": 0, "pending": 0}


def render_name(p, c):
    out = os.path.join(P(p["comfy"]["output"]), os.path.dirname(c_base_hint(p, c)) or "")
    used = {r["name"] for r in c["renders"]}
    n = 1
    while True:
        name = f"{p['prefix']}{c['name']}" + ("" if n == 1 else f"_v{n}")
        if name not in used and not glob.glob(os.path.join(out, name + "_*")):
            return name
        n += 1


def c_base_hint(p, c):
    return (c.get("base") if c["mode"] == "start" else "") or p["base_clip"] or "x/x"


def plan_render(pname, p, c, info, name):
    """Zwraca liste polecen (to samo co robilismy recznie) bez uruchamiania czegokolwiek."""
    inp, song = P(p["comfy"]["input"]), os.path.join(P(p["dir"]), p["song"]) if not os.path.isabs(p["song"]) else p["song"]
    m, r = f"mvs_{name}_master.wav", f"mvs_{name}_ref.wav"
    pf = os.path.join(workdir(pname, "prompts"), name + ".txt")
    def cut(a, f):
        if a["ss"] < 0:                             # poczatek filmu: prefiks wypada przed piosenka -> cisza z przodu
            return ["ffmpeg", "-y", "-v", "error", "-t", f"{a['t'] + a['ss']:.2f}", "-i", song, "-af",
                    f"adelay={round(-a['ss'] * 1000)}:all=1", "-c:a", "pcm_s16le", os.path.join(inp, f)]
        return ["ffmpeg", "-y", "-v", "error", "-ss", f"{a['ss']:.3f}", "-t", f"{a['t']:.2f}", "-i", song,
                "-c:a", "pcm_s16le", os.path.join(inp, f)]
    env = {"MP": str(p["mp"]), "MASTER_AUDIO": m, "AUDIO": r, "COMFY_URL": p["comfy"]["url"], "COMFY_OUTPUT": p["comfy"]["output"]}
    if str(p["steps"]) == "8":
        env["TURBO"] = "1"
    refs = ",".join(x.strip() for x in (c.get("refs") or p["refs"]).split(",") if x.strip())
    run = [P(p["comfy"]["python"]), "-u", p["comfy"]["runner"], name, pf, info["base"], str(c["order"]),
           str(c.get("seed") or p["seed"]), refs, str(info.get("window", p["window"]))]
    return {"name": name, "prompt_file": pf, "audio": [cut(info["master"], m), cut(info["ref"], r)], "env": env, "run": run}


def worker(pname, cid, plan):
    log = os.path.join(workdir(pname, "logs"), plan["name"] + ".log")
    JOB.update(state="running", project=pname, chunk=cid, render=plan["name"], log=log, started=time.time(), proc=None)
    status, result = "error", None
    with open(log, "w") as lf:
        try:
            for a in plan["audio"]:
                lf.write("$ " + " ".join(a) + "\n"); lf.flush()
                subprocess.run(a, check=True, stdout=lf, stderr=lf)
            lf.write("$ " + " ".join(f"{k}={v}" for k, v in plan["env"].items()) + " " + " ".join(plan["run"]) + "\n"); lf.flush()
            proc = subprocess.Popen(plan["run"], env={**os.environ, **plan["env"]}, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            JOB["proc"] = proc
            for line in proc.stdout:
                lf.write(line); lf.flush()
                if line.startswith("RESULT ") and line.split(None, 1)[1].strip() != "none":
                    result = line.split(None, 1)[1].strip()
            if proc.wait() == 0 and result:
                status = "done"
            elif JOB.get("interrupted"):
                status = "interrupted"
        except Exception as e:
            lf.write(f"BLAD: {e}\n")
    with LOCK:
        p = load(pname)
        c = next(x for x in p["chunks"] if x["id"] == cid)
        r = next(x for x in c["renders"] if x["name"] == plan["name"])
        r.update(status=status, minutes=round((time.time() - JOB["started"]) / 60, 1))
        if status == "done":
            r["file"] = result
            r["frames"] = nframes(os.path.join(P(p["comfy"]["output"]), result))
        save(pname, p)
    JOB.clear(); JOB.update(state="idle", last=plan["name"], last_status=status)


def start_render(pname, cid, prompt, dry):
    with LOCK:
        p = load(pname)
        tl, _, _ = timeline(p)
        i = next(k for k, x in enumerate(p["chunks"]) if x["id"] == cid)
        c, info = p["chunks"][i], tl[i]
        if not info["ready"]:
            raise ValueError(info["warn"][0])
        if not info["base"]:
            raise ValueError("brak bazy dla tego chunka")
        errs = [x["msg"] for x in validate(p, prompt, info) if x["level"] == "error"]
        plan = plan_render(pname, p, c, info, render_name(p, c))
        if dry:
            return {"dry": True, "plan": plan, "errors": errs, "comfy": comfy_queue(p)}
        if errs:
            raise ValueError("prompt ma bledy: " + "; ".join(errs[:3]))
        if JOB["state"] != "idle":
            raise ValueError("render juz trwa - jeden naraz")
        q = comfy_queue(p)
        if not q["up"]:
            raise ValueError("ComfyUI nie odpowiada - uruchom je w terminalu")
        if q["running"] or q["pending"]:
            raise ValueError("ComfyUI jest zajete innym zadaniem - poczekaj, az skonczy")
        open(plan["prompt_file"], "w").write(prompt)
        c["prompt"] = prompt
        c["renders"].append({"name": plan["name"], "status": "running", "prompt": prompt, "order": c["order"],
                             "created": time.strftime("%Y-%m-%d %H:%M")})
        save(pname, p)
        JOB["state"] = "starting"
        threading.Thread(target=worker, args=(pname, cid, plan), daemon=True).start()
        return {"dry": False, "plan": plan}


def interrupt(pname):
    if JOB["state"] != "running":
        raise ValueError("nic sie teraz nie renderuje z apki")
    p = load(pname)
    JOB["interrupted"] = True
    urllib.request.urlopen(urllib.request.Request(p["comfy"]["url"] + "/interrupt", data=b"{}", method="POST"), timeout=5)
    if JOB.get("proc"):
        JOB["proc"].terminate()                     # po PID, nigdy pkill -f
    return {"ok": True}


# ---------- montaz ----------
def segments(p, cid, rname, before=False):
    """Lista [plik, od_klatki, do_klatki] filmu do chunka cid wlacznie (before=True: bez niego) + klatka szwu."""
    segs, total, seam = [], 0, None
    if p["base_film"]["file"]:
        segs.append([P(p["base_film"]["file"]), 0, p["base_film"]["frames"]]); total = p["base_film"]["frames"]
    for c in p["chunks"]:
        if before and c["id"] == cid:
            return segs, total, seam
        want = rname if c["id"] == cid else c.get("accepted")
        r = next((x for x in c["renders"] if x["name"] == want and x.get("file")), None)
        if not r:
            raise ValueError(f"chunk {c['name']} nie ma gotowego/zaakceptowanego renderu")
        skip = p["overlap"]
        if c["mode"] == "start":
            cut, skip = int(c.get("cut_frame") or total), int(c.get("lead", p["lead"]))
            while total > cut:                      # przytnij stary film do klatki ciecia
                over = total - cut
                if segs[-1][2] - segs[-1][1] <= over:
                    total -= segs[-1][2] - segs[-1][1]; segs.pop()
                else:
                    segs[-1][2] -= over; total = cut
        seam = total
        segs.append([os.path.join(P(p["comfy"]["output"]), r["file"]), skip, r["frames"]]); total += r["frames"] - skip
        if c["id"] == cid:
            return segs, total, seam
    raise ValueError("nie ma takiego chunka")


def seam_metric(film, seam, n=12):
    import numpy as np
    vf = f"select='between(n,{seam - n},{seam + n})',scale=64:36,format=gray"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", film, "-vf", vf, "-vsync", "0", "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    if len(d) < n + 1:
        return None
    at, med = float(d[n - 1]), float(np.median(np.delete(d, n - 1)))
    return {"at": round(at, 2), "median": round(med, 2), "ratio": round(at / max(med, 0.01), 1)}


def encode(p, segs, out):
    song = p["song"] if os.path.isabs(p["song"]) else os.path.join(P(p["dir"]), p["song"])
    cmd, fc = ["ffmpeg", "-y", "-v", "error"], []
    for i, (f, a, b) in enumerate(segs):
        cmd += ["-i", f]
        fc.append(f"[{i}:v]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,fps={p['fps']},scale={p['width']}:{p['height']},setsar=1[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[v]")
    cmd += ["-i", song, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(segs)}:a", "-shortest",
            "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
            "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise ValueError("ffmpeg: " + r.stderr[-400:])


def assemble(pname, cid, rname):
    p = load(pname)
    segs, total, seam = segments(p, cid, rname)
    out = os.path.join(workdir(pname, "film"), f"film_{rname}.mp4")
    encode(p, segs, out)
    m = seam_metric(out, seam)
    with LOCK:
        p = load(pname)
        c = next(x for x in p["chunks"] if x["id"] == cid)
        rr = next(x for x in c["renders"] if x["name"] == rname)
        rr.update(film=out, film_frames=total, seam_frame=seam, seam=m)
        save(pname, p)
    return {"film": out, "frames": total, "seam_frame": seam, "seam": m}


def film_before(pname, cid):
    """Film taki, jaki jest przed chunkiem cid (z muzyka). Skladany raz, potem brany z dysku."""
    import hashlib
    p = load(pname)
    segs, total, _ = segments(p, cid, None, before=True)
    if not segs:
        raise ValueError("przed tym chunkiem nie ma jeszcze zadnego filmu")
    key = hashlib.md5(json.dumps(segs).encode()).hexdigest()[:10]
    out = os.path.join(workdir(pname, "film"), f"before_{key}.mp4")
    if not os.path.exists(out):
        encode(p, segs, out)
    return {"film": out, "frames": total}


# ---------- piosenka + tekst -> chunki ----------
def song_path(p):
    return p["song"] if os.path.isabs(p["song"]) else os.path.join(P(p["dir"]), p["song"])


def duration(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True)
    return float(r.stdout.strip())


def pick_order(p, mode, length):
    """Najmniejszy tier, ktory pokrywa chunk + 0.3 s zapasu."""
    lost = p["overlap"] if mode == "extend" else p["lead"]
    tiers = p["tiers"].get(mode, [])
    for lo, hi, fr in tiers:
        if (fr - lost) / p["fps"] >= length + 0.3:
            return lo
    return tiers[-1][0] if tiers else round(length + 1, 1)


def resplit(name, lines=None):
    """Zapisuje czasy fraz w folderze apki (plikow projektu nie rusza) i liczy propozycje chunkow."""
    with LOCK:
        p = load(name)
        if lines is not None:
            f = os.path.join(workdir(name, "analysis"), "_line_times.json")
            json.dump(lines, open(f, "w"), ensure_ascii=False, indent=1)
            p["lines"] = f
        lines = read_json(p["lines"], [])
        if not lines:
            raise ValueError("brak czasow fraz - najpierw analiza Whisperem")
        p["proposal"] = analyze.split(lines, duration(song_path(p)), float(p["max_chunk"]))
        save(name, p)
        return {"proposal": p["proposal"]}


def analyze_worker(name):
    try:
        p = load(name)
        lines = analyze.parse_lyrics(p["lyrics_text"])
        ANALYZE.update(state="running", project=name, msg=f"Whisper {p['whisper_model']} slucha piosenki (na CPU, kilka minut)...", started=time.time())
        res = analyze.transcribe(song_path(p), p["language"], p["whisper_model"], ". ".join(l["text"] for l in lines[:4]))
        wf = os.path.join(workdir(name, "analysis"), "_whisper_words.json")
        json.dump(res, open(wf, "w"))
        with LOCK:
            p = load(name); p["words"] = wf; save(name, p)
        al = analyze.align(lines, res)
        resplit(name, al)
        miss = sum(1 for l in al if l["start"] is None)
        ANALYZE.clear(); ANALYZE.update(state="idle", msg=f"Gotowe: {len(al)} fraz, {miss} bez czasu." , done=time.time())
    except Exception as e:
        ANALYZE.clear(); ANALYZE.update(state="idle", msg=f"Blad analizy: {e}")


def apply_proposal(name):
    with LOCK:
        p = load(name)
        if any(c["renders"] for c in p["chunks"]):
            raise ValueError("plan ma juz chunki z renderami - nie zastepuje go")
        if not p["proposal"]:
            raise ValueError("brak propozycji")
        p["chunks"] = []
        for k, c in enumerate(p["proposal"]):
            mode = "start" if k == 0 else "extend"
            p["chunks"].append({"id": f"c{int(time.time() * 1000)}_{k}", "name": f"V{k + 1}", "section": c["section"],
                                "start": c["start"], "end": c["end"], "text": c["text"], "mode": mode,
                                "order": pick_order(p, mode, c["end"] - c["start"]), "prompt": "", "renders": []})
        save(name, p)
        return {"chunks": len(p["chunks"])}


def upload(name, filename, rfile, n):
    """Wgranie piosenki do folderu projektu. Istniejacego pliku nie nadpisuje."""
    with LOCK:
        p = load(name)
        d = P(p["dir"]) or workdir(name, "song")
        os.makedirs(d, exist_ok=True)
        base, ext = os.path.splitext(os.path.basename(filename))
        if ext.lower() not in (".wav", ".mp3", ".flac", ".m4a", ".ogg"):
            raise ValueError("to nie jest plik audio (wav, mp3, flac, m4a, ogg)")
        dst, k = os.path.join(d, base + ext), 1
        while os.path.exists(dst):
            k += 1; dst = os.path.join(d, f"{base}_{k}{ext}")
        with open(dst, "wb") as f:
            while n > 0:
                buf = rfile.read(min(1 << 20, n))
                if not buf:
                    break
                f.write(buf); n -= len(buf)
        p["dir"], p["song"] = d, os.path.basename(dst)
        save(name, p)
        return {"song": p["song"], "duration": duration(dst)}


# ---------- API ----------
def api(method, path, q, body):
    parts = path.strip("/").split("/")[1:]                   # bez "api"
    if parts == ["projects"]:
        return sorted(f[:-5] for f in os.listdir(PROJ) if f.endswith(".json"))
    if parts == ["create"]:
        name, d = body["name"], P(body.get("dir") or "")
        if os.path.exists(pfile(name)):
            raise ValueError("taki projekt juz jest")
        d = d or workdir(name, "song")
        p = json.loads(json.dumps(DEFAULTS)); p.update(dir=d, song=body.get("song", ""))
        for k, f in (("lines", "_line_times.json"), ("words", "_whisper_words.json")):
            if os.path.exists(os.path.join(d, f)):
                p[k] = os.path.join(d, f)
        save(name, p)
        return {"ok": True}
    name, act = parts[1], "/".join(parts[2:])
    with LOCK:
        p = load(name)
        find = lambda: next(x for x in p["chunks"] if x["id"] == body["id"])
        if act == "":
            tl, words, lines = timeline(p)
            job = {k: v for k, v in JOB.items() if k != "proc"}
            if job.get("log") and os.path.exists(job["log"]):
                job["tail"] = open(job["log"]).read()[-1500:]
            return {"project": p, "timeline": tl, "words": words, "lines": lines, "job": job, "analyze": dict(ANALYZE), "outdir": P(p["comfy"]["output"]),
                    "song_path": song_path(p)}
        if act == "comfy":
            return comfy_queue(p)
        if act == "settings":
            for k, v in body.items():
                if k in DEFAULTS and k not in ("chunks", "rejects"):
                    p[k] = v
            if p["base_film"].get("file") and not p["base_film"].get("frames"):
                p["base_film"]["frames"] = nframes(P(p["base_film"]["file"]))
            save(name, p); return {"ok": True}
        if act == "chunk":
            if body.get("id"):
                c = find()
            else:
                c = {"id": f"c{int(time.time() * 1000)}", "renders": [], "prompt": "", "mode": "extend", "order": 8.4}
                p["chunks"].append(c)
            for k in ("name", "section", "start", "end", "text", "mode", "order", "seed", "refs", "base", "cut_frame", "lead", "window", "prompt"):
                if k in body:
                    c[k] = body[k]
            p["chunks"].sort(key=lambda x: float(x.get("start") or 0))
            save(name, p); return {"id": c["id"]}
        if act == "chunk/remove":                            # tylko z planu; pliki zostaja
            c = find()
            if c["renders"] and not body.get("force"):
                raise ValueError("chunk ma rendery - nie usuwam go z planu")
            if JOB.get("chunk") == c["id"]:
                raise ValueError("ten chunk wlasnie sie renderuje")
            p["chunks"].remove(c); save(name, p); return {"ok": True}
        if act == "render/remove":                           # wersja znika z apki; plik wideo zostaje na dysku
            c = find(); r = next(x for x in c["renders"] if x["name"] == body["render"])
            if r.get("status") == "running":
                raise ValueError("ta wersja wlasnie sie renderuje")
            c["renders"].remove(r)
            if c.get("accepted") == r["name"]:
                c["accepted"] = None
            save(name, p); return {"ok": True}
        if act == "validate":
            i = next(k for k, x in enumerate(p["chunks"]) if x["id"] == body["id"])
            return {"issues": validate(p, body["prompt"], timeline(p)[0][i]), "rules": p["rules"]}
        if act == "verdict":
            c = find(); r = next(x for x in c["renders"] if x["name"] == body["render"])
            if body["verdict"] == "accept":
                if r.get("status") not in ("done", "accepted", "rejected") or not r.get("file"):
                    raise ValueError("ten render nie ma gotowego pliku")
                r["status"], c["accepted"] = "accepted", r["name"]
            else:
                r["status"], r["reason"] = "rejected", body.get("reason", "")
                if c.get("accepted") == r["name"]:
                    c["accepted"] = None
                p["rejects"].append({"date": time.strftime("%Y-%m-%d %H:%M"), "render": r["name"], "reason": r["reason"]})
            save(name, p); return {"ok": True}
        if act == "still":                                   # 2-sekundowy still z refki = baza swiezego startu
            c = find()
            ref = next((x.strip() for x in (c.get("refs") or p["refs"]).split(",") if x.strip()), None)
            if not ref:
                raise ValueError("najpierw wpisz refki w Ustawieniach")
            src = os.path.join(P(p["comfy"]["input"]), ref)
            if not os.path.isfile(src):
                raise ValueError(f"nie ma pliku {src}")
            rel = os.path.join("mv_" + name, f"base_{os.path.splitext(ref)[0]}.mp4")
            dst = os.path.join(P(p["comfy"]["output"]), rel)
            if not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                vf = f"scale={p['width']}:{p['height']}:force_original_aspect_ratio=decrease,pad={p['width']}:{p['height']}:(ow-iw)/2:(oh-ih)/2,setsar=1"
                r = subprocess.run(["ffmpeg", "-v", "error", "-loop", "1", "-i", src, "-frames:v", "48", "-r", str(p["fps"]), "-vf", vf,
                                    "-pix_fmt", "yuv420p", dst], capture_output=True, text=True)
                if r.returncode:
                    raise ValueError("ffmpeg: " + r.stderr[-300:])
            c["base"] = rel
            save(name, p); return {"base": rel}
        if act == "rule":
            if body.get("remove") is not None:
                p["rules"].pop(int(body["remove"]))
            else:
                p["rules"].append({"text": body["text"], "date": time.strftime("%Y-%m-%d")})
            save(name, p); return {"ok": True}
        if act == "log":
            f = os.path.join(workdir(name, "logs"), os.path.basename(q["render"][0]) + ".log")
            return {"log": open(f).read()[-6000:] if os.path.exists(f) else ""}
    if act == "render":
        return start_render(name, body["id"], body["prompt"], bool(body.get("dry")))
    if act == "interrupt":
        return interrupt(name)
    if act == "analyze":
        if body.get("whisper"):
            if ANALYZE["state"] != "idle":
                raise ValueError("analiza juz trwa")
            if not analyze.parse_lyrics(load(name)["lyrics_text"]):
                raise ValueError("wklej najpierw tekst piosenki")
            if not os.path.isfile(song_path(load(name))):
                raise ValueError("brak pliku piosenki")
            ANALYZE.update(state="running", project=name, msg="Start analizy...", started=time.time())
            threading.Thread(target=analyze_worker, args=(name,), daemon=True).start()
            return {"started": True}
        return resplit(name, body.get("lines"))
    if act == "apply_proposal":
        return apply_proposal(name)
    if act == "film_before":
        return film_before(name, body["id"])
    if act == "assemble":
        return assemble(name, body["id"], body["render"])
    raise ValueError("nieznane polecenie: " + path)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def send_file(self, path):
        if not os.path.isfile(path):
            return self.send_error(404)
        size, start, end = os.path.getsize(path), 0, None
        m = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        if m:
            start, end = int(m.group(1)), int(m.group(2)) if m.group(2) else None
        end = size - 1 if end is None or end >= size else end
        self.send_response(206 if m else 200)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(end - start + 1))
        if m:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start); left = end - start + 1
            while left > 0:
                buf = f.read(min(1 << 16, left))
                if not buf:
                    break
                try:
                    self.wfile.write(buf)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(buf)

    def handle_any(self, method):
        u = urlparse(self.path); q = parse_qs(u.query)
        try:
            if u.path.startswith("/api/p/") and u.path.endswith("/upload"):
                return self.send_json(upload(u.path.split("/")[3], q["name"][0], self.rfile, int(self.headers.get("Content-Length") or 0)))
            if u.path.startswith("/api/"):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n)) if n else {}
                return self.send_json(api(method, u.path, q, body))
            if u.path == "/media":                           # tylko mp4/png/wav z dysku lokalnego, serwer slucha na 127.0.0.1
                f = os.path.realpath(q["path"][0])
                if os.path.splitext(f)[1].lower() not in (".mp4", ".png", ".jpg", ".wav"):
                    return self.send_error(403)
                return self.send_file(f)
            return self.send_file(os.path.join(ROOT, "static", "index.html" if u.path == "/" else os.path.basename(u.path)))
        except Exception as e:
            self.send_json({"error": str(e) or type(e).__name__}, 400)

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    os.makedirs(PROJ, exist_ok=True)
    print(f"MV Studio: http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
