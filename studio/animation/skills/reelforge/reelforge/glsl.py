"""GLSL shared library + post-processing shaders (GLSL 3.30 core -> runs on Windows, Linux and macOS)."""

GLSL_HEADER = r"""
#version 330
uniform vec2  uRes;
uniform float uTime;
uniform vec2  uJitter;
uniform float uKick;
uniform float uSnare;
uniform float uBeat;
uniform float uGlobal;
"""

GLSL_LIB = r"""
#define PI 3.14159265359
#define TAU 6.28318530718
float sat(float x){ return clamp(x,0.0,1.0); }
vec2  FC(){ return gl_FragCoord.xy + uJitter; }
vec2  P(){ return (FC() - 0.5*uRes) / uRes.y; }          // centered, y up, height = 1
mat2  rot(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }
float hash11(float p){ p=fract(p*.1031); p*=p+33.33; p*=p+p; return fract(p); }
float hash21(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec2  hash22(vec2 p){ vec3 p3=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
vec3  hash33(vec3 p3){ p3=fract(p3*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yxz+33.33); return fract((p3.xxy+p3.yxx)*p3.zyx); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); vec2 u=f*f*(3.-2.*f);
  return mix(mix(hash21(i),hash21(i+vec2(1,0)),u.x), mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),u.x), u.y); }
float vnoise3(vec3 p){ vec3 i=floor(p), f=fract(p); vec3 u=f*f*(3.-2.*f);
  float n000=hash33(i).x, n100=hash33(i+vec3(1,0,0)).x, n010=hash33(i+vec3(0,1,0)).x, n110=hash33(i+vec3(1,1,0)).x;
  float n001=hash33(i+vec3(0,0,1)).x, n101=hash33(i+vec3(1,0,1)).x, n011=hash33(i+vec3(0,1,1)).x, n111=hash33(i+vec3(1,1,1)).x;
  return mix(mix(mix(n000,n100,u.x),mix(n010,n110,u.x),u.y), mix(mix(n001,n101,u.x),mix(n011,n111,u.x),u.y), u.z); }
float fbm(vec2 p){ float a=.5, s=0.; for(int i=0;i<5;i++){ s+=a*vnoise(p); p=rot(.5)*p*2.03+11.7; a*=.5; } return s; }
float fbm3(vec3 p){ float a=.5, s=0.; for(int i=0;i<4;i++){ s+=a*vnoise3(p); p=p*2.02+7.3; a*=.5; } return s; }
vec3  pal(float t, vec3 a, vec3 b, vec3 c, vec3 d){ return a + b*cos(TAU*(c*t+d)); }
vec3  srgb2lin(vec3 c){ return pow(c, vec3(2.2)); }
vec3  hex(int h){ return srgb2lin(vec3(float((h>>16)&255), float((h>>8)&255), float(h&255))/255.); }
float easeOutCubic(float x){ x=sat(x); return 1.-pow(1.-x,3.); }
float easeInOutCubic(float x){ x=sat(x); return x<.5 ? 4.*x*x*x : 1.-pow(-2.*x+2.,3.)/2.; }
float easeOutExpo(float x){ x=sat(x); return x>=1. ? 1. : 1.-pow(2.,-10.*x); }
float easeInOutExpo(float x){ x=sat(x); if(x<=0.) return 0.; if(x>=1.) return 1.;
  return x<.5 ? pow(2.,20.*x-10.)/2. : (2.-pow(2.,-20.*x+10.))/2.; }
float easeOutBack(float x){ x=sat(x); float c1=1.70158, c3=c1+1.; return 1.+c3*pow(x-1.,3.)+c1*pow(x-1.,2.); }
float easeOutElastic(float x){ x=sat(x); if(x<=0.) return 0.; if(x>=1.) return 1.;
  return pow(2.,-10.*x)*sin((x*10.-.75)*TAU/3.)+1.; }
float sdCircle(vec2 p, float r){ return length(p)-r; }
float sdBox(vec2 p, vec2 b){ vec2 d=abs(p)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float sdRBox(vec2 p, vec2 b, float r){ vec2 d=abs(p)-b+r; return length(max(d,0.))+min(max(d.x,d.y),0.)-r; }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=sat(dot(pa,ba)/dot(ba,ba)); return length(pa-ba*h); }
float sdRing(vec2 p, float r, float w){ return abs(length(p)-r)-w; }
float smin(float a, float b, float k){ float h=max(k-abs(a-b),0.)/k; return min(a,b)-h*h*k*.25; }
float smax(float a, float b, float k){ return -smin(-a,-b,k); }
float fill(float d){ float w=fwidth(d); return 1.-smoothstep(-w,w,d); }
float fillpx(float d, float px){ return 1.-smoothstep(-px, px, d); }
float stroke(float d, float w){ return fill(abs(d)-w); }
float glow(float d, float k){ return exp(-max(d,0.)*k); }
"""

