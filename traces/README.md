# Your own traces

Drop line-art pictures in this folder and they show up in Playbox under
**Traces → 📁 Added**, on every device that opens the site. Nothing has to be
copied onto the tablet — the pictures arrive with the page.

## How

1. Put `.png` or `.jpg` files in this folder. One picture per file, cropped to
   just that picture. Keep each under 2 MB.
2. Name the files after what they are — `space-cat.png` becomes "Space cat".
3. Run:

```bash
node tools/build-traces.mjs
```

4. Commit and push:

```bash
git add -A && git commit -m "Add traces" && git push
```

About a minute later they are on the tablet. Pull down to refresh the page.

## What works best

Black lines on a white background. Playbox drops the white out automatically,
so the scene behind still shows through and the child can colour inside the
lines. Photographs work too but come out messy — for those, use the **📷
Import** button inside the app, which runs proper edge detection.

## Size

Everything in here is downloaded when the child opens the Traces picker, so
keep the folder sensible. Twenty pictures at a couple of hundred KB each is
fine. Two hundred is not.

## Please only add art you have the rights to

Your own drawings, your child's drawings, public-domain art, or anything you
hold a licence for.

Pictures of characters from anime, cartoons, games or films are owned by their
studios, and that does not change if an AI generated the drawing — an AI
picture of a known character is still a picture of someone else's character.
This site is public, so anything in this folder is published to anyone with
the link. Original characters are completely fine.
