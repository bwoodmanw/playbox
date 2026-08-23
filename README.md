# Playbox

A single-file creative playground for kids: paint, animation, stickers and music.
Built to run in the Amazon Fire tablet's Silk browser under Amazon Kids.

Everything lives in `index.html` — ~128 KB, no build step, no npm, no CDN,
no analytics, and exactly **one network request to start** (the page itself).
That is what makes it work behind a locked-down kids browser. The only
additional requests happen if you put files in `traces/` — those load lazily,
when the trace picker is first opened, never at page load.

---

## What's in it

### 🎨 Paint
- **13 brush textures** — brush, crayon, chalk, marker, pencil, watercolour,
  neon glow, rainbow, sparkle, spray, plus eraser and paint-bucket fill.
- **7 shape tools** — line, box, circle, triangle, star, heart, arrow, each
  switchable between filled and outline, with a live preview while dragging.
- **26 colouring pages in 4 categories**, all drawn in code so they stay sharp
  at any size and cost nothing to download:
  - *Easy* — fish, butterfly, flower, house, rocket, car, cat, ice cream,
    robot, tree, stars, balloons
  - *Anime* — anime girl, anime boy, chibi, manga eyes
  - *Cool* — skateboard, guitar, sneaker, headphones, dragon, sports car, skull
  - *Patterns* — mandala, rose, galaxy
- **4 paper types** — plain, grid, lined, dots.
- **Colour mixer** (Big and Teen) — hue/brightness/lightness sliders; the last
  six custom colours stay in the palette.

### 🌍 Scenes
16 full-bleed environments sit on a **separate background layer** beneath the
art, in Paint, Animate and Stickers:

- *Nature* — meadow, forest, mountains, beach, under the sea, desert, snowy
  day, jungle
- *Sky & space* — sunset, night sky, outer space, rainbow sky
- *Places* — city, bedroom, on stage

Because the scene is its own layer, swapping it never disturbs the drawing on
top, and the eraser cuts through to reveal it.

### 🎬 Animate
Draw frame by frame and play it back as a cartoon.
- Up to 24 frames, with add / duplicate / delete.
- **Onion skinning** — the previous frame shows faintly underneath so the kid
  can line up the next one.
- Playback at 2, 5, 10 or 15 frames per second.
- Saved cartoons replay in My Stuff and can be loaded back in to keep working.
- Uses the same 13 brushes and colours as Paint.

### 🦄 Stickers
Tap emoji into a scene, drag to move, grow/shrink/spin/remove, swap the
background, save the whole thing as a picture.

### 🎵 Music
- **22 sounds in three categories** — 8 instruments (bells, toy piano, robot,
  marimba, flute, bass, organ, music box), 6 drums (kick, snare, hat, tom,
  clap, cowbell), and 8 fun sounds (boing, zap, pop, whoosh, laser, magic,
  siren, drip). All synthesised with the Web Audio API — zero bytes of audio
  files.
- Instrument pads are tuned to a **pentatonic scale**, so nothing a child
  plays sounds wrong.
- **16-step, 6-track sequencer** (Big and Teen). Every track can be pointed at any
  of the 22 sounds.
- **4 preset songs** — Rock beat, Twinkle, Robot dance, Silly — plus room to
  save 6 of your own.
- Tempo control from 50 to 200 bpm.

### 📁 Adding your own traces

Two ways, depending on where the picture is.

**On the tablet already?** Use **📷 Import** in Paint. Drag a box round the
part you want (so a sheet of several drawings can be cut up one at a time),
then pick *Trace it now*, *Keep the picture*, or *Add to My Traces* to keep it
in a personal library. Stored on that device, 24 slots.

**On a computer?** Drop the files into `traces/` and run:

```bash
python tools/update_sketches.py
```

That cuts any grid sheet into individual traces, rebuilds the manifest,
commits and pushes in one go. They appear under **Traces → 📁 Added** on every
device that opens the site — nothing has to be copied onto the tablet at all.

Folders:

| | |
|---|---|
| `traces/` | the individual traces the app serves |
| `traces/sheets/` | grids waiting to be cut up (not published) |
| `traces/_private/` | never scanned, never published |

The sheet's filename sets the labels: `torso.png` gives `torso-01.png` …
which the app lists as "Torso 01". See `traces/README.md`.

Either way, Playbox drops the white background out so the scene behind still
shows through.

