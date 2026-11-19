---
name: langchain-content-studio
description: LangChain "Content Studio" design-agent — 36 production skills (HyperFrames family, motion-direction, motion-graphics, storyboard, thumbnails, data-viz, embedded-captions, faceless-explainer, film-breakdown, sound, visual-verify, slideshow, launch-film, media-use, brand-design) installed from langchain-ai/design-agent.
---

# LangChain Content Studio (36 Skills)

منبع: `https://github.com/langchain-ai/design-agent` — همان ایجنتی که در LangChain بیش از ۳۰۰۰ دارایی و ۴.۵ میلیون ویو تولید کرده است.

## مهارت‌های کلیدی و کاربردشان در استودیوی ما
| مهارت | چه چیزی می‌دهد |
|---|---|
| `hyperframes` + `hyperframes-core` + `hyperframes-cli` | معماری رسمی ساخت ویدیو با HTML/CSS/JS (همان پایپ‌لاین ما) |
| `hyperframes-animation` + `hyperframes-keyframes` | قواعد فنر، easing، کروئوگرافی کلیدفریم |
| `hyperframes-creative` | پریست‌های فریم (broadside, editorial-forest, biennale-yellow) + گزارش کنتراست |
| `hyperframes-audio` + `sound` + `music-to-video` | طراحی صدا، صدای محیط، همگام‌سازی موسیقی با برش |
| `motion-direction` + `motion-graphics` | زبان موشن، تصمیم‌های کارگردانی، گرافیک حرکتی داده‌محور |
| `storyboard` + `content-brief` + `film-breakdown` | استوری‌بورد، بریف، شکستن فیلم مرجع به پلان/پالت/آهنگ برش |
| `thumbnails` + `stills` + `image-ops` | تامبنیل، استیل و عملیات تصویر |
| `data-viz` | نمودار داده با استاندارد تحریریه |
| `embedded-captions` | زیرنویس سوخته با تایمینگ کلمه |
| `faceless-explainer` + `launch-film` + `slideshow` + `general-video` | فرمت‌های کامل ویدیو |
| `visual-verify` + `design-wiki` | بازرسی چشمی خروجی و حافظه‌ی طراحی برند |
| `media-use` | کار با مدیا (BGM/SFX/متادیتا) — **مسیرهای TTS حذف شده‌اند** |
| `brand-design` + `paper-design` + `reference-study` + `pr-to-video` + `remotion-to-hyperframes` | برند، کاغذ، مطالعه مرجع، تبدیل محتوا به ویدیو |

`_doctrine/` شامل `instructions.md`, `AGENTS.md`, `CLAUDE.md`, `llms.txt` اصلی است.

> **قانون صدا:** هیچ‌یک از مسیرهای TTS این پکیج در استودیو مجاز نیست؛ فقط Arena `voice-05` + `tools/vocal_fx_chain.py`.
