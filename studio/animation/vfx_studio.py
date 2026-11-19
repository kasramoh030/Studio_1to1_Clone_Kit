"""
vfx_studio.py — Unified GPU Special Effects & Shader Bridge for «چی میشه؟» Studio
==================================================================================
Connects all persisted VFX repositories under /home/user/animation-studio/:
  1. gl-transitions (265 OpenGL GLSL video transitions: BurnThrough, CameraShake,
     BloomDissolve, BokehDissolve, GlitchMemories, CrossZoom, DirectionalWarp, etc.)
  2. LYGIA Shader Library (378 GLSL modules with automatic #include resolution:
     filter/bloom, filter/chromaticAberration, filter/radialBlur, generative/fbm,
     generative/curl, color/tonemap/aces, distort/barrel, etc.)
  3. ModernGL Headless OpenGL 3.3 Renderer (top-row-first FBO ready for FFmpeg)
  4. Movis & ReelForge Python compositing & GPU helpers
"""

import os
import re
import glob
import numpy as np
import moderngl

STUDIO_ROOT = "/home/user/animation-studio"
GL_TRANS_DIR = os.path.join(STUDIO_ROOT, "vfx-repos", "gl-transitions")
LYGIA_DIR    = os.path.join(STUDIO_ROOT, "vfx-repos", "lygia")
SKILLS_DIR   = os.path.join(STUDIO_ROOT, "skills")


def list_gl_transitions():
    """Return sorted list of all 265+ installed GLSL transition names."""
    files = glob.glob(os.path.join(GL_TRANS_DIR, "*.glsl"))
    return sorted(os.path.splitext(os.path.basename(f))[0] for f in files)


def list_lygia_modules():
    """Return relative paths of all 378+ installed LYGIA GLSL shader modules."""
    out = []
    for root, _, files in os.walk(LYGIA_DIR):
        for fn in files:
            if fn.endswith(".glsl"):
                rel = os.path.relpath(os.path.join(root, fn), os.path.join(STUDIO_ROOT, "vfx-repos"))
                out.append(rel)
    return sorted(out)


def resolve_lygia_includes(glsl_source: str, _visited=None) -> str:
    """Recursively resolve #include \"lygia/...\" directives against local vfx-repos/lygia."""
    if _visited is None:
        _visited = set()

    inc_re = re.compile(r'^\s*#include\s+"([^"]+)"\s*$', re.MULTILINE)

    def _repl(match):
        rel_path = match.group(1)
        if rel_path.startswith("lygia/"):
            full_path = os.path.join(STUDIO_ROOT, "vfx-repos", rel_path)
        else:
            full_path = os.path.join(LYGIA_DIR, rel_path)
        full_path = os.path.normpath(full_path)
        if full_path in _visited or not os.path.exists(full_path):
            return f"// [skipped/already-included: {rel_path}]"
        _visited.add(full_path)
        with open(full_path, "r", encoding="utf-8") as fh:
            sub_src = fh.read()
        # Resolve relative includes inside sub-file
        sub_dir = os.path.dirname(full_path)
        def _sub_repl(m2):
            p2 = m2.group(1)
            cand = os.path.join(STUDIO_ROOT, "vfx-repos", p2) if p2.startswith("lygia/") else os.path.normpath(os.path.join(sub_dir, p2))
            if cand in _visited or not os.path.exists(cand):
                return ""
            _visited.add(cand)
            with open(cand, "r", encoding="utf-8") as f2:
                return resolve_lygia_includes(f2.read(), _visited)
        return inc_re.sub(_sub_repl, sub_src)

    return inc_re.sub(_repl, glsl_source)