VS_FULLSCREEN = r"""
#version 330
void main(){
  vec2 v = vec2((gl_VertexID<<1)&2, gl_VertexID&2);
  gl_Position = vec4(v*2.0-1.0, 0.0, 1.0);
}
"""

FS_BLIT = r"""
uniform sampler2D uSrc; uniform float uWeight;
out vec4 o;
void main(){ o = texelFetch(uSrc, ivec2(gl_FragCoord.xy), 0) * uWeight; }
"""

FS_DOWN = r"""
uniform sampler2D uSrc; uniform vec2 uSrcTexel; uniform vec2 uDstSize; uniform int uFirst; uniform float uThreshold;
out vec4 o;
vec3 S(vec2 uv){ return texture(uSrc, uv).rgb; }
float luma(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
vec3 karis(vec3 c){ return c/(1.+luma(c)); }
void main(){
  vec2 uv = gl_FragCoord.xy / uDstSize; vec2 t = uSrcTexel;
  vec3 a=S(uv+t*vec2(-2,2)), b=S(uv+t*vec2(0,2)), c=S(uv+t*vec2(2,2));
  vec3 d=S(uv+t*vec2(-2,0)), e=S(uv), f=S(uv+t*vec2(2,0));
  vec3 g=S(uv+t*vec2(-2,-2)), h=S(uv+t*vec2(0,-2)), i=S(uv+t*vec2(2,-2));
  vec3 j=S(uv+t*vec2(-1,1)), k=S(uv+t*vec2(1,1)), l=S(uv+t*vec2(-1,-1)), m=S(uv+t*vec2(1,-1));
  vec3 col;
  if(uFirst==1){
    vec3 g0=(a+b+d+e)*.25, g1=(b+c+e+f)*.25, g2=(d+e+g+h)*.25, g3=(e+f+h+i)*.25, g4=(j+k+l+m)*.25;
    col = (karis(g0)+karis(g1)+karis(g2)+karis(g3))*.125 + karis(g4)*.5;
    col = col/(1.-min(luma(col),.99));
    float br = luma(col);
    col *= max(br-uThreshold, 0.)/max(br, 1e-4);
  } else {
    col = e*.125 + (a+c+g+i)*.03125 + (b+d+f+h)*.0625 + (j+k+l+m)*.125;
  }
  o = vec4(col,1);
}
"""

FS_UP = r"""
uniform sampler2D uSrc; uniform vec2 uSrcTexel; uniform vec2 uDstSize; uniform float uRadius;
out vec4 o;
void main(){
  vec2 uv = gl_FragCoord.xy / uDstSize; vec2 t = uSrcTexel*uRadius;
  vec3 c = texture(uSrc,uv).rgb*4.
    + (texture(uSrc,uv+vec2(-t.x,0)).rgb + texture(uSrc,uv+vec2(t.x,0)).rgb + texture(uSrc,uv+vec2(0,-t.y)).rgb + texture(uSrc,uv+vec2(0,t.y)).rgb)*2.
    + texture(uSrc,uv+vec2(-t.x,-t.y)).rgb + texture(uSrc,uv+vec2(t.x,-t.y)).rgb + texture(uSrc,uv+vec2(-t.x,t.y)).rgb + texture(uSrc,uv+vec2(t.x,t.y)).rgb;
  o = vec4(c/16., 1);
}
"""

