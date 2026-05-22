# Social preview image prompt (Gemini Imagen)

The image you'll generate becomes the **GitHub repository social preview** for
`timothywarner-org/claude-architect`. GitHub renders it when the repo link is
shared on Twitter/X, LinkedIn, Slack, Discord, etc.

## Hard spec (must respect)

- **Dimensions:** 1280 x 640 pixels (2:1 aspect ratio)
- **File size:** under 1 MB
- **Format:** PNG preferred, JPG acceptable
- **Crop awareness:** Twitter/X often shows the center 1200x600. Don't put load-bearing content in the outer 40px on any side.

## Paste this into Gemini

```
Create a 1280 by 640 pixel image (2:1 aspect ratio, landscape) for a
GitHub repository social media preview card. The repository is a
technical training course called "Claude Architect Foundations" by
Tim Warner, taught on O'Reilly Live Learning. It teaches developers
how to architect production-grade AI agents using Anthropic's Claude
API, the Model Context Protocol (MCP), and Claude Code.

VISUAL STYLE - production-architect / engineering blueprint aesthetic:

- Dark navy or near-black background (think #0A0F1E to #111827 range,
  not pure black). The background should suggest depth, not flat.
- Schematic / technical-drawing visual language: thin clean lines,
  geometric primitives, a sense of an architectural diagram or
  circuit blueprint laid out across the frame.
- Sparse, deliberate accent color: a single warm orange (think the
  #E07B47 to #D97757 range - warm, slightly muted, not neon, not
  pure red, not Stripe-purple, not corporate-blue). The orange is
  for accent strokes and one or two focal elements only, never
  more than 10 percent of total pixel coverage.
- Optional secondary accent: a very soft cool blue or teal (#3B82F6
  at low opacity) used for line work or grid elements that should
  recede into the background.
- Typography (if rendered in-image): a precise geometric sans-serif
  in the style of Inter, IBM Plex Sans, or JetBrains Mono. Crisp,
  high contrast against the dark background. Letters must be cleanly
  rendered without artifacts.

COMPOSITION (left-to-right reading order):

- LEFT THIRD: the title "Claude Architect Foundations" rendered in
  clean white or near-white sans-serif type, large enough to read
  easily at half size (so it survives the Twitter/X timeline
  thumbnail crop). One line if possible; two lines maximum, with
  "Claude Architect" on line 1 and "Foundations" on line 2 if
  needed. Below the title, the tagline "Production patterns for
  agents, tools, and MCP" in a smaller, lighter weight, in a muted
  white at about 70 percent opacity.
- RIGHT TWO THIRDS: an abstract technical-blueprint illustration
  suggesting an agentic system. Schematic-style elements you might
  include (pick a tasteful subset, do NOT cram all of them in):
    * thin geometric nodes connected by clean lines (suggesting
      a coordinator-subagent topology)
    * a small "loop" motif somewhere (suggesting the agentic loop)
    * a faint grid or graph paper texture behind everything at
      very low opacity, like engineering drafting paper
    * a few small annotation marks (tick marks, dots, brackets)
      that suggest "this is a precise technical diagram, not
      decorative art"
- Whatever is on the right side should feel ARCHITECTURAL and
  DELIBERATE, like a sober technical schematic. NOT cyberpunk,
  NOT glowing neon, NOT a brain or robot, NOT a head silhouette
  with circuits inside, NOT abstract swirly AI art.

CRITICAL NEGATIVE PROMPTS - what NOT to include:

- NO photorealistic humans, faces, or hands
- NO robot imagery, NO brain imagery, NO neural network "node and
  edge cloud" cliché
- NO glowing neon cyberpunk aesthetic
- NO chatbot speech bubbles
- NO fake corporate logos that resemble real companies (no fake
  Anthropic logo, no fake OpenAI logo, no fake GitHub logo)
- NO fictional code that contains AI hallucinations, if any code
  appears, keep it to two or three lines of plausible Python and
  proofread it
- NO emoji
- NO watermarks, signatures, or "stock photo" style
- NO trailing periods on the title text
- NO em dashes (use hyphens or commas)

ATMOSPHERE: serious, confident, designed for working engineers. The
viewer should think "this is a real technical course taught by
someone who ships" within one second of seeing the thumbnail. Not
"this is enterprise vendor marketing" and not "this is an AI hype
listicle." Closer to the cover of a well-designed technical book
than to a SaaS landing-page hero image.

ASPECT RATIO REMINDER: 1280 by 640 pixels exactly, 2 to 1 landscape.
The image will be cropped to roughly 1200 by 600 by Twitter and to
roughly 600 by 314 by LinkedIn. Keep all critical content (title,
key illustration elements) inside the central 1200 by 600 safe area.
```

## Iteration tips

If Gemini produces something off-target on the first attempt:

- **Too busy** → add "minimalist, lots of negative space, single
  focal element on the right side"
- **Too generic AI art** → add "engineering blueprint style, like an
  architectural drawing or circuit schematic"
- **Wrong color temperature** → specify the hex codes explicitly:
  "background #0A0F1E, accent color #D97757, no other colors"
- **Title text mangled** → ask Gemini to leave the title area blank
  and you'll composite the text in Figma / Photoshop yourself
- **Too dark** → add "high contrast, the title text should be clearly
  legible against the background"

## What Tim's repo currently has

The existing `images/cover.png` and `images/cover-original-1280.png`
are the prior cover assets. The new image is for the GitHub repo's
**Social preview** setting (Settings -> General -> Social preview),
which is a different surface from the README cover.

## How to apply the image once you have it

1. Save the candidate as `images/social-preview.png` (1280 x 640, under 1 MB)
2. Validate the spec: dimensions, file size, format
3. Upload to GitHub: Settings -> General -> Social preview -> Edit -> Upload an image
4. Test by sharing the repo URL in a tweet (you can delete the tweet after) or
   on https://www.opengraph.xyz/ to preview the rendering

## What's currently in the repo (2026-05-21)

- **`images/social-preview.png`** - the live asset, 1280 x 640, ~877 KB, derived
  from a Gemini Imagen generation followed by a Pillow resize-and-crop to spec.
  This is the file uploaded to GitHub Settings -> Social preview.
- **`images/social-preview-prompt.md`** (this file) - the prompt used to
  generate the source image, plus iteration tips for future regenerations.

To regenerate: paste the prompt above into Gemini, save the result to
`images/social1.png`, then run the resize-and-crop:

```powershell
uv run --with pillow python -c @'
from PIL import Image
src = Image.open(r"images/social1.png")
scale = 640 / src.size[1]
intermediate_w = round(src.size[0] * scale)
resized = src.resize((intermediate_w, 640), Image.Resampling.LANCZOS)
extra = intermediate_w - 1280
cropped = resized.crop((extra // 2, 0, intermediate_w - (extra - extra // 2), 640))
cropped.save(r"images/social-preview.png", format="PNG", optimize=True)
'@
```

Then delete `images/social1.png` (the unprocessed source is too large to commit;
it's superseded by the spec-compliant `social-preview.png`).
