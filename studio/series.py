import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts") + "/"
def font(n, s): return ImageFont.truetype(FD + n + ".ttf", s)

BG = (11, 13, 16); PANEL = (20, 23, 28); LINE = (38, 43, 51)
INK = (244, 241, 234); MUTED = (163, 168, 176)
OR = (255, 106, 31); GOLD = (245, 197, 66); GREEN = (72, 201, 130); RED = (222, 58, 92)

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_back(x):
    x = max(0.0, min(1.0, x)); c1, c3 = 1.2, 2.2
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def vis(t, t0, t1, fin=0.35, fout=0.3):
    if t < t0 or t > t1: return 0.0
    return ease(min(1.0, (t - t0) / fin, (t1 - t) / fout))

def make_bg():
    base = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([140, 350, 940, 1150], fill=OR + (34,))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    court = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(court); lc = INK + (22,)
    cd.rectangle([380, 1180, 700, 1700], outline=lc, width=4)
    cd.ellipse([380, 1020, 700, 1340], outline=lc, width=4)
    cd.arc([-80, 940, 1160, 2180], 202, 338, fill=lc, width=4)
    cd.line([(60, 1700), (1020, 1700)], fill=lc, width=4)
    cd.ellipse([500, 1640, 580, 1720], outline=lc, width=4)
    base.alpha_composite(court)
    return base
BGI = make_bg()
logo_big = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
def logo_at(size): return logo_big.resize((size, size), Image.LANCZOS)
LOGO_SMALL = logo_at(170)
def paste_logo(img, im, cx, cy, a):
    if a <= 0: return
    if a < 1:
        r, g, b, al = im.split(); al = al.point(lambda v: int(v * a)); im = Image.merge("RGBA", (r, g, b, al))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def fit(d, s, name, size, maxw=940, sp=0):
    while size > 24:
        f = font(name, size)
        if d.textlength(s, font=f) + sp * max(0, len(s) - 1) <= maxw: return f
        size -= 4
    return font(name, 24)