FS_FINAL = r"""
uniform sampler2D uHDR; uniform sampler2D uBloom;
uniform float uBloomAmt, uExposure, uCA, uVignette, uGrain, uFrame, uFlash, uSat, uContrast, uFade;
uniform vec3 uTint;
out vec4 o;
vec3 aces(vec3 x){ // Stephen Hill fit
  const mat3 i = mat3(0.59719,0.07600,0.02840, 0.35458,0.90834,0.13383, 0.04823,0.01566,0.83777);
  const mat3 oo = mat3(1.60475,-0.10208,-0.00327, -0.53108,1.10813,-0.07276, -0.07367,-0.00605,1.07602);
  x = i*x; vec3 a = x*(x+0.0245786)-0.000090537; vec3 b = x*(0.983729*x+0.4329510)+0.238081; return clamp(oo*(a/b),0.,1.);
}
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
void main(){
  vec2 uv = gl_FragCoord.xy / uRes; uv.y = 1.0 - uv.y;           // flip so readback is top-down
  vec2 d = uv - .5;
  float r2 = dot(d,d);
  vec2 off = d * uCA * (0.4 + 2.0*r2);
  vec3 c;
  c.r = texture(uHDR, uv - off).r;
  c.g = texture(uHDR, uv).g;
  c.b = texture(uHDR, uv + off).b;
  vec3 bl;
  bl.r = texture(uBloom, uv - off*1.5).r; bl.g = texture(uBloom, uv).g; bl.b = texture(uBloom, uv + off*1.5).b;
  c += bl * uBloomAmt;
  c *= uTint * uExposure;
  c += uFlash;
  c *= mix(1.0, smoothstep(1.25, 0.2, length(d*vec2(1.0, 0.85))*1.35), uVignette);
  c = aces(c);
  float L = dot(c, vec3(.2126,.7152,.0722));
  c = mix(vec3(L), c, uSat);
  c = pow(c, vec3(1.0/2.2));                                        // display encode (once)
  c = mix(vec3(.5), c, uContrast);
  c *= uFade;
  float n = h12(gl_FragCoord.xy + fract(uFrame*.6180339)*917.) + h12(gl_FragCoord.xy*1.37 + fract(uFrame*.4142)*513.) - 1.0;
  c += n * (uGrain + 1.0/255.0);
  o = vec4(clamp(c,0.,1.), 1);
}
"""

FS_TRANSITION = r"""
uniform sampler2D uA; uniform sampler2D uB; uniform float uP; uniform int uType; uniform vec2 uDir;
out vec4 o;
void main(){
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = (gl_FragCoord.xy - .5*uRes)/uRes.y;
  float t = uP;
  vec4 a, b; float m;
  if(uType==0){                       // crossfade
    a = texture(uA,uv); b = texture(uB,uv); o = mix(a,b,smoothstep(0.,1.,t)); return;
  } else if(uType==1){                // circle iris reveal with hot rim
    float r = easeInOutExpo(t)*1.2;
    float dd = length(p) - r;
    m = 1.-smoothstep(-0.004,0.004,dd);
    a = texture(uA,uv); b = texture(uB,uv);
    o = mix(a,b,m) + vec4(vec3(3.0,2.2,1.4)*exp(-abs(dd)*140.)*(1.-t)*step(0.001,t),0.); return;
  } else if(uType==2){                // push with directional smear
    float e = easeInOutExpo(t);
    vec2 sh = uDir*e;
    vec4 acc = vec4(0);
    float blur = sin(PI*t)*0.04;
    for(int i=0;i<12;i++){
      float k = (float(i)/11. - .5)*blur;
      vec2 ua = uv + uDir*(e + k);
      vec2 ub = uv + uDir*(e + k) - uDir;
      bool inA = all(greaterThanEqual(ua,vec2(0))) && all(lessThanEqual(ua,vec2(1)));
      acc += inA ? texture(uA, ua) : texture(uB, ub);
    }
    o = acc/12.; return;
  } else if(uType==3){                // glitch slices
    float e = easeInOutCubic(t);
    float row = floor(uv.y*24.);
    float rn = hash11(row*13.1 + floor(t*20.));
    float th = rn*0.8 + 0.1;
    float sw = step(th, e*1.1 - 0.05 + 0.1*sin(row));
    vec2 o2 = vec2((rn-.5)*0.25*sin(PI*t), 0);
    a = texture(uA, uv + o2); b = texture(uB, uv - o2*.5);
    vec4 c = mix(a,b,sw);
    c.r = mix(texture(uA,uv+o2+vec2(.01,0)).r, texture(uB,uv-o2*.5+vec2(.01,0)).r, sw);
    o = c; return;
  } else if(uType==4){                // zoom punch through white
    float e = t;
    vec2 ca = (uv-.5)/(1.+e*e*3.)+.5, cb = (uv-.5)*(1.+(1.-e)*(1.-e)*1.5)+.5;
    a = texture(uA,ca); b = texture(uB,cb);
    float fl = exp(-pow((t-.5)*6.,2.))*4.;
    o = mix(a,b,smoothstep(.45,.55,t)) + vec4(vec3(fl),0); return;
  } else {                            // diagonal wipe with a coloured band
    float e = easeInOutExpo(t);
    float x = dot(p, normalize(vec2(1., .35)));
    float edge = mix(-1.3, 1.3, e);
    m = smoothstep(edge+0.002, edge-0.002, x);
    float band = smoothstep(edge+0.07, edge, x) * smoothstep(edge-0.07, edge, x)*0.;
    a = texture(uA,uv); b = texture(uB,uv);
    vec4 bandCol = vec4(hex(0xff5a1f)*2., 1);
    float bb = step(edge, x) * step(x, edge + 0.06*sin(PI*t));
    o = mix(mix(a,b,m), bandCol, bb); return;
  }
}
"""

