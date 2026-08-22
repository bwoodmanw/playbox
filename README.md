# Playbox

A single-file creative playground for kids: paint, animation, stickers and music.
Built to run in the Amazon Fire tablet's Silk browser under Amazon Kids.

Everything lives in `index.html` — ~95 KB, no build step, no npm, no CDN,
no analytics, and exactly **one network request** (the page itself). Nothing
loads after that, which is what makes it work behind a locked-down kids browser.

---

## What's in it

### 🎨 Paint
- **13 brush textures** — brush, crayon, chalk, marker, pencil, watercolour,
  neon glow, rainbow, sparkle, spray, plus eraser and paint-bucket fill.
- **7 shape tools** — line, box, circle, triangle, star, heart, arrow, each
  switchable between filled and outline, with a live preview while dragging.
- **12 colouring pages** — fish, butterfly, flower, house, rocket, car, cat,
  ice cream, robot, tree, stars, balloons. Drawn in code, so they stay sharp
  at any screen size and cost nothing to download.
- **4 paper types** — plain, grid, lined, dots.
- **Colour mixer** (Big mode) — hue/brightness/lightness sliders; the last six
  custom colours stay in the palette.

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
- **16-step, 6-track sequencer** (Big mode). Every track can be pointed at any
  of the 22 sounds.
- **4 preset songs** — Rock beat, Twinkle, Robot dance, Silly — plus room to
  save 6 of your own.
- Tempo control from 50 to 200 bpm.

### 🖼️ My Stuff
Everything saved, as thumbnails. Paintings and sticker scenes open large;
cartoons play back. Deleting is behind a grown-up gate.

## Little mode vs Big mode

The **Little / Big** button in the top bar reshapes the whole app:

| | Little (3–6) | Big (7–12) |
|---|---|---|
| Brushes | 7 | 13 |
| Colours | 8 | 18 + mixer |
| Brush sizes | 3 | 4 |
| Music pads | 6 | 8 |
| Sequencer | hidden | 16 steps × 6 tracks |
| Stickers | 12 | 30 |
| Buttons | larger, wider tool rail | standard |

The choice is remembered between visits.

## Grown-up gate

Deleting saved work asks a small multiplication question first. It keeps a
four-year-old from wiping the gallery. It is **not** a security boundary — an
older kid will solve it.

## Where things are saved

In the tablet browser's `localStorage`, on that device only. Nothing is
uploaded anywhere. Pictures are downscaled to 640 px and stored as JPEG
(~7 KB each); cartoon frames go to 320 px (~2.5 KB each). Capped at 12 saved
items so the browser's storage quota is never hit — saving a thirteenth drops
the oldest. Clearing the browser's data erases saved work.

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

## Notes for whoever edits this next

- One file on purpose. Open `index.html` in any editor; there is no build.
- To test on a computer, double-click `index.html` — `file://` works fine.
  It will **not** work inside a chat window or file-preview pane, because
  those sandbox JavaScript; the page shows a message saying so.
- Emoji are used as all the artwork, which is why there are zero image files.
  They render with the tablet's own emoji font.
- Paint and Animate share one drawing engine, re-pointed at whichever canvas
  the current screen owns (`bindCanvas`).
- Shapes preview on a transparent overlay canvas stacked above the real one,
  so dragging a shape never damages what is underneath.
- The canvas caps at 2× device pixels so older Fire tablets keep up.
- Audio only starts after a real tap — mobile Chromium, which Silk is built
  on, refuses to make sound before a user gesture.
- Page zoom, rubber-band scroll, long-press menus and double-tap zoom are all
  suppressed, so a dragging finger draws instead of scrolling the page.
- `window.__playbox` exposes state and tables for console smoke-testing.
