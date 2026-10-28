# Adding ClearVisit to Squarespace

`squarespace-code-block.html` is a self-contained interactive showcase: patient booking card + admin table, with primary-color and light/dark toggles and a live contrast readout.

## Why a Code Block snippet (and not an iframe of the full reference)

- **No JavaScript.** Toggles are CSS radio inputs + `:has()`. Squarespace only runs JavaScript in Code Blocks on Core plans and above, and hides scripts while you're logged in. This snippet works on every plan and shows correctly in the editor.
- **Scoped.** Every selector sits under `.cvx`, with a reset layer, so your template's fonts, table borders, label and paragraph styles can't leak in and nothing leaks out. Tested against a deliberately hostile host stylesheet (`tests/test_squarespace.py`, 17/17).
- **Small.** About 49KB, with only the 349 tokens it uses.

The full 10-section reference (`site/dist/clearvisit-design-system.html`) is ~250KB and sets page-level styles, so it isn't suitable for a Code Block. If you want it on your portfolio too, host that file on GitHub Pages or Netlify and link to it (or iframe it from a page with room for a tall frame).

## Steps

1. Edit the page, click an insert point, choose **Code**.
2. Set the block to **HTML**, and turn **Display Source** off.
3. Paste the whole contents of `squarespace-code-block.html`.
4. Save, then check the published page (incognito is the most faithful view).

Use a full-width section; the layout switches to one column automatically below ~700px of block width.

## Rebuild after token changes

```bash
python3 scripts/build.py && python3 scripts/build_squarespace.py
python3 tests/test_squarespace.py
```

Requires a browser with `:has()` support (all current major browsers). In older browsers the demo still renders in its default state; only the toggles don't respond.
