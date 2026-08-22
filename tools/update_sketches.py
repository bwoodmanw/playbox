# -*- coding: utf-8 -*-
"""Slice sheets into individual traces, rebuild the manifest, commit and push.

    python tools/update_sketches.py            # slice, build, commit, push
    python tools/update_sketches.py --dry-run  # show what would happen
    python tools/update_sketches.py --no-push  # slice, build, commit only

Folders
    traces/sheets/    grids to be cut up. Not published; only the slices are.
    traces/           the individual traces the app serves.
    traces/_private/  never scanned, never published. Anything you hold no
                      rights to belongs here.

The sheet's filename decides the labels: torso.png produces torso-01.png ...
which the app lists as "Torso 01".
"""

import os, re, sys, json, subprocess, shutil

try:
    from PIL import Image, ImageFilter, ImageOps, ImageStat
except ImportError:
    print("This needs Pillow:  python -m pip install Pillow")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACES = os.path.join(ROOT, "traces")
SHEETS = os.path.join(TRACES, "sheets")
PRIVATE = os.path.join(TRACES, "_private")
STATE = os.path.join(SHEETS, ".sliced.json")

IMG = (".png", ".jpg", ".jpeg", ".webp")
HOLD = os.path.join(TRACES, "_hold")
MAX_SIDE = 460
DRY = "--dry-run" in sys.argv
NO_PUSH = "--no-push" in sys.argv


