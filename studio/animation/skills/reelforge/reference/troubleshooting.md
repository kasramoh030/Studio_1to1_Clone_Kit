# Troubleshooting

| symptom | cause | fix |
|---|---|---|
| `doctor`: OpenGL is "Intel UHD" or "AMD Radeon(TM) Graphics" but you have an NVIDIA GPU | Windows Optimus gives OpenGL the iGPU | The CLI re-launches with `SHIM_MCCOMPAT=0x800000001` automatically. If that fails, set NVIDIA Control Panel > Manage 3D settings > Program settings > python.exe to "High-performance NVIDIA processor". |
| `Could not create an OpenGL 3.3 context` on Linux servers | no display | Install Mesa EGL (`apt install libegl1 libgl1-mesa-dri`). The engine falls back to the EGL backend. Software rendering (llvmpipe) works but is slow. |
| macOS | OpenGL is capped at 4.1 | Supported: ReelForge targets GLSL 3.30 core. |
| `OpenBLAS error: Memory allocation still failed` | OpenBLAS allocates a buffer per thread at import | `import reelforge` sets `OPENBLAS_NUM_THREADS=1` before numpy loads. If you import numpy first, set the env var yourself. |
| Render dies midway: `ffmpeg died`, `Cannot allocate memory`, exit 139 | system out of RAM or commit (browsers are the usual culprit) | `render --chunked` renders 5 s chunks in separate processes, verifies frame counts and resumes. Close browser tabs. |
| Everything is upside down | read back without the flip | Use `eng.read()`. The final pass already flips. |
| Hues look shifted or washed out after upload | BT.601/709 mismatch or double gamma | The encoder converts and tags BT.709. Don't sRGB-encode in your shaders: colours are linear, and the encode happens once at the end. |
| Banding in dark gradients | 8-bit 4:2:0 | Keep `grain` at 0.02 or higher (the final pass dithers). |
| Ghost or double image at a cut | motion blur sampled across a hard cut | Leave the shot without a transition (the project clamps sub-frames there). For cuts inside a scene, list them in `Scene.cuts`. |
| Text runs off screen, especially in 9:16 | fixed size | `size = eng.text.fit(s, font, max_size, eng.aspect*0.86)` |
| Text hidden behind shapes | shapes are queued | Call `eng.shapes.flush(fb)` before `eng.text.put(...)`. |
| Glyph shows as `?` | character not in the atlas charset | Extend `CHARSET` in `reelforge/draw.py`, or add a font containing it. Delete `~/.cache/reelforge/atlas_*` after changing the charset. |
| Screen goes black or the driver resets while rendering a shader | a single draw took more than about 2 s (Windows TDR) | Cap loop iterations (raymarch 110 steps or fewer, reflections 48 or fewer). Preview at half resolution. |
| A frame differs between `stills` and the render | the scene keeps state or uses `random`/`time` | Make `render` a pure function of `t`. Hash indices with `h11(i)`. |
| Particles clump into a few bright dots | `fract(sin(n*big))` hash precision collapse | Use the integer `pcg` hash (see the cookbook). |
| Liquid SDF shading shows sharp creases | height profile saturates at the medial axis | Use `1 - exp(-(-d)/k)` for the height. |
| Music is out of sync after a range render | audio not offset | `render --range a b` offsets the audio automatically. For your own music, use `proj.music_file`. |
| Microsoft Store Python writes files "nowhere" | AppData virtualisation | Keep projects and outputs in a normal folder (not under AppData). |