Only add art you have the rights to. Characters from anime, cartoons, games
and films belong to their studios, and that does not change if an AI generated
the drawing — an AI picture of a known character is still a picture of someone
else's character. This site is public.

### 🖼️ My Stuff
Everything saved, as thumbnails, with **filter and sort**: show everything,
paintings, cartoons or stickers (each with a live count), ordered by newest,
oldest or type. Each item carries a date badge. Paintings and sticker scenes
open large; cartoons play back and can be reopened for more editing. Deleting
is behind a grown-up gate. Holds 48 items.

## Age modes

The **Little / Big / Teen** button in the top bar reshapes the whole app:

| | Little (3–6) | Big (7–12) | Teen (13+) |
|---|---|---|---|
| Brushes | 7 | 13 | 13 |
| Colours | 8 | 18 + mixer | 18 bolder + mixer |
| Brush sizes | 3 | 4 | 4 |
| Music pads | 6 | 8 | 8 |
| Sequencer | hidden | 16 × 6 | 16 × 6 |
| Stickers | 12 | 30 | 24 (older set) |
| Pages open on | Easy | Easy | Anime |
| Buttons | larger, wider rail | standard | standard |

Every category of colouring page is reachable in all three modes — the age
only changes which one opens first. The choice is remembered between visits.

## Grown-up gate

Deleting saved work asks a small multiplication question first. It keeps a
four-year-old from wiping the gallery. It is **not** a security boundary — an
older kid will solve it.

## Where things are saved — and how to not lose it

There is **no account and no sync**. Everything lives in `localStorage`, keyed
to this site, **on one device, in one browser, under one child profile**. It
survives closing the app and rebooting the tablet. It does *not* survive
clearing browsing data, a factory reset, a different profile, or a second
tablet.

**Unfinished work is kept too.** The painting on the canvas, the cartoon
frames and the sticker scene are snapshotted to storage about a second after
each change - and immediately when you switch screens or the tab goes into the
background. Reopen Playbox and they come back where you left them, no Save
needed. Save is still what puts a finished piece into My Stuff.

Playbox asks the browser for **persistent storage** at start-up so the work is
not evicted when space runs low, and My Stuff shows how much room is left and
whether that request was granted. Use **💾 Back up** there now and then — it
writes everything (art, cartoons, songs, My Traces, settings) to one file, and
**📂 Restore** reads it back. Restore is reachable even when nothing is saved.

The backup *download* may be blocked inside Amazon Kids; if so, do it from the
grown-up profile.

Nothing is uploaded anywhere. Pictures are downscaled to 640 px and stored as JPEG
(~7 KB each); cartoon frames go to 320 px (~2.5 KB each). Capped at 48 saved
items so the browser's storage quota is never hit — saving past that drops the
oldest. Clearing the browser's data erases saved work.

---

## Getting it onto the Fire tablet

The tablet needs a real `https://` address, so the file has to be hosted.

### Option A — GitHub Pages

If `gh` is installed and signed in, this is one command:

```bash
gh repo create playbox --public --source=. --push && gh api -X POST repos/:owner/playbox/pages -f "source[branch]=main" -f "source[path]=/"
```

Otherwise, by hand: create a public repo, upload `index.html`, then
**Settings → Pages → Source: `main` / root → Save**. Live at
`https://<username>.github.io/playbox/` after a minute.

### Option B — Netlify Drop

Go to <https://app.netlify.com/drop> and drag the `Playbox` folder onto the
page. You get an `https://….netlify.app` URL in about twenty seconds.

---

## Allowlisting it in Amazon Kids

Amazon Kids blocks the browser by default, and when it is on, only approved
sites load. From a computer or phone:

1. Go to <https://parents.amazon.com> and sign in with the Amazon account that
   owns the tablet.
2. Pick the child's profile.
3. Find the web/browser settings for that profile and turn the browser on.
4. Add your Playbox URL to the list of allowed sites.
5. On the tablet: child's profile → web browser → Playbox.

The exact wording moves around between Fire OS versions, so if you don't see
"Add website", look under the child's profile for anything named Web, Browser,
or Add Content.

**To skip Amazon Kids entirely:** open the URL in Silk from the adult profile
and use **Add to Home screen** from the Silk menu. Playbox then opens from the
home screen like an app.

---

## Using it with no wifi

