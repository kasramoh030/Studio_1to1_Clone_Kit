# Motion principles & delivery specs

## Timing numbers that work
| thing | duration |
|---|---|
| UI pop / small element in | 0.15-0.3 s |
| Headline entrance | 0.4-0.8 s (`ease_out_expo`) |
| Exit | 60-70 % of the entrance time (`ease_in_cubic`) |
| Letter or item stagger | 30-60 ms per item |
| Minimum readable hold | 0.3 s per word, at least 1 s total |
| Crossfade or iris transition | 0.4-0.8 s, centred on the cut |
| Kinetic type, one word per beat | at 120 BPM that is 0.5 s per word, fast but readable |
| Logo sting | 3-6 s |
| Short / Reel | 7-35 s, with the hook in the first 1.5 s |

## The 12 principles, translated to code
- **Squash & stretch:** `sx = 1/sq**0.5`, `sy = sq` on impact, and stretch along the velocity.
- **Anticipation:** a small reverse move (5-10 %) before the main move.
- **Slow in/out:** never animate linearly, except mechanical or UI scroll motion.
- **Arcs:** move along curves. Add `sin(pi*u)*h` to the straight-line path.
- **Follow-through and overlap:** children sample the parent at `t - i*lag`.
- **Secondary action:** background drift, breathing scale `1 + 0.01*t`, dust or parallax. No frame is ever frozen.
- **Timing:** pick BPM first, then cut on bars and accent on beats (`uKick`).
- **Exaggeration:** `ease_out_back(x, 2.5)` pops. Use shake and flash sparingly: 1-3 per 30 s.
- **Appeal:** one palette, two fonts, generous negative space, strong contrast.

## Typography
- Headlines use `display` with tracking 0.02-0.06. Labels use `sans` or `mono` with tracking 0.2-0.5, uppercase.
- Text should be at least 0.03 of frame height for body text on mobile, and 0.06 or more for captions.
- For contrast, put light text on dark (or the reverse) with at least a 4.5:1 ratio. Use a pill or box behind captions on busy backgrounds.
- Use `T.fit()` for any variable-length string.

## Colour
- Choose a palette and stay in it. The accent colour (`a`) should cover about 10 % of the frame.
- Neon and glow come from HDR values (2-4x) plus bloom. Keep text at 1.0-1.2 so it stays crisp.
- Light-background scenes need `post=dict(bloom=0.25, threshold=2.0)`, or the bloom turns hazy.

## Platform specs
| platform | preset | notes |
|---|---|---|
| YouTube | `16:9` (1080p60) or `4k` | Keep titles 5 % inside the edges. |
| YouTube Shorts, Reels, TikTok | `9:16` 1080x1920 | Captions go in the centre band, y from -0.25 to 0.15. Avoid the bottom 20 % (UI) and the top 12 %. |
| Instagram feed | `4:5` or `1:1` | |
| X / LinkedIn | `16:9` or `1:1` | Autoplay is muted, so burn in the captions. |
| README / Slack / docs | `gif --width 640 --fps 15` | Keep it under about 8 MB so GitHub renders it inline. |

Render output is H.264 High, yuv420p, BT.709 tagged, AAC 256k, with faststart. That uploads everywhere.