def slug(name):
    s = os.path.splitext(name)[0].lower()
    s = re.sub(r"\b(cut|sheet|sheets|final|copy|\d+)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "trace"


def find_grid(im, want=None):
    """Locate the separator lines. Falls back to an even split."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    step = max(1, h // 400)

    def dark_col(x):
        n = t = 0
        for y in range(0, h, step):
            t += 1
            if px[x, y] < 200:
                n += 1
        return n / float(t)

    def dark_row(y):
        n = t = 0
        for x in range(0, w, max(1, w // 400)):
            t += 1
            if px[x, y] < 200:
                n += 1
        return n / float(t)

    def runs(vals, size):
        # a separator is either a ruled line (nearly all dark) or a blank gap
        hits = [i for i, v in enumerate(vals) if v > 0.80 or v < 0.004]
        out, run = [], []
        for i in hits:
            if run and i - run[-1] > 2:
                out.append(sum(run) // len(run)); run = []
            run.append(i)
        if run:
            out.append(sum(run) // len(run))
        return [c for c in out if 4 < c < size - 4]

    vcols = runs([dark_col(x) for x in range(w)], w)
    hrows = runs([dark_row(y) for y in range(h)], h)

    xs = [0] + vcols + [w]
    ys = [0] + hrows + [h]
    cols, rows = len(xs) - 1, len(ys) - 1

    ok = 2 <= cols <= 15 and 1 <= rows <= 10
    if ok and want and cols * rows != want:
        ok = False                      # trust the count in the filename
    if not ok:
        cols, rows = even_grid(w, h, want or 30)
        xs = [round(w * i / float(cols)) for i in range(cols + 1)]
        ys = [round(h * i / float(rows)) for i in range(rows + 1)]
    return xs, ys


def even_grid(w, h, n):
    """Pick the factor pair of n whose cells come out closest to portrait."""
    best, score = (10, 3), 1e9
    for cols in range(1, n + 1):
        if n % cols:
            continue
        rows = n // cols
        aspect = (w / float(cols)) / (h / float(rows))
        d = abs(aspect - 0.78)
        if d < score:
            best, score = (cols, rows), d
    return best


def is_lineart(im):
    """Line art is mostly white paper with a little ink on it. Anything else
    - colour, or dark shaded art - gets converted to outlines."""
    g = im.convert("L")
    hist = g.histogram()
    total = float(sum(hist)) or 1.0
    white = sum(hist[240:]) / total
    mean = ImageStat.Stat(g).mean[0]
    return white > 0.55 and mean > 195


def to_lineart(cell):
    """Leave existing line art alone; turn colour art into clean outlines."""
    if is_lineart(cell):
        return cell
    g = cell.convert("L").filter(ImageFilter.CONTOUR)
    # CONTOUR draws a frame round the edge - shave it off
    g = g.crop((2, 2, g.width - 2, g.height - 2))
    g = ImageOps.autocontrast(g, cutoff=1)
    g = g.point(lambda v: 255 if v > 205 else int(v * 0.55))
    return g.convert("RGB")


def erase_cell_number(cell):
    """Paint out the numeral in the top-left corner, but only if what is there
    is small enough to be a numeral rather than part of the drawing."""
    w, h = cell.size
    cw, chh = int(w * 0.16), int(h * 0.15)
    if cw < 4 or chh < 4:
        return cell
    corner = cell.crop((0, 0, cw, chh)).convert("L")
    ink = sum(1 for v in corner.getdata() if v < 200) / float(cw * chh)
    if ink < 0.30:                      # a numeral covers only a little of it
        cell = cell.copy()
        cell.paste((255, 255, 255), (0, 0, cw, chh))
    return cell


def slice_sheet(path, prefix, want=None):
    im = Image.open(path).convert("RGB")
    xs, ys = find_grid(im, want)
    made = []
    n = 0
    for r in range(len(ys) - 1):
        for c in range(len(xs) - 1):
            n += 1
            x0, x1 = xs[c], xs[c + 1]
            y0, y1 = ys[r], ys[r + 1]
            cw, ch = x1 - x0, y1 - y0
            # trim the rule lines and the printed cell number
            cell = im.crop((int(x0 + cw * 0.09), int(y0 + ch * 0.085),
                            int(x1 - cw * 0.025), int(y1 - ch * 0.02)))
            cell = erase_cell_number(cell)
            grey = cell.convert("L")
            box = grey.point(lambda v: 255 if v < 235 else 0).getbbox()
            if box:
                pad = 8
                cell = cell.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                                  min(cell.width, box[2] + pad),
                                  min(cell.height, box[3] + pad)))
            if cell.width < 20 or cell.height < 20:
                n -= 1
                continue
            cell.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            cell = to_lineart(cell)
            # line art needs very few tones; a small palette shrinks the PNG ~70%
            cell = cell.convert("L").quantize(colors=16, method=Image.MEDIANCUT)
            out = os.path.join(TRACES, "%s-%02d.png" % (prefix, n))
            if not DRY:
                cell.save(out, "PNG", optimize=True)
            made.append(out)
    return made


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, shell=isinstance(cmd, str),
                          capture_output=True, text=True, **kw)


def main():
    for d in (SHEETS, PRIVATE, HOLD):
        if not os.path.isdir(d):
            os.makedirs(d)

    # a sheet dropped straight into traces/ gets filed away automatically
    for f in sorted(os.listdir(TRACES)):
        p = os.path.join(TRACES, f)
        if not os.path.isfile(p) or not f.lower().endswith(IMG):
            continue
        if re.search(r"sheet|grid|\bcut\b", f, re.I) or os.path.getsize(p) > 900_000:
            print("filing %s -> traces/sheets/" % f)
            if not DRY:
                shutil.move(p, os.path.join(SHEETS, f))

    state = {}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE))
        except Exception:
            state = {}

    sheets = [f for f in sorted(os.listdir(SHEETS)) if f.lower().endswith(IMG)]
    if not sheets:
        print("No sheets in traces/sheets/ - nothing to cut.")

    total_new = []
    for f in sheets:
        p = os.path.join(SHEETS, f)
        stamp = "%d-%d" % (os.path.getsize(p), int(os.path.getmtime(p)))
        if state.get(f) == stamp:
            print("unchanged, skipping: %s" % f)
            continue
        prefix = slug(f)
        m = re.search(r"(\d+)", os.path.splitext(f)[0])
        want = int(m.group(1)) if m and 2 <= int(m.group(1)) <= 200 else None
        made = slice_sheet(p, prefix, want)
        print("cut %s into %d traces (%s-NN.png)" % (f, len(made), prefix))
        total_new += made
        state[f] = stamp

    if not DRY:
        json.dump(state, open(STATE, "w"), indent=2)

    r = run(["node", "tools/build-traces.mjs"])
    print(r.stdout.strip() or r.stderr.strip())

    if DRY:
        print("\n--dry-run: nothing written, nothing pushed.")
        return

    # stage traces/ but never the private folder or the raw sheets
    run(["git", "add", "traces/", "--", ":!traces/_private", ":!traces/sheets"])
    st = run(["git", "status", "--porcelain"]).stdout.strip()
    if not st:
        print("Nothing changed - already up to date.")
        return
    print("\nstaged:\n" + st)

    msg = "Update sketches: %d new trace%s" % (len(total_new),
                                               "" if len(total_new) == 1 else "s")
    c = run(["git", "commit", "-q", "-m", msg])
    if c.returncode:
        print(c.stdout + c.stderr)
        return
    print("committed: " + msg)

    if NO_PUSH:
        print("--no-push: stopping before push.")
        return
    p = run(["git", "push", "-q", "origin", "main"])
    if p.returncode:
        print("push failed:\n" + p.stdout + p.stderr)
        return
    print("pushed. Live in about a minute at "
          "https://bwoodmanw.github.io/playbox/")


if __name__ == "__main__":
    main()