VS_GLYPH = r"""
#version 330
uniform vec2 uRes; uniform vec2 uJitter;
in vec2 iPos; in vec2 iSize; in vec4 iUV; in float iRot; in vec4 iColor; in vec4 iStyle; in vec2 iScale;
in vec2 iAnchor;
out vec2 vUV; out vec4 vColor; out vec4 vStyle; out vec2 vLocal;
void main(){
  vec2 corner = vec2(gl_VertexID & 1, (gl_VertexID >> 1) & 1);        // 0..1
  vec2 lp = (corner - .5) * iSize;                                      // local, y up
  lp.x += lp.y * iStyle.w;                                              // skew / italic
  lp -= iAnchor; lp *= iScale; float c=cos(iRot), s=sin(iRot); lp = mat2(c,s,-s,c)*lp; lp += iAnchor;
  vec2 p = iPos + lp;
  vec2 ndc = p / vec2(.5*uRes.x/uRes.y, .5);
  ndc += uJitter * 2.0 / uRes;
  gl_Position = vec4(ndc, 0, 1);
  vUV = vec2(mix(iUV.x, iUV.z, corner.x), mix(iUV.w, iUV.y, corner.y));
  vColor = iColor; vStyle = iStyle; vLocal = corner;
}
"""

FS_GLYPH = r"""
#version 330
uniform sampler2D uAtlas;
in vec2 vUV; in vec4 vColor; in vec4 vStyle; in vec2 vLocal;
out vec4 o;
void main(){
  float d = texture(uAtlas, vUV).r;            // atlas px, + inside
  float w = max(fwidth(d), 1e-4) * 0.75;
  float a;
  if(vStyle.x > 0.0) a = smoothstep(-w, w, vStyle.x - abs(d - vStyle.x));   // outline of width x (px in atlas)
  else a = smoothstep(-w, w, d + vStyle.z);                                   // fill with dilate z
  float g = vStyle.y > 0.0 ? exp(-max(-d,0.0)/vStyle.y) * 0.6 : 0.0;
  float alpha = clamp(a + g*(1.0-a), 0.0, 1.0) * vColor.a;
  o = vec4(vColor.rgb * alpha, alpha);         // premultiplied
}
"""

VS_SHAPE = r"""
#version 330
uniform vec2 uRes; uniform vec2 uJitter;
in vec2 iPos; in vec2 iHalf; in float iRot; in vec4 iColor; in vec4 iParam;   // corner, stroke, glowK, glowAmt
out vec2 vLocal; out vec2 vHalf; out vec4 vColor; out vec4 vParam;
void main(){
  vec2 corner = vec2(gl_VertexID & 1, (gl_VertexID >> 1) & 1)*2.0-1.0;
  float margin = iParam.w > 0.0 ? 4.0/max(iParam.z,1.0) : 0.0;
  margin += iParam.y + 3.0/uRes.y;
  vec2 lp = corner * (iHalf + margin);
  float c=cos(iRot), s=sin(iRot);
  vec2 p = iPos + mat2(c,s,-s,c)*lp;
  vec2 ndc = p / vec2(.5*uRes.x/uRes.y, .5) + uJitter*2.0/uRes;
  gl_Position = vec4(ndc,0,1);
  vLocal = lp; vHalf = iHalf; vColor = iColor; vParam = iParam;
}
"""

FS_SHAPE = r"""
#version 330
in vec2 vLocal; in vec2 vHalf; in vec4 vColor; in vec4 vParam;
out vec4 o;
float sdRBox(vec2 p, vec2 b, float r){ vec2 d=abs(p)-b+r; return length(max(d,0.))+min(max(d.x,d.y),0.)-r; }
void main(){
  float r = min(vParam.x, min(vHalf.x, vHalf.y));
  float d = sdRBox(vLocal, vHalf, r);
  if(vParam.y > 0.0) d = abs(d) - vParam.y;
  float w = fwidth(d);
  float a = 1.0 - smoothstep(-w, w, d);
  float g = vParam.w > 0.0 ? exp(-max(d,0.0)*vParam.z) * vParam.w : 0.0;
  float alpha = clamp(a + g*(1.0-a), 0.0, 1.0) * vColor.a;
  o = vec4(vColor.rgb*alpha, a*vColor.a);
}
"""