Playbox installs a service worker (`sw.js`) the first time it opens. After
that it loads from the tablet rather than the network, so it works on a plane,
in a car, or anywhere the wifi has given up.

**Nobody has to do anything.** About four seconds after the app opens, it
quietly downloads all 181 trace pictures in the background - roughly 2 MB, or
2.5 MB once the app itself is counted. From then on everything works offline.

Menu → **📶 Use without wifi** shows what has been saved and how much room it
is taking. There is a button there to fetch the pictures immediately rather
than waiting, and one to remove them again.

### The address must end in a slash

Use this, with the final `/`:

    https://bwoodmanw.github.io/playbox/

Without it, GitHub Pages answers `https://bwoodmanw.github.io/playbox` with a
301 redirect to the slashed version. That redirect needs the network, and the
unslashed address also sits *outside* the saved copy's scope, so the browser
never even asks Playbox - it just reports no connection. This is the single
most likely reason offline appears not to work.

Check the allowed-sites entry at <https://parents.amazon.com> and any bookmark
or home-screen shortcut on the tablet.

### Something is wrong - what do I check?

Menu -> **📶 Use without wifi** -> **Check**, while on wifi. It prints a tick
or a cross against each thing offline needs, plus the exact address the tablet
is on, and names the one action that follows. Photograph it if you want help
reading it.

### Will this work under Amazon Kids?

Silk is Chromium underneath and supports service workers, so it should. What
has **not** been tested on a real device is whether the Kids profile lets a
page register one, and whether the Kids browser will open an allowlisted site
at all with no connection - it may refuse before Playbox gets a say.

To find out, on the tablet:

1. Open Playbox in the child's profile and wait about ten seconds.
2. Check Menu → **📶 Use without wifi** says *Playbox itself: saved* and
   *181 of 181*.
3. Turn on aeroplane mode.
4. Close Playbox completely and open it again.

If it opens and the trace pictures are all there, it works. If the browser
refuses to open the page at all, that is Amazon Kids blocking on connectivity
and no amount of caching will get round it - in that case use **Add to Home
screen** from the adult profile instead, where it definitely works.

### If a bad copy ever gets stuck

Open the URL with `?fresh=1` on the end:

    https://bwoodmanw.github.io/playbox/?fresh=1

That throws away every cache, unregisters the worker, and hands back a clean
copy from the network. The next ordinary launch turns offline back on. Saved
drawings are untouched - they live in localStorage, not the cache.

### What this means when you change the app

Updates arrive **one launch late**. The worker serves the copy it already has
and fetches the new one in the background, so a push shows up the second time
the app is opened, not the first. That is deliberate: it is what makes the app
start instantly and work with no connection.

If a change ever must not be served stale, bump `VERSION` at the top of
`sw.js`. That throws away the cached app - but not the pictures, which live in
a separate unversioned cache precisely so a code change does not cost a 2 MB
re-download.

---

## Notes for whoever edits this next

- One file on purpose. Open `index.html` in any editor; there is no build.
- To test on a computer, double-click `index.html` — `file://` works fine.
  It will **not** work inside a chat window or file-preview pane, because
  those sandbox JavaScript; the page shows a message saying so.
- Emoji are used as all the artwork, which is why there are zero image files.
  They render with the tablet's own emoji font.
- Paint and Animate share one drawing engine, re-pointed at whichever canvas
  the current screen owns (`bindCanvas`).
- Each drawing screen is a stack of canvases: `bg` (opaque scene) → `board`
  (transparent art) → `onion` (animation ghost) → `overlay` (shape preview).
  The art layer is transparent on purpose; that is what lets scenes be swapped
  freely and what makes the eraser a `destination-out` hole rather than white
  paint. Saving calls `flatten()` to composite scene and art into one opaque
  image.
- Animation frames store **art only**. Thumbnails and saved cartoons composite
  the scene in at write time.
- Anime pages are drawn in a generic style; they deliberately do not copy any
  existing character.
- Shapes preview on a transparent overlay canvas stacked above the real one,
  so dragging a shape never damages what is underneath.
- The canvas caps at 2× device pixels so older Fire tablets keep up.
- Audio only starts after a real tap — mobile Chromium, which Silk is built
  on, refuses to make sound before a user gesture.
- Page zoom, rubber-band scroll, long-press menus and double-tap zoom are all
  suppressed, so a dragging finger draws instead of scrolling the page.
- `window.__playbox` exposes state and tables for console smoke-testing.
