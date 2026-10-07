# LazyEdit Studio app icons

## Current rounded icon (2026-10-07)

The current colorful ribbon/play artwork is `lazyedit-studio-icon-v2.png`.
Its rounded, transparent counterpart is
`lazyedit-studio-icon-v2-rounded.png`, edited with the image-generation tool
to preserve the existing artwork and remove the square outer corners.
These are application icons, never publication watermarks.

Regenerate platform assets with the LazyEdit environment:

```bash
/home/lachlan/miniconda3/envs/lazyedit/bin/python scripts/studio/build_icons.py
```

- iOS: opaque full-bleed RGB AppIcon; iOS applies its own corner mask.
- Android: rounded transparent legacy launcher exports; adaptive foreground
  remains full-bleed so the launcher can apply its supported mask.
- macOS: complete 16–1024px rounded RGBA family, with a 1/16 transparent inset
  on each side for balanced Dock sizing. This also supports older Mac systems
  that display the supplied PNG silhouette directly.
- In-app/PWA and Windows: transparent rounded PNG/ICO assets.

Check alpha at the corners, small-size legibility and the signed bundle's
actual icon resources before uploading. A changed source PNG does not update
an installed native app: build and upload a new version code/build number.
The October 7 release is internal testing only; see
`references/studio/2026-10-07-rounded-icon-test-builds.md`.

Platform guidance: [Apple app icons](https://developer.apple.com/design/human-interface-guidelines/app-icons/)
and [Android adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive).

## Original concept (historical)

`lazyedit-studio-ribbon-v1.png` is the original generated app-icon artwork.
Created with the built-in image-generation tool on 2026-09-20.

Direction: the Studio's existing forest teal, a warm ivory folded ribbon,
an abstract L and a play opening. Simple silhouette, no typography, full-bleed
square for system-applied icon masks. Used by the native iOS build 3.
The existing video watermark and Android/PWA icons remain unchanged.
`scripts/studio/build_icons.py` reproducibly derives the opaque 1024px AppIcon
and 256px StudioMark from this original.

Generation prompt:

```text
Use case: logo-brand
Asset type: premium iOS/Android app icon for LazyEdit Studio, a video editing and publishing app.
Primary request: design one exceptionally clean, beautiful, distinctive app icon. Sophisticated restraint and excellent readability at tiny sizes.
Scene/backdrop: full-bleed solid deep forest teal (#102d29), matching the existing app. Square canvas with no rounded outer corners baked in.
Subject: one bold sculptural ivory ribbon mark, suggesting a gently folded editing strip and an abstract L, with a clear right-facing play-shaped opening in its negative space. The silhouette should feel calm, effortless, memorable, balanced and ownable.
Style: precisely drawn geometry with softly rounded edges, essentially flat graphic design; only a very subtle warm highlight on the fold for depth, no dramatic shadow or metallic gloss.
Composition: optically centered single symbol, occupying roughly 56 percent of width and height, plenty of quiet empty background on all sides.
Palette: deep forest teal background, warm porcelain ivory mark, one restrained muted jade fold.
Constraints: finished production icon artwork only, square 1024 by 1024 or higher. No typography, letters as text, words, labels, border, device mockup, presentation sheet, separate tiles, watermark, film sprocket holes, scissors, sparkle, elaborate detail or fluorescent gradient. No outer rounded-square container: artwork fills the whole square.
```
