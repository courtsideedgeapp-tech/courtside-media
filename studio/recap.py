"""Courtside Edge - daily Heat Check recap video (data-driven).

usage: python3 studio/recap.py RECORD_JSON OUT_DIR [YYYY-MM-DD]
  RECORD_JSON  array of daily entries (data/record.json from the Courtside Edge artifact)
  OUT_DIR      writes recap_<date>.mp4 (with beat), recap_<date>.txt (caption), recap_<date>.json (facts)
  date         defaults to the latest fully graded day
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
DUR = 19.0
N = int(DUR * FPS)

MKT = {"pts": "PTS", "reb": "REB", "ast": "AST", "fg3m": "3PM", "pa": "PTS + AST", "ra": "REB + AST",
       "pr": "PTS + REB", "pra": "PTS + REB + AST", "stl": "STL", "blk": "BLK"}

# ---------------------------------------------------------------- data
def load_facts(rec_path, date=None):
    recs = json.load(open(rec_path))
    recs = sorted(recs, key=lambda e: e["id"])
    def graded(e):
        t = e.get("top") or []
        return len(t) > 0 and all(p.get("r") in ("hit", "miss") for p in t)
    if date is None:
        date = [e for e in recs if graded(e)][-1]["id"]
    e = [x for x in recs if x["id"] == date][0]
    top = e["top"]
    hits = sum(1 for p in top if p["r"] == "hit"); n = len(top)
    sh = sm = 0
    for x in recs:
        if x["id"] <= date:
            for p in x.get("top") or []:
                if p.get("r") == "hit": sh += 1
                elif p.get("r") == "miss": sm += 1
    # last 7 calendar days ending at date
    from datetime import date as D, timedelta
    d0 = D.fromisoformat(date)
    wk = [x for x in recs if d0 - timedelta(days=6) <= D.fromisoformat(x["id"]) <= d0]
    wh = sum(1 for x in wk for p in x.get("top") or [] if p.get("r") == "hit")
    wm = sum(1 for x in wk for p in x.get("top") or [] if p.get("r") == "miss")
    picks = []
    for p in top:
        picks.append(dict(name=p["n"], market=MKT.get(p["m"], p["m"].upper()), side=p["s"].upper(), line=p["l"],
                          final=p["v"], mins=p.get("mn"), usual=p.get("um"), hit=p["r"] == "hit", team=p.get("t")))
    return dict(date=date, hits=hits, n=n, picks=picks, season=(sh, sm), week=(wh, wm), insight=find_insight(e.get("odd") or []))

def parse_score(s):
    m = re.findall(r"([A-Z]{2,4}) (\d+)", s or "")
    if len(m) != 2: return None
    a, b = (m[0][0], int(m[0][1])), (m[1][0], int(m[1][1]))
    return (a, b) if a[1] >= b[1] else (b, a)

def find_insight(odd):
    best = None
    for g in odd:
        its = " ".join(g.get("it") or [])
        m = re.search(r"decided by (\d+)", its)
        margin = int(m.group(1)) if m else 0
        sc = parse_score(g.get("s"))
        drops = []
        for pl in g.get("pl") or []:
            mm = re.match(r"(.+?): (\d+) min \(usually (\d+)\)", pl)
            if mm: drops.append((int(mm.group(3)) - int(mm.group(2)), mm.group(1), int(mm.group(2)), int(mm.group(3))))
        drops.sort(reverse=True)
        if sc and margin >= 20 and drops and (best is None or margin > best["margin"]):
            best = dict(kind="blowout", margin=margin, winner=sc[0], loser=sc[1], player=drops[0][1],
                        mins=drops[0][2], usual=drops[0][3], game=g.get("g"))
    if best: return best
    # fallback: biggest total vs line surprise
    for g in odd:
        for it in g.get("it") or []:
            m = re.match(r"(\d+) total points, ([\d.]+) (over|under) the ([\d.]+) line", it)
            if m and parse_score(g.get("s")):
                sc = parse_score(g["s"])
                return dict(kind="total", total=int(m.group(1)), diff=float(m.group(2)), dirn=m.group(3), line=float(m.group(4)),
                            winner=sc[0], loser=sc[1], game=g.get("g"))
    return None

# ---------------------------------------------------------------- caption
def caption(f):
    h, n = f["hits"], f["n"]; sh, sm = f["season"]
    pct = round(100 * sh / max(1, sh + sm))
    sweep = h == n
    lead = {3: "🔥 CLEAN SWEEP", 2: "✅ 2 for 3", 1: "📉 1 for 3", 0: "🧊 Tough night"}.get(h, f"{h}/{n}") if n == 3 else f"{h}/{n}"
    lines = [f"{lead}: last night's Heat Check went {h}-{n-h} 🏀"]
    for p in f["picks"]:
        lines.append(f"{'✅' if p['hit'] else '❌'} {p['name']} {p['side'].lower()} {p['line']} {p['market']} → {p['final']}")
    ins = f.get("insight")
    if ins and ins["kind"] == "blowout":
        lines.append(f"\n💥 Story of the night: {ins['winner'][0]} {ins['winner'][1]}, {ins['loser'][0]} {ins['loser'][1]}. "
                     f"{ins['player']} played {ins['mins']} min (usually {ins['usual']}). Blowouts steal minutes!")
    lines.append(f"\n📈 Season Heat Check: {sh}-{sm} ({pct}%)")
    lines.append("Every morning we break down the NBA stats and trends behind the numbers 🧠")
    lines.append("Research, not betting advice. Do the homework! 👇\nWhich result surprised you most?")
    lines.append("\n#NBA #NBAStats #BasketballAnalytics #HeatCheck #CourtsideEdge #NBAHighlights")
    return "\n".join(lines)

# ---------------------------------------------------------------- drawing
def font(name, size): return ImageFont.truetype(os.path.join(HERE, "fonts", name + ".ttf"), size)
BG = (11, 13, 16); PANEL = (20, 23, 28); LINE = (38, 43, 51)
INK = (244, 241, 234); MUTED = (163, 168, 176)
OR = (255, 106, 31); GOLD = (245, 197, 66); GREEN = (72, 201, 130); RED = (222, 58, 92)

F_HOOK = font("BSD800", 84); F_BIG = font("BSD900", 520); F_SUB = font("Plex500", 40)
F_PROP = font("Plex600", 38); F_VAL = font("BSD900", 120); F_VLAB = font("Plex600", 28)
F_BADGE = font("BSD900", 40); F_MEAN = font("Plex600", 54); F_SMALL = font("Plex500", 36)
F_REC = font("BSD900", 330); F_END = font("BSD900", 120); F_SCORE = font("BSD900", 120)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
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
    cd.rectangle([380, 1180, 700, 1700], outline=lc, width=4); cd.ellipse([380, 1020, 700, 1340], outline=lc, width=4)
    cd.arc([-80, 940, 1160, 2180], 202, 338, fill=lc, width=4); cd.line([(60, 1700), (1020, 1700)], fill=lc, width=4)
    cd.ellipse([500, 1640, 580, 1720], outline=lc, width=4)
    base.alpha_composite(court); return base

logo_big = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
def logo_at(size): return logo_big.resize((size, size), Image.LANCZOS)
def paste_logo(img, im, cx, cy, a):
    if a <= 0: return
    if a < 1:
        r, g, b, al = im.split(); al = al.point(lambda v: int(v * a)); im = Image.merge("RGBA", (r, g, b, al))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def tw(d, s, f, sp=0): return d.textlength(s, font=f) + sp * max(0, len(s) - 1)
def draw_sp(d, x, y, s, f, fill, a, sp=0):
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill + (int(255 * a),)); cx += d.textlength(ch, font=f) + sp
def text_c(d, y, s, f, fill, a, dy=0, sp=0, x=W // 2):
    if a <= 0: return
    w = tw(d, s, f, sp)
    if sp: draw_sp(d, x - w / 2, y + dy, s, f, fill, a, sp)
    else: d.text((x - w / 2, y + dy), s, font=f, fill=fill + (int(255 * a),))
def text_l(d, x, y, s, f, fill, a, sp=0):
    if a <= 0: return
    if sp: draw_sp(d, x, y, s, f, fill, a, sp)
    else: d.text((x, y), s, font=f, fill=fill + (int(255 * a),))
def text_r(d, xr, y, s, f, fill, a):
    if a <= 0: return
    d.text((xr - d.textlength(s, font=f), y), s, font=f, fill=fill + (int(255 * a),))
def fit(name, s, maxw, start=62, lo=34):
    for sz in range(start, lo - 1, -2):
        f = font(name, sz)
        if f.getlength(s) <= maxw: return f
    return font(name, lo)

def render(facts, out_silent):
    BGI = make_bg(); LOGO_SMALL = logo_at(170)
    picks = facts["picks"]; hits, n = facts["hits"], facts["n"]; sh, sm = facts["season"]
    ins = facts["insight"]; pct = round(1000 * sh / max(1, sh + sm)) / 10
    big = f"{hits}-{n - hits}"
    sub = {3: "CLEAN SWEEP", 2: "SOLID NIGHT", 1: "TOUGH ONE", 0: "ROUGH NIGHT"}.get(hits, "") if n == 3 else "THE RESULTS"
    big_col = GOLD if hits * 2 >= n else MUTED
    card_h, gap = 250, 50
    def frame(i):
        t = i / FPS
        img = BGI.copy(); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        paste_logo(img, LOGO_SMALL, W // 2, 235, vis(t, 0, 16.6, 0.3, 0.35))
        text_c(d, 1700, "Research, not betting advice.", F_SMALL, MUTED, 0.9 * vis(t, 0, 19.0, 0.3, 0.25))
        a = vis(t, 0.0, 3.4); k = ease_back(t / 0.7)
        text_c(d, 420, "LAST NIGHT'S HEAT CHECK", F_HOOK, INK, a, dy=70 * (1 - k), sp=3)
        k2 = ease_back((t - 0.15) / 0.7)
        text_c(d, 560, big, F_BIG, big_col, a, dy=90 * (1 - k2))
        ln = ease((t - 0.5) / 0.7)
        if a > 0: d.rectangle([W / 2 - 220 * ln, 1195, W / 2 + 220 * ln, 1200], fill=OR + (int(255 * a),))
        text_c(d, 1235, sub, F_SUB, MUTED, a, sp=8)
        ab = vis(t, 3.4, 11.6, fin=0.4, fout=0.4)
        if ab > 0:
            text_c(d, 380, "THE RESULTS", F_SUB, MUTED, ab, sp=8)
            for k_, p in enumerate(picks[:3]):
                t0 = 4.0 + k_ * 2.3; ar = ab * ease((t - t0) / 0.5)
                if ar <= 0: continue
                y = 480 + k_ * (card_h + gap) + 40 * (1 - ease((t - t0) / 0.5)); col = GREEN if p["hit"] else RED
                d.rounded_rectangle([60, y, W - 60, y + card_h], radius=22, fill=PANEL + (int(255 * ar),), outline=LINE + (int(255 * ar),), width=2)
                d.rectangle([60, y + 20, 70, y + 230], fill=col + (int(255 * ar),))
                nm = p["name"].upper(); fn = fit("BSD900", nm, W - 100 - 100 - 330 - 80)
                text_l(d, 100, y + 34, nm, fn, INK, ar)
                text_l(d, 100, y + 128, f"{p['side']} {p['line']}  {p['market']}", F_PROP, MUTED, ar)
                if p.get("mins") is not None: text_l(d, 100, y + 184, f"PLAYED {p['mins']} MIN", F_VLAB, MUTED, ar, sp=3)
                text_r(d, W - 330, y + 40, str(p["final"]), F_VAL, INK, ar); text_r(d, W - 330, y + 170, "FINAL", F_VLAB, MUTED, ar)
                ah = ar * ease((t - t0 - 0.45) / 0.35)
                if ah > 0:
                    lab = "HIT" if p["hit"] else "MISS"
                    d.rounded_rectangle([W - 290, y + 78, W - 100, y + 172], radius=14, fill=col + (int(255 * ah),))
                    bw = tw(d, lab, F_BADGE, 4); draw_sp(d, W - 195 - bw / 2, y + 101, lab, F_BADGE, BG, ah, 4)
        a = vis(t, 11.6, 15.2)
        if a > 0 and not ins:
            wh, wm = facts["week"]
            text_c(d, 470, "LAST 7 DAYS", F_SUB, MUTED, a, sp=8)
            text_c(d, 560, f"{wh}-{wm}", F_REC, GOLD if wh >= wm else MUTED, a)
            text_c(d, 960, f"{round(100 * wh / max(1, wh + wm))}% HIT RATE", F_MEAN, INK, a, sp=2)
        if a > 0 and ins:
            text_c(d, 500, "BIGGEST STORY OF THE NIGHT", F_SUB, MUTED, a, sp=4)
            if ins["kind"] == "blowout":
                w, l = ins["winner"], ins["loser"]
                text_c(d, 600, f"{w[0]} {w[1]}  -  {l[0]} {l[1]}", F_SCORE, INK, a)
                text_c(d, 790, f"A {ins['margin']}-point blowout.", F_MEAN, INK, a)
                last = ins["player"].split()[-1] if len(ins["player"].split()) > 1 else ins["player"]
                text_c(d, 880, f"{ins['player']} played {ins['mins']} minutes", F_MEAN, INK, a)
                text_c(d, 950, f"(usually {ins['usual']}).", F_MEAN, INK, a)
                text_c(d, 1080, "Blowouts cut starters' minutes.", F_SMALL, MUTED, a)
            else:
                w, l = ins["winner"], ins["loser"]
                text_c(d, 600, f"{w[0]} {w[1]}  -  {l[0]} {l[1]}", F_SCORE, INK, a)
                text_c(d, 790, f"{ins['total']} total points.", F_MEAN, INK, a)
                text_c(d, 880, f"{ins['diff']:g} {ins['dirn']} the {ins['line']:g} line.", F_MEAN, INK, a)
                text_c(d, 1030, "Pace and scoring swings matter.", F_SMALL, MUTED, a)
        a = vis(t, 15.2, 16.9)
        text_c(d, 470, "SEASON HEAT CHECK RECORD", F_SUB, MUTED, a, sp=4)
        text_c(d, 560, f"{sh}-{sm}", F_REC, GOLD, a, dy=30 * (1 - ease((t - 15.2) / 0.5)))
        text_c(d, 960, f"{pct:g}% HIT RATE", F_MEAN, INK, a, sp=2)
        a = vis(t, 16.9, 19.0, fin=0.4, fout=0.25)
        if a > 0:
            s = 0.86 + 0.14 * ease_back((t - 16.9) / 0.6); paste_logo(img, logo_at(max(10, int(640 * s))), W // 2, 640, a)
        text_c(d, 1010, "DO THE HOMEWORK.", F_END, INK, a, dy=20 * (1 - ease((t - 17.1) / 0.5)))
        img.alpha_composite(ov); return img.convert("RGB")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_silent]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    return frame

def stamp_first_frame(mp4):
    # Frame 0 is near-black (elements animate in), and TikTok/Instagram show frame 0 while a video loads.
    # Prepend one frame copied from the settled title state (1.6s) so the loading thumbnail is never black.
    png = mp4.rsplit('.', 1)[0] + '_f0.png'; tmp = mp4.rsplit('.', 1)[0] + '_st.mp4'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','1.6','-i',mp4,'-frames:v','1',png], check=True)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','30','-loop','1','-t','0.034','-i',png,'-i',mp4,
        '-filter_complex','[0:v]fps=30,format=yuv420p[a];[1:v]format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v];[1:a]adelay=34|34[au]',
        '-map','[v]','-map','[au]','-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',tmp], check=True)
    os.replace(tmp, mp4); os.remove(png)

def make_cover(mp4):
    stamp_first_frame(mp4)
    # Frame 0 is near-black (elements animate in), so Instagram needs an explicit cover.
    # Take the settled frame at 1.6s, then shift the content down 170px so the logo and
    # headline survive Instagram's 3:4 center crop on the profile grid.
    cov = mp4.rsplit('.', 1)[0] + '_cover.jpg'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','1.6','-i',mp4,'-frames:v','1','-q:v','2',cov], check=True)
    from PIL import Image, ImageDraw
    im = Image.open(cov).convert('RGB'); W, H = im.size
    out = im.copy(); ImageDraw.Draw(out).rectangle((0, 0, W, 1670), fill=(11, 13, 16))
    out.paste(im.crop((0, 0, W, 1500)), (0, 170)); out.save(cov, quality=93)
    return cov


def add_beat(silent, out):
    fo = max(0, DUR - 1.5)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(HERE, "beat.wav"), "-filter_complex",
        f"[1:a]atrim=0:{DUR},loudnorm=I=-15:TP=-1.5:LRA=7,afade=t=in:d=0.3,afade=t=out:st={fo}:d=1.5[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out])

if __name__ == "__main__":
    rec, outdir = sys.argv[1], sys.argv[2]; date = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(outdir, exist_ok=True)
    facts = load_facts(rec, date); d = facts["date"]
    silent = os.path.join(outdir, f"recap_{d}.silent.mp4"); final = os.path.join(outdir, f"recap_{d}.mp4")
    fr = render(facts, silent); add_beat(silent, final); os.remove(silent)
    make_cover(final)
    open(os.path.join(outdir, f"recap_{d}.txt"), "w").write(caption(facts))
    json.dump(facts, open(os.path.join(outdir, f"recap_{d}.json"), "w"), indent=1)
    fr(int(13 * FPS)).save(os.path.join(outdir, f"recap_{d}_insight.png"))
    fr(int(8 * FPS)).save(os.path.join(outdir, f"recap_{d}_results.png"))
    print("ok", final)