def tw(d, s, f, sp=0): return d.textlength(s, font=f) + sp * max(0, len(s) - 1)
def tc(d, y, s, f, fill, a, dy=0, sp=0, x=W // 2):
    if a <= 0: return
    w = tw(d, s, f, sp)
    if sp:
        cx = x - w / 2
        for ch in s:
            d.text((cx, y + dy), ch, font=f, fill=fill + (int(255 * a),)); cx += d.textlength(ch, font=f) + sp
    else:
        d.text((x - w / 2, y + dy), s, font=f, fill=fill + (int(255 * a),))
def tl(d, x, y, s, f, fill, a):
    if a > 0: d.text((x, y), s, font=f, fill=fill + (int(255 * a),))
def tr(d, xr, y, s, f, fill, a):
    if a > 0: d.text((xr - d.textlength(s, font=f), y), s, font=f, fill=fill + (int(255 * a),))

F_KICK = font("Plex600", 38); F_SUB = font("Plex500", 40); F_MEAN = font("Plex600", 54)
F_SMALL = font("Plex500", 36); F_LAB = font("Plex600", 30); F_END = font("BSD900", 120)

def draw_slide(d, s, t, a):
    k = s["kind"]
    if k == "hook":
        kk = ease_back(t / 0.7)
        y = 520
        for i, ln in enumerate(s["lines"]):
            f = fit(d, ln, "BSD900", s.get("size", 190))
            tc(d, y, ln, f, s.get("colors", [INK] * 9)[i], a, dy=80 * (1 - ease_back((t - 0.12 * i) / 0.7)))
            y += int(f.size * 1.08)
        d.rectangle([W / 2 - 220 * ease((t - 0.5) / 0.7), y + 20, W / 2 + 220 * ease((t - 0.5) / 0.7), y + 25], fill=OR + (int(255 * a),)) if a > 0 else None
        tc(d, y + 60, s["sub"], F_SUB, MUTED, a)
    elif k == "text":
        if s.get("head"): tc(d, 470, s["head"], F_KICK, MUTED, a, sp=4)
        y = 590
        for ln in s["lines"]:
            f = fit(d, ln, "Plex600", 56)
            tc(d, y, ln, f, INK, a, dy=24 * (1 - ease(t / 0.5))); y += 88
        if s.get("foot"): tc(d, y + 50, s["foot"], F_SMALL, MUTED, a)
    elif k == "stat":
        tc(d, 450, s["kick"], F_KICK, MUTED, a, sp=4)
        tc(d, 530, s["name"], fit(d, s["name"], "BSD900", 96), INK, a)
        tc(d, 650, s["big"], fit(d, s["big"], "BSD900", 330), s.get("col", GOLD), a, dy=40 * (1 - ease(t / 0.5)))
        tc(d, 1010, s["bigsub"], F_MEAN, INK, a)
        for i, ln in enumerate(s.get("lines", [])):
            tc(d, 1110 + 60 * i, ln, fit(d, ln, "Plex500", 38), MUTED, a)
    elif k == "rows":
        tc(d, 400, s["kick"], F_KICK, MUTED, a, sp=4)
        for n, (title, sub, big, lab) in enumerate(s["rows"]):
            ar = a * ease((t - 0.3 - n * 0.6) / 0.5)
            if ar <= 0: continue
            y = 490 + n * 300 + 40 * (1 - ease((t - 0.3 - n * 0.6) / 0.5))
            d.rounded_rectangle([60, y, W - 60, y + 250], radius=22, fill=PANEL + (int(255 * ar),), outline=LINE + (int(255 * ar),), width=2)
            d.rectangle([60, y + 20, 70, y + 230], fill=OR + (int(255 * ar),))
            tl(d, 100, y + 38, title, fit(d, title, "BSD900", 70, maxw=560), INK, ar)
            tl(d, 100, y + 130, sub, fit(d, sub, "Plex600", 34, maxw=560), MUTED, ar)
            tr(d, W - 100, y + 30, big, font("BSD900", 120), GOLD, ar)
            tr(d, W - 100, y + 170, lab, F_LAB, MUTED, ar)
    elif k == "week":
        tc(d, 450, s["kick"], F_KICK, MUTED, a, sp=4)
        tc(d, 520, s["big"], font("BSD900", 330), GOLD, a, dy=30 * (1 - ease(t / 0.5)))
        tc(d, 880, s["bigsub"], F_MEAN, INK, a, sp=2)
        n = len(s["days"]); cw = 120; gap = 12
        x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
        for i, (dn, rec, good) in enumerate(s["days"]):
            ar = a * ease((t - 0.6 - i * 0.2) / 0.4)
            if ar <= 0: continue
            x = x0 + i * (cw + gap)
            d.rounded_rectangle([x, 1030, x + cw, 1230], radius=16, fill=PANEL + (int(255 * ar),), outline=LINE + (int(255 * ar),), width=2)
            tc(d, 1048, dn, font("Plex600", 28), MUTED, ar, x=x + cw / 2)
            tc(d, 1110, rec, font("BSD900", 52), GREEN if good else INK, ar, x=x + cw / 2)
        tc(d, 1300, s["foot"], F_MEAN, INK, a)

def make(spec, out, preview=None):
    slides = spec["slides"]
    t0 = 0.0
    for s in slides:
        s["t0"] = t0; t0 += s["dur"]
    end0 = t0; DUR = end0 + 2.2
    N = int(DUR * FPS)

    def frame(i):
        t = i / FPS
        img = BGI.copy(); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        paste_logo(img, LOGO_SMALL, W // 2, 235, vis(t, 0, end0 - 0.1, 0.3, 0.35))
        tc(d, 345, spec["series"], F_KICK, OR, vis(t, 0, end0 - 0.1, 0.3, 0.3), sp=5) if False else None
        tc(d, 1700, "Research, not betting advice.", F_SMALL, MUTED, 0.9 * vis(t, 0, DUR, 0.3, 0.25))
        for s in slides:
            a = vis(t, s["t0"], s["t0"] + s["dur"], 0.35, 0.3)
            if a > 0: draw_slide(d, s, t - s["t0"], a)
        # series tag
        tc(d, 330, spec["series"], font("Plex600", 30), OR, vis(t, 0, end0 - 0.1, 0.3, 0.3), sp=5)
        ae = vis(t, end0, DUR, 0.4, 0.25)
        if ae > 0:
            sc = 0.86 + 0.14 * ease_back((t - end0) / 0.6)
            paste_logo(img, logo_at(max(10, int(640 * sc))), W // 2, 640, ae)
        tc(d, 1010, "DO THE HOMEWORK.", F_END, INK, ae, dy=20 * (1 - ease((t - end0 - 0.2) / 0.5)))
        tc(d, 1170, spec.get("endsub", "New research every day."), F_SUB, MUTED, ae)
        img.alpha_composite(ov)
        return img.convert("RGB")

    if preview:
        os.makedirs("/home/claude/out/prev", exist_ok=True)
        for sec in preview:
            frame(int(float(sec) * FPS)).save(f"/home/claude/out/prev/{spec['id']}_{sec}.png")
        return DUR
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    return DUR

RS = "HOW I RESEARCH A PROP"
VIDEOS = {
 "ep1_minutes": dict(id="ep1_minutes", series=RS + "  1/5", slides=[
   dict(kind="hook", dur=3.4, lines=["MINUTES"], colors=[GOLD], size=300, sub="The stat behind the stat"),
   dict(kind="text", dur=3.8, head="WHY IT MATTERS", lines=["Points need minutes.", "Before the line,", "check how long he's playing."]),
   dict(kind="stat", dur=5.4, kick="NOV 13  -  SAS 123, GSW 85", name="DE'AARON FOX", big="17 MIN", bigsub="usually plays 30", lines=["Finished with 8 pts + ast", "against a 20.5 line"]),
   dict(kind="text", dur=3.4, head="THE TAKEAWAY", lines=["Minutes first.", "Everything else second."])]),
 "ep2_blowout": dict(id="ep2_blowout", series=RS + "  2/5", slides=[
   dict(kind="hook", dur=3.4, lines=["BLOWOUT", "RISK"], colors=[GOLD, INK], size=230, sub="Big spreads shrink starters' minutes"),
   dict(kind="text", dur=3.6, head="WHY IT MATTERS", lines=["When a game gets out of hand,", "starters sit.", "Their stats stop."]),
   dict(kind="rows", dur=6.0, kick="NOV 13  -  SAS 123, GSW 85", rows=[("DE'AARON FOX", "usually plays 30 min", "17", "MIN PLAYED"), ("BRANDIN PODZIEMSKI", "usually plays 34 min", "22", "MIN PLAYED"), ("DRAYMOND GREEN", "usually plays 27 min", "16", "MIN PLAYED")]),
   dict(kind="text", dur=3.4, head="THE TAKEAWAY", lines=["Check the spread", "before the stat line."])]),
 "ep3_teammates": dict(id="ep3_teammates", series=RS + "  3/5", slides=[
   dict(kind="hook", dur=3.4, lines=["WHO'S OUT?"], colors=[GOLD], size=230, sub="When one player sits, usage moves"),
   dict(kind="text", dur=4.0, head="WHY IT MATTERS", lines=["Shots, touches and minutes", "go to someone else.", "Check injuries before averages."]),
   dict(kind="text", dur=4.8, head="NOV 13  -  UTA AT HOU", lines=["Lauri Markkanen was out.", "Josh Green played 14 minutes", "and finished with 2 pts + reb."], foot="The extra usage didn't show up."),
   dict(kind="text", dur=3.6, head="THE TAKEAWAY", lines=["A flag is context,", "not a guarantee."])]),
 "ep4_linemove": dict(id="ep4_linemove", series=RS + "  4/5", slides=[
   dict(kind="hook", dur=3.4, lines=["LINES MOVE"], colors=[GOLD], size=210, sub="The number you see isn't the first number"),
   dict(kind="text", dur=3.8, head="WHY IT MATTERS", lines=["Lines move on news.", "By the time you look,", "it may already be priced in."]),
   dict(kind="stat", dur=5.4, kick="OCT 30  -  TYRESE MAXEY", name="POINTS + REB + AST", big="30.5 TO 34.5", bigsub="opened at 30.5, moved to 34.5", lines=["He finished with 35"]),
   dict(kind="text", dur=3.6, head="THE TAKEAWAY", lines=["Know where it opened.", "Then ask why it moved."])]),
 "ep5_matchup": dict(id="ep5_matchup", series=RS + "  5/5", slides=[
   dict(kind="hook", dur=3.4, lines=["MATCHUP", "RANK"], colors=[GOLD, INK], size=230, sub="How the defense ranks vs his position"),
   dict(kind="text", dur=3.8, head="WHY IT MATTERS", lines=["Some defenses shut down", "guards. Others shut down bigs.", "Position matters."]),
   dict(kind="stat", dur=5.4, kick="OCT 27  -  MICHAEL PORTER JR.", name="BKN AT BOS", big="1ST", bigsub="BOS ranked 1st vs forwards", lines=["He still finished with", "29 pts + ast on a 22.5 line"]),
   dict(kind="text", dur=3.6, head="THE TAKEAWAY", lines=["A tough matchup", "is a flag, not a wall."])]),
 "blowout_report": dict(id="blowout_report", series="BLOWOUT REPORT", endsub="Every week.", slides=[
   dict(kind="hook", dur=3.4, lines=["BLOWOUT", "REPORT"], colors=[GOLD, INK], size=230, sub="NOV 7 - 13"),
   dict(kind="rows", dur=7.0, kick="BIGGEST BLOWOUTS OF THE WEEK", rows=[("GSW 138, NOP 87", "Julian Reese: 9 min (usually 31)", "51", "PT MARGIN"), ("OKC 114, WAS 75", "Anthony Gill: 9 min (usually 26)", "39", "PT MARGIN"), ("MIN 133, DAL 94", "Santi Aldama: 10 min (usually 30)", "39", "PT MARGIN")]),
   dict(kind="text", dur=3.6, head="WHY IT MATTERS", lines=["Big margins cut minutes.", "That changes every prop", "on the board."])]),
 "myth_highline": dict(id="myth_highline", series="PROP MYTHS", endsub="More myths, every week.", slides=[
   dict(kind="hook", dur=3.4, lines=["MYTH"], colors=[RED], size=300, sub="A high line is a hard prop"),
   dict(kind="text", dur=5.2, head="THE FACT", lines=["A line is a number.", "It isn't a difficulty rating.", "The minutes and role", "behind it are what matter."]),
   dict(kind="text", dur=3.4, head="THE TAKEAWAY", lines=["Judge the role,", "not the number."])]),
 "myth_hotstreak": dict(id="myth_hotstreak", series="PROP MYTHS", endsub="More myths, every week.", slides=[
   dict(kind="hook", dur=3.4, lines=["MYTH"], colors=[RED], size=300, sub="He's hot, so it keeps going"),
   dict(kind="text", dur=5.2, head="THE FACT", lines=["A streak is the past.", "A projection looks at", "minutes, matchup and role."]),
   dict(kind="text", dur=3.4, head="THE TAKEAWAY", lines=["Ask why he's hot.", "Not just that he is."])]),
 "week_review": dict(id="week_review", series="WEEK IN REVIEW", endsub="Results posted every morning.", slides=[
   dict(kind="week", dur=9.0, kick="HEAT CHECK  -  NOV 7 - 13", big="17-4", bigsub="81% HIT RATE THIS WEEK", foot="46-23 on the season",
        days=[("SAT", "1-2", False), ("SUN", "2-1", False), ("MON", "3-0", True), ("TUE", "3-0", True), ("WED", "3-0", True), ("THU", "2-1", False), ("FRI", "3-0", True)])]),
}


# ---------------------------------------------------------------- data-driven weekly videos
import json, re
from datetime import date as _D, timedelta as _T

def _recs(path): return sorted(json.load(open(path)), key=lambda e: e["id"])
def _graded(e):
    t = e.get("top") or []
    return len(t) > 0 and all(p.get("r") in ("hit", "miss") for p in t)
def _fmt(d): return d.strftime("%b %-d").upper()

def week_window(recs, end=None):
    last = _D.fromisoformat(end or [e for e in recs if _graded(e)][-1]["id"])
    return last - _T(days=6), last

def spec_week_review(recs, end=None):
    a, b = week_window(recs, end)
    days = []; wh = wm = 0
    by = {e["id"]: e for e in recs}
    d = a
    while d <= b:
        e = by.get(d.isoformat())
        if e and _graded(e):
            h = sum(1 for p in e["top"] if p["r"] == "hit"); m = len(e["top"]) - h; wh += h; wm += m
            days.append((d.strftime("%a").upper(), f"{h}-{m}", h * 2 >= len(e["top"])))
        d += _T(days=1)
    sh = sum(1 for e in recs if e["id"] <= b.isoformat() for p in e.get("top") or [] if p.get("r") == "hit")
    sm = sum(1 for e in recs if e["id"] <= b.isoformat() for p in e.get("top") or [] if p.get("r") == "miss")
    pct = round(100 * wh / max(1, wh + wm))
    spec = dict(id="week_review", series="WEEK IN REVIEW", endsub="Results posted every morning.", slides=[
        dict(kind="week", dur=9.0, kick=f"HEAT CHECK  -  {_fmt(a)} - {_fmt(b).split()[-1] if a.month == b.month else _fmt(b)}",
             big=f"{wh}-{wm}", bigsub=f"{pct}% HIT RATE THIS WEEK", foot=f"{sh}-{sm} on the season", days=days)])
    return spec, dict(wh=wh, wm=wm, pct=pct, sh=sh, sm=sm, start=a.isoformat(), end=b.isoformat(), days=days)

def spec_blowout_report(recs, end=None):
    a, b = week_window(recs, end)
    found = []
    for e in recs:
        if not (a.isoformat() <= e["id"] <= b.isoformat()): continue
        for g in e.get("odd") or []:
            its = " ".join(g.get("it") or []); m = re.search(r"decided by (\d+)", its)
            sc = re.findall(r"([A-Z]{2,4}) (\d+)", g.get("s") or "")
            if not m or len(sc) != 2: continue
            drops = []
            for pl in g.get("pl") or []:
                mm = re.match(r"(.+?): (\d+) min \(usually (\d+)\)", pl)
                if mm: drops.append((int(mm.group(3)) - int(mm.group(2)), pl))
            if not drops: continue
            drops.sort(reverse=True)
            w, l = sorted([(t, int(v)) for t, v in sc], key=lambda x: -x[1])
            found.append((int(m.group(1)), f"{w[0]} {w[1]}, {l[0]} {l[1]}", drops[0][1]))
    found.sort(reverse=True)
    if len(found) < 3: return None, dict(found=len(found))
    rows = [(g, pl, str(mg), "PT MARGIN") for mg, g, pl in found[:3]]
    spec = dict(id="blowout_report", series="BLOWOUT REPORT", endsub="Every week.", slides=[
        dict(kind="hook", dur=3.4, lines=["BLOWOUT", "REPORT"], colors=[GOLD, INK], size=230, sub=f"{_fmt(a)} - {_fmt(b).split()[-1] if a.month == b.month else _fmt(b)}"),
        dict(kind="rows", dur=7.0, kick="BIGGEST BLOWOUTS OF THE WEEK", rows=rows),
        dict(kind="text", dur=3.6, head="WHY IT MATTERS", lines=["Big margins cut minutes.", "That changes every prop", "on the board."])])
    return spec, dict(rows=rows, start=a.isoformat(), end=b.isoformat())

def make_cover(mp4):
    # Frame 0 is near-black (elements animate in), so Instagram needs an explicit cover.
    cov = mp4.rsplit('.', 1)[0] + '_cover.jpg'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','1.6','-i',mp4,'-frames:v','1','-q:v','2',cov], check=True)
    return cov


def add_beat(silent, out, dur):
    import subprocess
    fo = max(0, dur - 1.5)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(HERE, "beat.wav"), "-filter_complex",
        f"[1:a]atrim=0:{dur},loudnorm=I=-15:TP=-1.5:LRA=7,afade=t=in:d=0.3,afade=t=out:st={fo}:d=1.5[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out])

def week_caption(info):
    days = " ".join(f"{d[0].title()} {d[1]}" for d in info["days"])
    return (f"📊 WEEK IN REVIEW: {info['wh']}-{info['wm']} on the Heat Check! 🔥 ({info['pct']}% hit rate)\n\n"
            f"🗓️ {days}\n\nThat's {info['sh']}-{info['sm']} on the season 🏀 Every morning we break down the NBA stats and trends behind the numbers 🧠\n\n"
            "Research, not betting advice. Do the homework! 👇\nWhich night was your favorite?\n\n"
            "#NBA #NBAStats #BasketballAnalytics #HeatCheck #CourtsideEdge #NBAHighlights")

def blowout_caption(info):
    lines = ["💥 BLOWOUT REPORT: the biggest blowouts of the week and who sat 🪑\n"]
    for g, pl, mg, _ in info["rows"]: lines.append(f"🏀 {g} ({mg}-pt margin): {pl}")
    lines += ["\nBig margins cut starters' minutes, and that changes every prop on the board 📉",
              "\nResearch, not betting advice. Do the homework! 👇\nWhat was the most lopsided game you watched?",
              "\n#NBA #NBAStats #BasketballAnalytics #NBABlowouts #CourtsideEdge #NBAHighlights"]
    return "\n".join(lines)

if __name__ == "__main__":
    # usage: python3 studio/series.py weekly RECORD_JSON OUT_DIR [END_DATE]
    #        python3 studio/series.py evergreen NAME OUT_MP4      (static how-to / myth videos)
    mode = sys.argv[1]
    if mode == "weekly":
        recs = _recs(sys.argv[2]); out = sys.argv[3]; end = sys.argv[4] if len(sys.argv) > 4 else None
        os.makedirs(out, exist_ok=True)
        for fn, spec_fn, cap_fn in (("week_review", spec_week_review, week_caption), ("blowout_report", spec_blowout_report, blowout_caption)):
            spec, info = spec_fn(recs, end)
            if not spec: print("skip", fn, info); continue
            sil = os.path.join(out, fn + ".silent.mp4"); fin = os.path.join(out, f"{fn}_{info.get('end', end)}.mp4")
            dur = make(spec, sil); add_beat(sil, fin, dur); os.remove(sil); make_cover(fin)
            open(fin[:-4] + ".txt", "w").write(cap_fn(info)); json.dump(info, open(fin[:-4] + ".json", "w"), indent=1)
            print("ok", fin)
    else:
        dur = make(VIDEOS[sys.argv[2]], sys.argv[3]); print("done", round(dur, 1))