def _parse_gl_transition_defaults(glsl_code: str) -> dict:
    """Extract default uniform values from gl-transitions comments: uniform float strength; // = 0.4"""
    defaults = {}
    pattern = re.compile(
        r'uniform\s+(float|int|bool|vec2|vec3|vec4|ivec2)\s+(\w+)\s*;\s*//\s*=\s*([^\n]+)'
    )
    for utype, name, raw_val in pattern.findall(glsl_code):
        raw_val = raw_val.strip().rstrip(";")
        try:
            if utype == "float":
                defaults[name] = float(raw_val)
            elif utype == "int":
                defaults[name] = int(raw_val)
            elif utype == "bool":
                defaults[name] = (raw_val.lower() == "true")
            elif utype.startswith(("vec", "ivec")):
                nums = re.findall(r'[-+]?\d*\.?\d+', raw_val)
                cast = int if utype.startswith("ivec") else float
                dim = int(utype[-1])
                vals = [cast(x) for x in nums]
                if len(vals) == 1:
                    vals = vals * dim
                defaults[name] = tuple(vals[:dim])
        except Exception:
            pass
    return defaults


class GPUVFXEngine:
    """Headless ModernGL (EGL) engine with 265 GLSL transitions & LYGIA post-FX."""

    VERT_SRC = """
    #version 330
    in vec2 in_pos;
    out vec2 uv;
    void main() {
        uv = vec2(in_pos.x * 0.5 + 0.5, in_pos.y * 0.5 + 0.5);
        gl_Position = vec4(in_pos, 0.0, 1.0);
    }
    """

    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.ctx = moderngl.create_context(standalone=True, backend="egl")
        self.quad = self.ctx.buffer(
            np.array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1], dtype="f4").tobytes()
        )
        self.fbo_tex = self.ctx.texture((width, height), 4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.fbo_tex])
        self._trans_cache = {}

    def compile_transition(self, name: str):
        """Compile any of the 265 gl-transitions shaders for OpenGL 3.3 Core."""
        if name in self._trans_cache:
            return self._trans_cache[name]

        path = os.path.join(GL_TRANS_DIR, f"{name}.glsl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Transition '{name}' not found in {GL_TRANS_DIR}")

        with open(path, "r", encoding="utf-8") as f:
            body = f.read()

        defaults = _parse_gl_transition_defaults(body)
        # Replace legacy texture2D calls if any exist in older community transitions
        body_330 = re.sub(r'\btexture2D\s*\(', 'texture(', body)

        frag_src = f"""
        #version 330
        precision highp float;
        uniform sampler2D u_from;
        uniform sampler2D u_to;
        uniform float progress;
        uniform float ratio;
        in vec2 uv;
        out vec4 fragColor;

        vec4 getFromColor(vec2 p) {{ return texture(u_from, clamp(p, 0.0, 1.0)); }}
        vec4 getToColor(vec2 p)   {{ return texture(u_to,   clamp(p, 0.0, 1.0)); }}

        {body_330}

        void main() {{
            fragColor = transition(uv);
        }}
        """
        prog = self.ctx.program(vertex_shader=self.VERT_SRC, fragment_shader=frag_src)
        vao = self.ctx.simple_vertex_array(prog, self.quad, "in_pos")
        self._trans_cache[name] = (prog, vao, defaults)
        return prog, vao, defaults

    def render_transition(self, name: str, tex_from, tex_to, progress: float, **overrides) -> bytes:
        """Render a single transition frame at `progress` in [0.0, 1.0] and return RGBA bytes."""
        prog, vao, defaults = self.compile_transition(name)
        tex_from.use(location=0)
        tex_to.use(location=1)
        if "u_from" in prog:
            prog["u_from"].value = 0
        if "u_to" in prog:
            prog["u_to"].value = 1
        if "progress" in prog:
            prog["progress"].value = float(progress)
        if "ratio" in prog:
            prog["ratio"].value = float(self.width) / float(self.height)

        params = {**defaults, **overrides}
        for k, v in params.items():
            if k in prog:
                prog[k].value = v

        self.fbo.use()
        vao.render(moderngl.TRIANGLES)
        return self.fbo.read(components=4)
